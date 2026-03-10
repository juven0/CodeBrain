import { useEffect, useRef, useState } from "react";

export const InputBar = ({ onSend, prefill, setPrefill, disabled }) => {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  useEffect(() => {
    if (prefill) {
      setValue(prefill);
      setPrefill("");
      setTimeout(() => textareaRef.current?.focus(), 50);
    }
  }, [prefill]);

  const handleSend = () => {
    const t = value.trim();
    if (!t || disabled) return;
    onSend(t);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const active = !!value.trim() && !disabled;

  return (
    <div className="px-11 pt-2.5 pb-6">
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-sm">
        {/* Textarea */}
        <div className="flex gap-2 items-start px-4 pt-3 pb-2">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              e.target.style.height = "auto";
              e.target.style.height =
                Math.min(e.target.scrollHeight, 110) + "px";
            }}
            onKeyDown={handleKey}
            placeholder="Ask whatever you want…."
            rows={1}
            className="flex-1 border-0 bg-transparent resize-none focus:outline-none text-neutral-800 placeholder-stone-300"
            style={{
              fontSize: 13.5,
              fontFamily: "'DM Sans', sans-serif",
              lineHeight: 1.6,
              minHeight: 22,
              maxHeight: 110,
              caretColor: "#7c71f5",
            }}
          />
          <div className="flex items-center gap-1.5 flex-shrink-0 pt-0.5">
            <div className="flex items-center gap-1 bg-stone-100 rounded-full px-2.5 py-1 text-stone-500 cursor-pointer font-medium text-xs">
              🌐 All Web <span className="text-stone-300 ml-0.5">▾</span>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="flex items-center justify-between px-4 pt-2 pb-3 border-t border-stone-100">
          <div className="flex gap-3.5">
            {["⊕ Add Attachment", "🖼 Use Image"].map((label, i) => (
              <button
                key={i}
                className="bg-transparent border-0 cursor-pointer text-stone-300 p-0 transition-colors duration-150 hover:text-violet-500 text-xs"
                style={{ fontFamily: "'DM Sans', sans-serif" }}
              >
                {label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2.5">
            <span className="text-stone-300 font-mono text-xs">
              {value.length}/1000
            </span>
            <button
              onClick={handleSend}
              disabled={!active}
              className={`w-8 h-8 rounded-full border-0 flex items-center justify-center text-sm transition-all duration-200 ${active ? "cursor-pointer text-white" : "cursor-not-allowed text-stone-300"}`}
              style={{
                background: active ? "#7c71f5" : "#e8e4df",
                boxShadow: active ? "0 3px 10px #7c71f540" : "none",
              }}
            >
              →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
