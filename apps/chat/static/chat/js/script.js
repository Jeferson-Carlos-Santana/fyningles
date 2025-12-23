// ABRE E FECHA O MENU LATERAL
document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
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





// GARANTE QUE O AUDIO VAI SER LIDO PELA VOZ MESMO SE AINDA NAO EXISTIR
function playWhenReady(file, tries = 30) {
  const url = "/media/cache/" + file + "?t=" + Date.now();
  fetch(url, { method: "HEAD" })
    .then(r => {
      if (!r.ok) throw new Error("not ready");
      const a = new Audio(url);
      a.play().catch(() => {
        if (tries > 0) setTimeout(() => playWhenReady(file, tries - 1), 150);
      });
    })
    .catch(() => {
      if (tries > 0) setTimeout(() => playWhenReady(file, tries - 1), 150);
    });
}


// document.addEventListener("DOMContentLoaded", function () {
  // ===== SPEECH =====
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  // ===== ELEMENTOS =====
  const msgs = document.querySelectorAll(".chat-message");
  const btnStart = document.getElementById("btn-start");
  const btnMic = document.getElementById("btn-mic");

  let index = 0;

  // esconde todas
  msgs.forEach(m => m.style.display = "none");
  btnMic.disabled = true;

  // ===== MOSTRA FRASE + GERA AUDIO =====
  function mostrarSistema() {
    if (index >= msgs.length) {
      btnMic.disabled = true;
      btnStart.disabled = true;
      return;
    }

    const msg = msgs[index];
    const lineId = msg.dataset.id;

    msg.style.display = "block";

    // TTS (GERA AUDIO NO SERVER)
    fetch("/tts/line/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ line_id: lineId })
    })
    .then(r => r.json())
    .then(d => {
      if (d.file) {
        playWhenReady(d.file);
        new Audio("/media/cache/" + d.file + "?t=" + Date.now()).play();
      }
    });

    btnMic.disabled = false;
  }

  // ===== BOTÃO INICIAR =====
  btnStart.onclick = function () {
    btnStart.disabled = true;
    mostrarSistema();
  };

  // ===== BOTÃO MICROFONE =====
  btnMic.onclick = function () {
    btnMic.disabled = true;
    recognition.start();
  };

  // ===== RESPOSTA DO USUÁRIO =====
  recognition.onresult = function (e) {
    const texto = e.results[0][0].transcript;

    const user = document.createElement("div");
    user.className = "chat-message user";
    user.textContent = texto;

    msgs[index].after(user);

    index++;
    mostrarSistema();
  };

// });

