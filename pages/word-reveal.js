import Head from "next/head";
import WordRevealLab from "../components/WordRevealLab";

// Standalone tool route — does not touch the benchmark explorer (index.js).
export default function WordRevealPage() {
  return (
    <>
      <Head>
        <title>Word Reveal Lab — Sugidanon</title>
        <meta
          name="description"
          content="Apple-style word-by-word phrase reveal generator for Sugidanon demo scenes."
        />
      </Head>
      <WordRevealLab />
    </>
  );
}
