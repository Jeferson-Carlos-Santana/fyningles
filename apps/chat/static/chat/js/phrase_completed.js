// document.addEventListener("DOMContentLoaded", () => {
//   const input = document.getElementById("phraseSearch");
//   if (!input) return;

//   input.addEventListener("input", function () {
//     const q = this.value.toLowerCase();
//     document.querySelectorAll(".phrase-item").forEach(item => {
//       const text = item.dataset.text || "";
//       item.style.display = text.includes(q) ? "" : "none";
//     });
//   });
// });
document.addEventListener("DOMContentLoaded", () => {
  // busca
  const input = document.getElementById("phraseSearch");
  if (input) {
    input.addEventListener("input", function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll(".phrase-item").forEach(item => {
        const text = item.dataset.text || "";
        item.style.display = text.includes(q) ? "" : "none";
      });
    });
  }

  // modal
  const modal = document.getElementById("completed-modal");
  if (!modal) return;

  const closeBtn = modal.querySelector(".nivel-close");
  const confirmBtn = document.getElementById("btn-confirm-completed");

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

  confirmBtn.addEventListener("click", async () => {
    if (!currentChatId) return;

    const checked = document.querySelector('input[name="completed_percent"]:checked');
    if (!checked) return;

    const percent = parseInt(checked.value, 10);

    const r = await fetch("/progress/mark-learned/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: currentChatId, percent })
    });

    const j = await r.json().catch(() => ({}));
    if (r.ok && j.ok) {
      window.location.reload();
    }
  });
});

