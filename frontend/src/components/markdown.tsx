import { useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dracula } from "react-syntax-highlighter/dist/cjs/styles/prism";

// ─── Bouton copier ────────────────────────────────────────────────────────────
function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={() => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      className={`border-0 bg-transparent cursor-pointer p-0 font-mono text-xs transition-colors duration-200 ${
        copied ? "text-green-400" : "text-slate-500 hover:text-slate-300"
      }`}
    >
      {copied ? "✓ Copié" : "⎘ Copier"}
    </button>
  );
}

// ─── Composants Markdown stylisés ────────────────────────────────────────────
const mdComponents: React.ComponentProps<typeof Markdown>["components"] = {
  // ── Blocs de code ─────────────────────────────────────────────────────────
  code({ node, inline, className, children, ...props }: any) {
    const match = /language-(\w+)/.exec(className || "");
    const code = String(children).replace(/\n$/, "");

    if (!inline && match) {
      return (
        <div className="rounded-xl overflow-hidden my-3 border border-[#313145]">
          <div className="flex items-center justify-between px-3.5 py-1.5 bg-[#1e1e2e] border-b border-[#313145]">
            <span className="text-[11px] font-mono text-violet-400">
              {match[1]}
            </span>
            <CopyButton code={code} />
          </div>
          <SyntaxHighlighter
            style={dracula}
            language={match[1]}
            PreTag="div"
            customStyle={{
              margin: 0,
              borderRadius: 0,
              fontSize: 12.5,
              lineHeight: 1.7,
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              padding: "14px 16px",
            }}
            {...props}
          >
            {code}
          </SyntaxHighlighter>
        </div>
      );
    }

    // Code inline
    return (
      <code
        className="bg-violet-100 text-violet-800 font-mono rounded px-1.5 py-0.5 text-[0.82em]"
        {...props}
      >
        {children}
      </code>
    );
  },

  // ── Titres ────────────────────────────────────────────────────────────────
  // Tailwind preflight reset tous les styles natifs h1-h6,
  // les classes de taille/margin/border sont donc toutes explicites.
  h1: ({ children }) => (
    <h1 className="text-xl font-bold text-neutral-900 mt-5 mb-2 pb-1.5 border-b-2 border-violet-100 text-left">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-neutral-900 mt-4 mb-1.5 pb-1 border-b border-stone-200 text-left">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-neutral-800 mt-3.5 mb-1 text-left">
      {children}
    </h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-[13px] font-semibold text-neutral-700 mt-2.5 mb-1 text-left">
      {children}
    </h4>
  ),

  // ── Paragraphe ────────────────────────────────────────────────────────────
  p: ({ children }) => (
    <p className="mb-2 leading-relaxed text-[13.5px] whitespace-pre-line text-left">
      {children}
    </p>
  ),

  // ── Listes ───────────────────────────────────────────────────────────────
  // list-disc / list-decimal + pl-5 sont obligatoires :
  // Tailwind preflight supprime list-style et padding nativement.
  ul: ({ children }) => (
    <ul className="list-disc pl-5 my-2 space-y-1 text-[13.5px] text-left">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal pl-5 my-2 space-y-1 text-[13.5px] text-left">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="leading-relaxed text-left">{children}</li>
  ),

  // ── Tableau ───────────────────────────────────────────────────────────────
  table: ({ children }) => (
    <div className="overflow-x-auto my-3 rounded-xl border border-stone-300">
      <table
        className="w-full text-[12.5px]"
        style={{ borderCollapse: "collapse" }}
      >
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-violet-50">{children}</thead>,
  th: ({ children }) => (
    <th
      className="px-3 py-2 text-left font-semibold text-violet-700 whitespace-nowrap"
      style={{ border: "1px solid #d1d5db", borderTop: "none" }}
    >
      {children}
    </th>
  ),
  tbody: ({ children }) => <tbody>{children}</tbody>,
  tr: ({ children }) => <tr>{children}</tr>,
  td: ({ children }) => (
    <td
      className="px-3 py-2 align-top leading-relaxed text-left text-neutral-700"
      style={{ border: "1px solid #e5e7eb" }}
    >
      {children}
    </td>
  ),

  // ── Blockquote ────────────────────────────────────────────────────────────
  blockquote: ({ children }) => (
    <blockquote className="border-l-[3px] border-violet-400 pl-3 my-2 text-stone-500 italic text-[13px] text-left">
      {children}
    </blockquote>
  ),

  // ── Inline ────────────────────────────────────────────────────────────────
  strong: ({ children }) => (
    <strong className="font-bold text-neutral-900">{children}</strong>
  ),
  em: ({ children }) => <em className="italic">{children}</em>,
  del: ({ children }) => (
    <del className="line-through text-stone-400">{children}</del>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      className="text-violet-500 underline hover:text-violet-700 transition-colors"
    >
      {children}
    </a>
  ),
  hr: () => <hr className="my-4 border-0 border-t border-stone-200" />,
};

// ─── Export ───────────────────────────────────────────────────────────────────
export const MarkdownRenderer = ({ children }: { children: string }) => {
  return (
    <div className="text-neutral-700 text-left" dir="ltr">
      <Markdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={mdComponents}
      >
        {children}
      </Markdown>
    </div>
  );
};
