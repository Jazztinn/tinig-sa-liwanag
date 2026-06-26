import { useMemo } from "react";
import { AnimatePresence, motion } from "framer-motion";

// Apple-esque word-by-word phrase reveal.
// Each word starts slightly lower, faded out, and softly blurred, then rises
// gently into place one by one until the full phrase is formed.
//
// Reusable: drop into any scene. Drives the WordRevealLab preview, but has no
// dependency on it. `playKey` lets a parent force a replay by changing the key.
//
// Defaults match the reference motion spec:
//   initial -> opacity 0, translateY(18px), blur(6px)
//   final   -> opacity 1, translateY(0),    blur(0)
//   easing  -> cubic-bezier(0.16, 1, 0.3, 1)  (Apple "ease-out-expo"-ish)
//   duration 700ms, stagger 120ms

export const APPLE_EASE = [0.16, 1, 0.3, 1];

export default function WordReveal({
  phrase = "",
  mode = "dark", // "light" | "dark"
  fontSize = 64, // px
  wordDelay = 120, // ms between each word
  duration = 700, // ms per word
  rise = 18, // px each word travels up
  blur = 6, // px starting blur
  weight = 600,
  playKey = 0,
  className = "",
  style = {},
}) {
  const words = useMemo(
    () => phrase.split(/\s+/).filter(Boolean),
    [phrase]
  );

  const fg = mode === "dark" ? "#f5f5f7" : "#1d1d1f";

  return (
    <div
      className={className}
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "center",
        gap: `0 ${Math.round(fontSize * 0.28)}px`,
        maxWidth: "85%",
        textAlign: "center",
        lineHeight: 1.15,
        color: fg,
        fontSize: `${fontSize}px`,
        fontWeight: weight,
        letterSpacing: "-0.02em",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Helvetica, Arial, sans-serif',
        ...style,
      }}
    >
      <AnimatePresence>
        {words.map((word, i) => (
          <motion.span
            key={`${playKey}-${i}-${word}`}
            initial={{ opacity: 0, y: rise, filter: `blur(${blur}px)` }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{
              duration: duration / 1000,
              delay: (i * wordDelay) / 1000,
              ease: APPLE_EASE,
            }}
            style={{ display: "inline-block", whiteSpace: "pre" }}
          >
            {word}
          </motion.span>
        ))}
      </AnimatePresence>
    </div>
  );
}
