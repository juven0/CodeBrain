export const Sidebar = ({ onNewChat }) => {
  const items = [
    { icon: "✦", isLogo: true },
    { icon: "+", action: onNewChat },
    { icon: "◯" },
    { icon: "⌂" },
    { icon: "☰" },
    { icon: "◷" },
  ];
  return (
    <div
      className="absolute left-0 flex h-full flex-col items-center py-3 pb-4 gap-1 border-r border-stone-200 bg-stone-100"
      style={{ width: 52 }}
    >
      {items.map((item, i) => (
        <button
          key={i}
          onClick={item.action}
          className={`w-8 h-8 rounded-lg border-0 cursor-pointer flex items-center justify-center transition-all duration-150 ${
            item.isLogo
              ? "bg-neutral-900 text-white mb-2"
              : "bg-transparent text-stone-400 hover:bg-stone-200"
          }`}
          style={{ fontSize: item.isLogo ? 13 : 17 }}
        >
          {item.icon}
        </button>
      ))}
      <div className="flex-1" />
      <div
        className="w-7 h-7 rounded-full flex items-center justify-center text-white font-bold cursor-pointer text-xs"
        style={{ background: "linear-gradient(135deg,#7c71f5,#b09cf8)" }}
      >
        J
      </div>
    </div>
  );
};
