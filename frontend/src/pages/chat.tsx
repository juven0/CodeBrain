import { useState, useRef, useEffect, useMemo } from "react";
import { Sidebar } from "../layout/sidebare";
import { InputBar } from "../components/input";
import { WelcomeScreen } from "../layout/welcome";
import { ChatMessages } from "../layout/chatLayout";
import type { chatItem } from "../types/chat";
import { UseAxios } from "../hooks/useAxios";
import { useStreamChat } from "../hooks/streamMessage";

export default function ChatLayout() {
  const [messages, setMessages] = useState<chatItem[]>([]);
  const [prefill, setPrefill] = useState("");

  const { message, loading, send } = useStreamChat();

  const sendMessage = async (text: string) => {
    setMessages((prev) => [
      ...prev,
      { role: "user", content: text },
      { role: "assistant", content: "" },
    ]);

    await send(text);
  };

  useEffect(() => {
    if (!message) return;

    setMessages((prev) => {
      const updated = [...prev];

      updated[updated.length - 1] = {
        role: "assistant",
        content: message,
      };

      return updated;
    });
  }, [message]);

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
