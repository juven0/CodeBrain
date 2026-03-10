import { useEffect, useRef } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { dark } from "react-syntax-highlighter/dist/esm/styles/prism";

export const ChatMessages = ({ messages, loading }) => {
  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const markdown = `Here is some JavaScript code:

~~~js
  const test = ()=>{
    ajdkj()
  }
~~~
`;

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
              className="w-7 h-7 rounded-full bg-neutral-900 flex-shrink-0 mt-0.5 flex items-center justify-center text-white"
              style={{ fontSize: 11 }}
            >
              ✦
            </div>
          )}
          <div
            className="whitespace-pre-wrap"
            style={{
              maxWidth: "66%",
              padding: "11px 15px",
              borderRadius:
                msg.role === "user"
                  ? "16px 4px 16px 16px"
                  : "4px 16px 16px 16px",
              background: "#fff",
              color: "#2a2a2a",
              border: msg.role === "user" ? "1px solid #e9e5e0" : "none",
              fontSize: 13.5,
              lineHeight: 1.65,
              fontFamily: "'DM Sans', sans-serif",
              boxShadow:
                msg.role === "user"
                  ? "0 4px 14px #7c71f530"
                  : "0 1px 6px #00000008",
            }}
          >
            <Markdown
              children={markdown}
              components={{
                code(props) {
                  const { children, className, node, ...rest } = props;
                  const match = /language-(\w+)/.exec(className || "");
                  return match ? (
                    <SyntaxHighlighter
                      {...rest}
                      PreTag="div"
                      children={String(children).replace(/\n$/, "")}
                      language={match[1]}
                      style={dark}
                    />
                  ) : (
                    <code {...rest} className={className}>
                      {children}
                    </code>
                  );
                },
              }}
            />
          </div>
        </div>
      ))}

      {loading && (
        <div
          className="flex gap-2.5 mb-4"
          style={{ animation: "fadeUp 0.25s ease" }}
        >
          <div
            className="w-7 h-7 rounded-full bg-neutral-900 flex-shrink-0 mt-0.5 flex items-center justify-center text-white"
            style={{ fontSize: 11 }}
          >
            ✦
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
    </div>
  );
};
