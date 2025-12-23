document.addEventListener("DOMContentLoaded", function () {


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

});

