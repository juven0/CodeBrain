import { useState } from "react";
import { EXTRA_PROMPTS, SUGGESTED_PROMPTS } from "../constants/prompte";

export const WelcomeScreen = ({ onPromptClick }) => {
  const [showExtra, setShowExtra] = useState(false);
  const prompts = showExtra ? EXTRA_PROMPTS : SUGGESTED_PROMPTS;

  return (
    <div
      className="flex-1 px-11 pt-12 overflow-hidden"
      style={{ animation: "fadeIn 0.4s ease" }}
    >
      <h1
        className="m-0 mb-0.5 font-extrabold text-neutral-900 leading-tight"
        style={{
          fontSize: 34,
          letterSpacing: "-0.025em",
        }}
      >
        Hi there, <span className="text-violet-500">John</span>
      </h1>
      <h1
        className="m-0 mb-2 font-extrabold text-neutral-900 leading-tight"
        style={{
          fontSize: 34,
          letterSpacing: "-0.025em",
        }}
      >
        What would like to know?
      </h1>
      <p
        className="mt-0 mb-7 text-stone-400"
        style={{ fontSize: 13.5, fontFamily: "'DM Sans', sans-serif" }}
      >
        Use one of the most common prompts below or use your own to begin
      </p>

      <div className="grid grid-cols-4 gap-2.5">
        {prompts.map((p, i) => (
          <button
            key={`${showExtra}-${i}`}
            onClick={() => onPromptClick(`${p.title} ${p.desc}`)}
            className="bg-white border border-stone-200 rounded-xl text-left cursor-pointer flex flex-col justify-between transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm"
            style={{
              minHeight: 86,
              padding: "14px 13px 11px",
              animation: `fadeUp 0.3s ${i * 0.05}s both`,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = "#7c71f540";
              e.currentTarget.style.boxShadow = "0 4px 18px #7c71f510";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "";
              e.currentTarget.style.boxShadow = "";
            }}
          >
            <p
              className="m-0 leading-snug"
              style={{ fontSize: 12.5, fontFamily: "'DM Sans', sans-serif" }}
            >
              <span className="font-semibold text-neutral-800">{p.title}</span>{" "}
              <span className="text-stone-400">{p.desc}</span>
            </p>
            <span className="mt-2 text-lg block">{p.icon}</span>
          </button>
        ))}
      </div>

      <button
        onClick={() => setShowExtra((v) => !v)}
        className="mt-3 bg-transparent border-0 cursor-pointer flex items-center gap-1 text-stone-300 p-0 transition-colors duration-150 hover:text-violet-500"
        style={{ fontSize: 12.5, fontFamily: "'DM Sans', sans-serif" }}
      >
        <span
          className="text-sm inline-block transition-transform duration-300"
          style={{ transform: showExtra ? "rotate(180deg)" : "none" }}
        >
          ↻
        </span>
        Refresh Prompts
      </button>
    </div>
  );
};
