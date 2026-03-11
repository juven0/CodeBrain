export const UserrChatBox = ({ message }: { message: string }) => {
  return (
    <div
      className="whitespace-pre-wrap "
      style={{
        maxWidth: "70%",
        padding: "8px 15px",
        borderRadius: "16px 6px 16px 16px",
        background: "#7c71f530",
        color: "#2a2a2a",
        fontSize: 12,
        lineHeight: 1.65,
        fontFamily: "'DM Sans', sans-serif",
      }}
    >
      <p className="text-start">{message.content}</p>
    </div>
  );
};
