import { useEffect, useRef, useState } from "react";
import { MarkdownRenderer } from "../components/markdown";
import { UserrChatBox } from "../components/userChatBox";
import lama from "../assets/sheep pp.jpeg";

export const ChatMessages = ({ messages, loading }) => {
  const [content, setContent] = useState("");
  const fetchMd = () => {
    fetch("/text.md")
      .then((res) => {
        return res.text();
      })
      .then((text) => {
        setContent(text);
      });
  };

  useEffect(() => {
    fetchMd();
  });
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="flex-1 overflow-y-auto px-11 pt-7">
      {messages.map((msg, i) => (
        <div
          key={i}
          className={`flex gap-2.5 mb-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          style={{ animation: "fadeUp 0.28s ease both" }}
        >
          {msg.role === "assistant" && (
            <div
              className="w-10 h-10 rounded-full bg-neutral-900 flex-shrink-0 mt-0.5 flex items-center justify-center text-white"
              style={{ fontSize: 11 }}
            >
              <img src={lama} />
            </div>
          )}
          {msg.role === "user" && <UserrChatBox message={msg} />}
        </div>
      ))}

      {loading && (
        <div
          className="flex gap-2.5 mb-4"
          style={{ animation: "fadeUp 0.25s ease" }}
        >
          <div
            className="w-10 h-10 rounded-full bg-neutral-900 flex-shrink-0 mt-0.5 flex items-center justify-center text-white"
            style={{ fontSize: 11 }}
          >
            <img src={lama} />
          </div>
          <div
            className="bg-white border border-stone-200 flex gap-1.5 items-center px-4 py-3"
            style={{ borderRadius: "4px 16px 16px 16px" }}
          >
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-1.5 h-1.5 rounded-full bg-stone-300 inline-block"
                style={{
                  animation: `bounce 1.1s ${i * 0.18}s infinite ease-in-out`,
                }}
              />
            ))}
          </div>
        </div>
      )}
      <div ref={bottomRef} />
      <MarkdownRenderer>
        {content.replace(/(\[.*?\])/g, "!1\n")}
      </MarkdownRenderer>
    </div>
  );
};
