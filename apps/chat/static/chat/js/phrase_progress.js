document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("phraseSearch");
  if (!input) return;

  input.addEventListener("input", function () {
    const q = this.value.toLowerCase();
    document.querySelectorAll(".phrase-item").forEach(item => {
      const text = item.dataset.text || "";
      item.style.display = text.includes(q) ? "" : "none";
    });
  });

  const modal = document.getElementById("learned-modal");
  const closeBtn = modal.querySelector(".nivel-close");
  let currentChatId = null;

  document.querySelectorAll(".btn-learned").forEach(btn => {
    btn.addEventListener("click", () => {
      currentChatId = btn.dataset.chatId;
      modal.style.display = "flex";
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
    currentChatId = null;
  });

  document.getElementById("btn-confirm-learned").addEventListener("click", () => {
    // aqui depois você liga no backend
    modal.style.display = "none";
  });
});
