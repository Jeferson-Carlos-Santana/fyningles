function playWhenReady(file, tries = 30) { // GARANTE QUE O AUDIO VAI SER LIDO PELA VOZ MESMO SE AINDA NAO EXISTIR
  // const url = "/media/cache/" + file + "?t=" + Date.now();
  const url = CHAT_CONFIG.mediaUrl + "cache/" + file + "?t=" + Date.now();

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


document.addEventListener("DOMContentLoaded", function () {
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
        // new Audio("/media/cache/" + d.file + "?t=" + Date.now()).play();
        new Audio(CHAT_CONFIG.mediaUrl + "cache/" + d.file + "?t=" + Date.now()).play();

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

});

