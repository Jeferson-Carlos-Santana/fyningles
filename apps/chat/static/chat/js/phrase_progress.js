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
});
