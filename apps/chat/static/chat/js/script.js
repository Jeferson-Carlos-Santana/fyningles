// ABRE E FECHA O MENU LATERAL
document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });















      const msgs = Array.from(document.querySelectorAll(".chat-message"));
  const btn = document.getElementById("btn-next");

  let index = 0;

  msgs.forEach(m => m.style.display = "none");

  btn.addEventListener("click", () => {

    if (index >= msgs.length) {
      btn.textContent = "✔️ Fim";
      btn.disabled = true;
      return;
    }

    const msg = msgs[index];
    const lineId = msg.dataset.id;

    msg.style.display = "block";

    fetch("/tts/line/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ line_id: lineId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.file) {
        new Audio("/media/cache/" + data.file + "?t=" + Date.now()).play();
      }
    });

    index++; // 🔑 AVANÇA SOMENTE APÓS TOCAR
  });









// FIM ABRE E FECHA O MENU LATERAL

// BUSCA LICOES NO MENU LATERAL
const searchInput = document.querySelector(".lesson-search");
const lessonItems = document.querySelectorAll(".lessons li");
searchInput.addEventListener("input", () => {
    const value = searchInput.value.toLowerCase();
    lessonItems.forEach(li => {
        const text = li.innerText.toLowerCase();
        li.style.display = text.includes(value) ? "block" : "none";
    });
});
// FIM BUSCA LICOES NO MENU LATERAL

// TEMPO DA MENSAGEM DE SUCESSO SUMIR
  setTimeout(() => {
    document.querySelectorAll(".msg-success").forEach(el => {
      el.style.display = "none";
    });
  }, 5000);

  setTimeout(() => {
    document.querySelectorAll(".msg-warning").forEach(el => {
      el.style.display = "none";
    });
  }, 5000);

  setTimeout(() => {
    document.querySelectorAll(".msg-primary").forEach(el => {
      el.style.display = "none";
    });
  }, 5000);

  setTimeout(() => {
    document.querySelectorAll(".msg-secondary").forEach(el => {
      el.style.display = "none";
    });
  }, 5000);

  setTimeout(() => {
    document.querySelectorAll(".msg-danger").forEach(el => {
      el.style.display = "none";
    });
  }, 5000);
// FIM TEMPO DA MENSAGEM DE SUCESSO SUMIR





});