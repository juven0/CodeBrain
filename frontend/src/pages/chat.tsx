import { useState, useRef, useEffect } from "react";
import { Sidebar } from "../layout/sidebare";
import { InputBar } from "../components/input";
import { WelcomeScreen } from "../layout/welcome";
import { ChatMessages } from "../layout/chatLayout";

export default function ChatLayout() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [prefill, setPrefill] = useState("");

  const sendMessage = async (text) => {
    const next = [...messages, { role: "user", content: text }];
    setMessages(next);
    setMessages((prev) => [...prev, { role: "assistant", content: "ok" }]);
    //   setLoading(true);
    //   try {
    //     const res = await fetch("https://api.anthropic.com/v1/messages", {
    //       method: "POST",
    //       headers: { "Content-Type": "application/json" },
    //       body: JSON.stringify({
    //         model: "claude-sonnet-4-20250514",
    //         max_tokens: 1000,
    //         messages: next.map((m) => ({ role: m.role, content: m.content })),
    //       }),
    //     });
    //     const data = await res.json();
    //     const reply = data?.content?.[0]?.text || "Unexpected error.";
    //     setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    //   } catch {
    //     setMessages((prev) => [
    //       ...prev,
    //       {
    //         role: "assistant",
    //         content: "Something went wrong. Please try again.",
    //       },
    //     ]);
    //   } finally {
    //     setLoading(false);
    //   }
  };

  return (
    <div
      className="flex h-screen items-center justify-center  "
      //   style={{
      //     background: "linear-gradient(135deg, #ebe7e0 0%, #ddd8d0 100%)",
      //   }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Playfair+Display:wght@700;800&display=swap');
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }
        @keyframes fadeUp { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:none} }
        @keyframes bounce { 0%,60%,100%{transform:translateY(0)} 30%{transform:translateY(-5px)} }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-thumb { background: #ddd; border-radius: 2px; }
      `}</style>
      <Sidebar onNewChat={() => setMessages([])} />
      <div className="w-1/2 h-full relative flex overflow-hidden rounded-2xl  ">
        <div className="flex-1 flex flex-col overflow-hidden">
          {messages.length === 0 ? (
            <>
              <WelcomeScreen onPromptClick={(t) => setPrefill(t)} />
              <InputBar
                onSend={sendMessage}
                prefill={prefill}
                setPrefill={setPrefill}
                disabled={loading}
              />
            </>
          ) : (
            <>
              <ChatMessages messages={messages} loading={loading} />
              <InputBar
                onSend={sendMessage}
                prefill={prefill}
                setPrefill={setPrefill}
                disabled={loading}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
