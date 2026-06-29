document.addEventListener("DOMContentLoaded", () => {
  renderKstTime();
  window.setInterval(renderKstTime, 30000);

  if (window.lucide) {
    window.lucide.createIcons();
  }
});

function renderKstTime() {
  const element = document.querySelector("[data-now]");
  if (!element) {
    return;
  }

  const now = new Date();
  element.dateTime = now.toISOString();
  element.textContent = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    month: "long",
    day: "numeric",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(now);
}
