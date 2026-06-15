// 每日AI名言 - 由 Kimi 生成
const quotes = [
  { text: "The question of whether a computer can think is no more interesting than the question of whether a submarine can swim.", author: "Edsger W. Dijkstra" },
  { text: "Artificial intelligence is the new electricity.", author: "Andrew Ng" },
  { text: "I visualize a time when we will be to robots what dogs are to humans, and I'm rooting for the machines.", author: "Claude Shannon" },
  { text: "By far, the greatest danger of Artificial Intelligence is that people conclude too early that they understand it.", author: "Eliezer Yudkowsky" },
  { text: "Machine intelligence is the last invention that humanity will ever need to make.", author: "Nick Bostrom" },
  { text: "AI is likely to be either the best or worst thing to happen to humanity.", author: "Stephen Hawking" },
  { text: "Our intelligence is what makes us human, and AI is an extension of that quality.", author: "Yann LeCun" },
  { text: "Robots are not going to love us, but they also won't hate us. The real risk is indifference.", author: "Max Tegmark" },
  { text: "The real question is, when will we draft an artificial intelligence bill of rights?", author: "Gray Scott" },
  { text: "The development of full artificial intelligence could spell the end of the human race.", author: "Stephen Hawking" }
];

function dailyQuote() {
  const today = new Date();
  const seed = today.getFullYear() * 10000 + (today.getMonth() + 1) * 100 + today.getDate();
  const index = seed % quotes.length;
  return quotes[index];
}

// 自动显示到页面
function showDailyQuote() {
  const container = document.getElementById('daily-quote');
  if (!container) return;
  const q = dailyQuote();
  container.innerHTML = `
    <div style="font-style:italic; color:var(--text-muted); font-size:0.95rem; text-align:center; padding:1rem; border-left:3px solid var(--primary); background:var(--surface); border-radius:0 8px 8px 0;">
      "${q.text}"
      <div style="margin-top:0.5rem; font-size:0.85rem; color:var(--text-light);">— ${q.author}</div>
    </div>
  `;
}

// 页面加载后自动显示
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', showDailyQuote);
} else {
  showDailyQuote();
}
