// document.addEventListener("DOMContentLoaded", function () {
function playWhenReady(file, tries = 30) { // GARANTE QUE O AUDIO VAI SER LIDO PELA VOZ MESMO SE AINDA NAO EXISTIR
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

  const msgs = document.querySelectorAll(".chat-message");
  const btnStart = document.getElementById("btn-start");
  const btnMic = document.getElementById("btn-mic");


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

