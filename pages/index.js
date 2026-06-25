import Link from "next/link";

const HF = "https://huggingface.co/datasets/LauelKills/sugidanon-hil-codeswitch";
const COLAB = "https://colab.research.google.com/github/Jazztinn/tinig-sa-liwanag/blob/main/notebooks/sugidanon_colab.ipynb";
const GITHUB = "https://github.com/Jazztinn/tinig-sa-liwanag";

// WER bars (higher = worse). Scaled against a 70% visual ceiling.
const CEIL = 70;
const breakdown = [
  { label: "Monolingual Hiligaynon", wer: 66.3, note: "pure Ilonggo words" },
  { label: "Overall", wer: 59.8, note: "whole utterance" },
  { label: "Switch-region", wer: 36.4, note: "words next to a language switch" },
];
const pairs = [
  { label: "tl ↔ en", wer: 6.2, note: "Tagalog–English: nearly solved" },
  { label: "hil ↔ tl", wer: 24.4, note: "Hiligaynon–Tagalog" },
  { label: "hil ↔ en", wer: 40.8, note: "Hiligaynon–English: worst" },
];

function werColor(wer) {
  // green (low/good) -> amber -> red (high/bad)
  if (wer < 20) return "#34d399";
  if (wer < 40) return "#fbbf24";
  return "#fb7185";
}

function Bar({ label, wer, note }) {
  return (
    <div className="bar">
      <div className="barhead">
        <span className="barlabel">{label}</span>
        <span className="barval" style={{ color: werColor(wer) }}>{wer}%</span>
      </div>
      <div className="bartrack">
        <div className="barfill" style={{
          width: `${Math.min(100, (wer / CEIL) * 100)}%`,
          background: `linear-gradient(90deg, ${werColor(wer)}aa, ${werColor(wer)})`,
        }} />
      </div>
      <span className="barnote">{note}</span>
    </div>
  );
}

function Code({ children }) {
  return <pre className="code"><code>{children}</code></pre>;
}

