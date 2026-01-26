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

  
  if (input) {
    input.addEventListener("input", function () {
      const q = this.value.toLowerCase();
      document.querySelectorAll(".phrase-item").forEach(item => {
        const text = item.dataset.text || "";
        item.style.display = text.includes(q) ? "" : "none";
      });
    });
  }

  const modal = document.getElementById("learned-modal");
  if (!modal) return;

  const closeBtn = modal.querySelector(".nivel-close");
  const confirmBtn = document.getElementById("btn-confirm-learned");

  let currentChatId = null;
  let currentCard = null;

  document.querySelectorAll(".btn-learned").forEach(btn => {
    btn.addEventListener("click", () => {
      currentChatId = btn.dataset.chatId;
      currentCard = btn.closest(".phrase-item");
      modal.style.display = "flex";
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
    currentChatId = null;
    currentCard = null;
  });

  // confirmBtn.addEventListener("click", async () => {
  //   if (!currentChatId) return;

  //   const r = await fetch("/progress/mark-learned/", {
  //     method: "POST",
  //     headers: {"Content-Type": "application/json"},
  //     body: JSON.stringify({ chat_id: currentChatId })
  //   });

  //   const j = await r.json().catch(() => ({}));
  //   if (r.ok && j.ok) {
  //     if (currentCard) currentCard.remove();
  //     modal.style.display = "none";
  //     currentChatId = null;
  //     currentCard = null;
  //   }
  // });

  confirmBtn.addEventListener("click", async () => {
  if (!currentChatId) return;

  const checked = document.querySelector(
    'input[name="learned_percent"]:checked'
  );
  if (!checked) return;

  const percent = parseInt(checked.value);

  const r = await fetch("/progress/mark-learned/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: currentChatId,
      percent: percent
    })
  });

  const j = await r.json().catch(() => ({}));
  if (r.ok && j.ok) {
    if (currentCard) currentCard.remove();
    modal.style.display = "none";
    currentChatId = null;
    currentCard = null;
  }
});



});
