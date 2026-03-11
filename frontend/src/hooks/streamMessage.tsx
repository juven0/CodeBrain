import { useState } from "react";

const BASE_URL = import.meta.env.VITE_BASE_URL;

export function useStreamChat() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async (query: string) => {
    setMessage("");
    setLoading(true);

    const res = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);

      // 🔥 pipe le stream dans le state
      setMessage((prev) => prev + chunk);
    }

    setLoading(false);
  };

  return { message, loading, send };
}
