import { execFile } from "node:child_process";
import { mkdtemp, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";

export const config = {
  api: {
    bodyParser: {
      sizeLimit: "12mb",
    },
  },
};

const execFileAsync = promisify(execFile);

const MAX_AUDIO_BYTES = Number(process.env.TRANSCRIBE_MAX_AUDIO_BYTES || 8 * 1024 * 1024);
const FFMPEG_BIN = process.env.LOCAL_FFMPEG_BIN || "ffmpeg";
const WHISPER_BIN = process.env.LOCAL_WHISPER_BIN || "whisper";
const WHISPER_MODEL = process.env.LOCAL_WHISPER_MODEL || "small";
const WHISPER_LANGUAGE = process.env.LOCAL_WHISPER_LANGUAGE || "tl";
const TRANSCRIBE_TIMEOUT_MS = Number(process.env.LOCAL_TRANSCRIBE_TIMEOUT_MS || 120000);

function extensionForMime(mimeType) {
  if (mimeType.includes("mp4")) return "m4a";
  if (mimeType.includes("mpeg")) return "mp3";
  if (mimeType.includes("ogg")) return "ogg";
  if (mimeType.includes("wav")) return "wav";
  return "webm";
}

function bufferFromBase64(audioBase64) {
  const value = String(audioBase64 || "").replace(/\s+/g, "");
  if (!value || !/^[A-Za-z0-9+/]+={0,2}$/.test(value)) {
    throw new Error("Recorded audio is not valid base64.");
  }
  return Buffer.from(value, "base64");
}

function parseBase64DataUrl(audio) {
  const value = String(audio || "");
  const commaIndex = value.indexOf(",");
  const meta = commaIndex >= 0 ? value.slice(5, commaIndex) : "";
  const audioBase64 = commaIndex >= 0 ? value.slice(commaIndex + 1) : "";
  const metaParts = meta.split(";").filter(Boolean);
  const mimeType = metaParts.find((part) => part.includes("/")) || "audio/webm";
  const hasBase64Flag = metaParts.some((part) => part.toLowerCase() === "base64");

  if (!value.startsWith("data:") || commaIndex < 0 || !hasBase64Flag) {
    const preview = value ? value.slice(0, 48) : "missing";
    throw new Error(
      `Expected audioBase64 or a base64 media data URL. Received audio=${preview}.`
    );
  }

  return {
    mimeType,
    audioBase64,
  };
}

function parseAudioPayload(payload) {
  const mimeType =
    typeof payload?.mimeType === "string" && payload.mimeType.trim()
      ? payload.mimeType.trim()
      : "audio/webm";

  if (typeof payload?.audioBase64 === "string" && payload.audioBase64.trim()) {
    return {
      mimeType,
      buffer: bufferFromBase64(payload.audioBase64),
    };
  }

  const audio = parseBase64DataUrl(payload?.audio);

  return {
    mimeType: payload?.mimeType ? mimeType : audio.mimeType,
    buffer: bufferFromBase64(audio.audioBase64),
  };
}

function localPrompt(reference) {
  return [
    "Hiligaynon, Tagalog, and English code-switched speech.",
    reference ? `Reference prompt: ${reference}` : "",
  ]
    .filter(Boolean)
    .join(" ");
}

function commandErrorMessage(err, label) {
  if (err?.code === "ENOENT") {
    return `${label} command not found. Install it locally or set the matching LOCAL_*_BIN env var.`;
  }

  const stderr = String(err?.stderr || "").trim();
  const stdout = String(err?.stdout || "").trim();
  const detail = stderr || stdout || err?.message || "unknown error";
  return `${label} failed: ${detail.slice(0, 700)}`;
}

async function convertToWav(inputPath, outputPath) {
  try {
    await execFileAsync(
      FFMPEG_BIN,
      [
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        inputPath,
        "-ar",
        "16000",
        "-ac",
        "1",
        outputPath,
      ],
      { timeout: 30000, maxBuffer: 1024 * 1024 }
    );
  } catch (err) {
    throw new Error(commandErrorMessage(err, "ffmpeg"));
  }
}

async function findWhisperJson(workDir, wavPath) {
  const expected = path.join(workDir, `${path.basename(wavPath, path.extname(wavPath))}.json`);
  try {
    return await readFile(expected, "utf8");
  } catch {
    const files = await readdir(workDir);
    const fallback = files.find((file) => file.endsWith(".json"));
    if (!fallback) throw new Error("Whisper did not write a JSON transcript.");
    return readFile(path.join(workDir, fallback), "utf8");
  }
}

async function transcribeWithLocalWhisper(wavPath, workDir, reference) {
  try {
    await execFileAsync(
      WHISPER_BIN,
      [
        wavPath,
        "--model",
        WHISPER_MODEL,
        "--language",
        WHISPER_LANGUAGE,
        "--task",
        "transcribe",
        "--output_format",
        "json",
        "--output_dir",
        workDir,
        "--verbose",
        "False",
        "--fp16",
        "False",
        "--initial_prompt",
        localPrompt(reference),
      ],
      { timeout: TRANSCRIBE_TIMEOUT_MS, maxBuffer: 8 * 1024 * 1024 }
    );
  } catch (err) {
    throw new Error(commandErrorMessage(err, "Local Whisper"));
  }

  const transcriptJson = await findWhisperJson(workDir, wavPath);
  const parsed = JSON.parse(transcriptJson);
  return String(parsed.text || "").trim();
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  let parsed;
  try {
    parsed = parseAudioPayload(req.body);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }

  if (!parsed.buffer.length) {
    return res.status(400).json({ error: "Recorded audio is empty." });
  }

  if (parsed.buffer.length > MAX_AUDIO_BYTES) {
    return res.status(413).json({ error: "Recorded audio is too large." });
  }

  const workDir = await mkdtemp(path.join(tmpdir(), "sugidanon-transcribe-"));
  const inputPath = path.join(workDir, `input.${extensionForMime(parsed.mimeType)}`);
  const wavPath = path.join(workDir, "recording.wav");

  try {
    await writeFile(inputPath, parsed.buffer);
    await convertToWav(inputPath, wavPath);
    const text = await transcribeWithLocalWhisper(wavPath, workDir, req.body?.reference);

    return res.status(200).json({
      text,
      backend: "local-whisper",
      model: WHISPER_MODEL,
      language: WHISPER_LANGUAGE,
    });
  } catch (err) {
    return res.status(503).json({
      error: err.message || "Local transcription failed.",
    });
  } finally {
    await rm(workDir, { recursive: true, force: true });
  }
}