export default function Home() {
  return (
    <div className="page">
      <div className="bg" aria-hidden />
      <main className="wrap">
        <header className="hero glass">
          <p className="kicker">Open speech benchmark &middot; Hiligaynon (Ilonggo)</p>
          <h1>Sugidanon</h1>
          <p className="lede">
            The first openly-licensed, code-switch-labeled speech benchmark for
            Hiligaynon &mdash; a language spoken by over 9 million Filipinos, yet
            nearly invisible to modern speech technology.
          </p>
          <nav className="links">
            <a className="pill primary" href={COLAB} target="_blank" rel="noreferrer">Run the benchmark</a>
            <a className="pill" href={HF} target="_blank" rel="noreferrer">Dataset</a>
            <a className="pill" href={GITHUB} target="_blank" rel="noreferrer">Source code</a>
            <Link className="pill" href="/demo">Translation demo</Link>
          </nav>
        </header>

        <section className="glass finding">
          <span className="eyebrow">The finding</span>
          <h2 className="punch">
            Today&apos;s speech AI hears the English and Tagalog in Ilonggo speech
            &mdash; but misses the Hiligaynon itself.
          </h2>
          <p className="plain">
            When a Hiligaynon speaker mixes in an English or Tagalog word, an
            off-the-shelf model transcribes it almost perfectly. The moment they
            speak actual Hiligaynon, it fails roughly <strong>two of every three
            words</strong>. We turned that blind spot into a measurable number.
          </p>

          <div className="bars">
            <div className="barcol">
              <h3>Word error rate by region</h3>
              <p className="colsub">Higher is worse. The model does best exactly where it leans on borrowed words.</p>
              {breakdown.map((b) => <Bar key={b.label} {...b} />)}
            </div>
            <div className="barcol">
              <h3>Error rate by switch pair</h3>
              <p className="colsub">The more Hiligaynon is involved, the harder it gets.</p>
              {pairs.map((b) => <Bar key={b.label} {...b} />)}
            </div>
          </div>

          <div className="takeaway">
            <strong>Why it matters:</strong> the failure scales with how much
            Hiligaynon a sentence contains. Tagalog&ndash;English code-switching is
            nearly solved (6% error); Hiligaynon&ndash;English is the worst (41%).
            That gap is what Sugidanon measures &mdash; and it&apos;s the first open
            dataset that lets anyone measure it.
            <span className="fine">Baseline: OpenAI Whisper (small), single speaker. Preliminary.</span>
          </div>
        </section>

        <section className="glass">
          <h2>What&apos;s inside</h2>
          <div className="chips">
            <div className="chip"><strong>40</strong><span>code-switch clips (~3.1 min)</span></div>
            <div className="chip"><strong>8</strong><span>everyday domains</span></div>
            <div className="chip"><strong>4</strong><span>switch types</span></div>
            <div className="chip"><strong>per-word</strong><span>hil / tl / en tags</span></div>
          </div>
          <p className="body">
            Domains span market, transport, school/work, family, health, culture,
            everyday talk, and oral tradition. Every word is tagged by language, so
            the scorer can isolate exactly where errors happen. Transcripts were
            reviewed by a native speaker; per-word tags are seed-labeled pending a
            confirmation pass. Released under CC BY 4.0.
          </p>
        </section>

        <section className="glass">
          <h2>Use it</h2>
          <p className="body">Load the dataset in one line:</p>
          <Code>{`from datasets import load_dataset

ds = load_dataset("LauelKills/sugidanon-hil-codeswitch",
                  data_dir="data/audio", split="train")
print(ds[0]["transcript"], ds[0]["switch_type"])
print(ds[0]["tokens"])   # per-word hil/tl/en tags`}</Code>
          <p className="body">
            Reproduce the whole benchmark with no local setup:&nbsp;
            <a className="ilink" href={COLAB} target="_blank" rel="noreferrer">open the Colab</a> and
            choose Runtime &rarr; Run all. Or run it locally:
          </p>
          <Code>{`python3 scripts/run_whisper.py --model small --language tl
python3 score.py --ref data/annotations --hyp data/predictions`}</Code>
        </section>

        <section className="glass">
          <h2>Build on it</h2>
          <p className="body">Sugidanon is a building block, not a finished product. You can:</p>
          <ul className="list">
            <li>Benchmark another model (Whisper large-v3, Meta MMS) on the same clips and compare switch penalties.</li>
            <li>Grow the corpus &mdash; add speakers and clips with the included capture and clap-splitting pipeline.</li>
            <li>Confirm the per-word tags with a native speaker to harden the switch/monolingual split.</li>
            <li>Fine-tune an open multilingual model toward Hiligaynon, keeping this set as a frozen test.</li>
            <li>Extend it into a full speech-to-text, translation, and text-to-speech pipeline for Ilonggo.</li>
          </ul>
        </section>

        <section className="glass">
          <h2>Why this matters</h2>
          <p className="body">
            The Philippines has more than 130 languages. Tagalog speech
            recognition has advanced; regional tongues like Hiligaynon, Cebuano,
            and Waray still lack open datasets, benchmarks, and models. Real
            Ilonggo speech constantly mixes Hiligaynon, Tagalog, and English &mdash;
            exactly where generic systems break. Sugidanon turns that invisible
            failure into a number the next developer can build against.
          </p>
        </section>

        <footer className="foot">
          <p>
            Recorded and reviewed by <strong>Aziel Faith Agustin</strong>
            (Hiligaynon speaker). Built by Team Hague for ACM TechSprint Asteria 2026.
          </p>
          <p className="fine">
            Data: CC BY 4.0 &middot; Code: MIT &middot;{" "}
            <a className="ilink" href={HF} target="_blank" rel="noreferrer">Hugging Face</a> &middot;{" "}
            <a className="ilink" href={GITHUB} target="_blank" rel="noreferrer">GitHub</a> &middot;{" "}
            <a className="ilink" href={COLAB} target="_blank" rel="noreferrer">Colab</a>
          </p>
        </footer>
      </main>

      <style jsx>{`
        .page { position: relative; min-height: 100vh; color: #eef1f8; overflow-x: hidden; }
        .bg {
          position: fixed; inset: 0; z-index: -1;
          background:
            radial-gradient(60% 60% at 15% 10%, rgba(56,189,248,.35), transparent 60%),
            radial-gradient(55% 55% at 85% 20%, rgba(167,139,250,.32), transparent 60%),
            radial-gradient(60% 60% at 70% 95%, rgba(45,212,191,.28), transparent 60%),
            linear-gradient(160deg, #0b1020, #0a0f1d 60%, #0c1326);
        }
        .wrap { max-width: 960px; margin: 0 auto; padding: 56px 20px 72px; display: flex; flex-direction: column; gap: 20px; }

        .glass {
          background: rgba(255,255,255,.07);
          backdrop-filter: blur(22px) saturate(150%);
          -webkit-backdrop-filter: blur(22px) saturate(150%);
          border: 1px solid rgba(255,255,255,.16);
          border-radius: 24px;
          padding: 30px 34px;
          box-shadow: 0 12px 48px rgba(2,6,23,.45), inset 0 1px 0 rgba(255,255,255,.22);
        }

        .hero { text-align: left; }
        .kicker { text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; color: #9fb3d1; margin: 0 0 10px; }
        h1 { font-size: 3rem; margin: 0 0 14px; letter-spacing: -.02em;
             background: linear-gradient(90deg,#fff,#bfe3ff); -webkit-background-clip: text; background-clip: text; color: transparent; }
        .lede { font-size: 1.18rem; line-height: 1.6; color: #d6deec; margin: 0 0 22px; max-width: 64ch; }
        .links { display: flex; flex-wrap: wrap; gap: 12px; }
        .pill {
          display: inline-block; padding: 11px 18px; border-radius: 999px;
          border: 1px solid rgba(255,255,255,.22); color: #eaf0fb; text-decoration: none;
          font-weight: 600; font-size: .95rem; background: rgba(255,255,255,.06);
          backdrop-filter: blur(8px); transition: transform .15s ease, background .15s ease;
        }
        .pill:hover { transform: translateY(-1px); background: rgba(255,255,255,.14); }
        .pill.primary { border-color: transparent; color: #04121f;
          background: linear-gradient(90deg,#7dd3fc,#5eead4); box-shadow: 0 6px 22px rgba(94,234,212,.35); }

        h2 { font-size: 1.5rem; margin: 0 0 14px; letter-spacing: -.01em; }
        .eyebrow { display: inline-block; text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; color: #7dd3fc; margin-bottom: 10px; }
        .punch { font-size: 1.7rem; line-height: 1.35; margin: 0 0 14px; letter-spacing: -.01em; }
        .plain { font-size: 1.05rem; line-height: 1.65; color: #d6deec; margin: 0 0 24px; max-width: 70ch; }
        .body { font-size: 1rem; line-height: 1.65; color: #d2dbea; margin: 0 0 14px; max-width: 72ch; }

        .bars { display: grid; grid-template-columns: 1fr 1fr; gap: 26px; margin: 6px 0 22px; }
        .barcol h3 { font-size: 1rem; margin: 0 0 4px; color: #f1f5ff; }
        .colsub { font-size: .85rem; color: #98a8c4; margin: 0 0 16px; }
        .bar { margin: 0 0 14px; }
        .barhead { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 5px; }
        .barlabel { font-size: .92rem; color: #e7edf8; }
        .barval { font-size: 1rem; font-weight: 700; }
        .bartrack { height: 10px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; border: 1px solid rgba(255,255,255,.08); }
        .barfill { height: 100%; border-radius: 999px; transition: width .6s ease; }
        .barnote { display: block; font-size: .78rem; color: #8fa1bf; margin-top: 4px; }

        .takeaway { font-size: 1rem; line-height: 1.6; color: #e3e9f5; padding: 18px 20px;
          border-radius: 16px; background: rgba(125,211,252,.10); border: 1px solid rgba(125,211,252,.22); }
        .fine { display: block; margin-top: 8px; font-size: .82rem; color: #93a3c0; }

        .chips { display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 18px; }
        .chip { flex: 1 1 140px; border-radius: 16px; padding: 16px 18px;
          background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.14); }
        .chip strong { display: block; font-size: 1.5rem; color: #bfe3ff; }
        .chip span { font-size: .82rem; color: #aebbd4; }

        .list { margin: 0; padding-left: 20px; line-height: 1.7; color: #d2dbea; }
        .list li { margin: 6px 0; }

        .ilink { color: #7dd3fc; text-decoration: none; border-bottom: 1px solid rgba(125,211,252,.4); }
        .ilink:hover { border-color: #7dd3fc; }

        .code {
          background: rgba(3,8,20,.55); border: 1px solid rgba(255,255,255,.12);
          border-radius: 14px; padding: 16px 18px; overflow-x: auto;
          font-size: .85rem; line-height: 1.55; color: #d7e6ff; margin: 0 0 14px;
        }
        .code code { background: none; }

        .foot { padding: 8px 6px 0; color: #aebbd4; font-size: .95rem; line-height: 1.6; }
        .foot a { color: #7dd3fc; }
        .foot strong { color: #eaf0fb; }

        @media (max-width: 720px) {
          h1 { font-size: 2.2rem; }
          .punch { font-size: 1.35rem; }
          .bars { grid-template-columns: 1fr; gap: 18px; }
          .glass { padding: 24px 20px; }
        }
      `}</style>
    </div>
  );
}
