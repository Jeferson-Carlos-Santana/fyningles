// document.addEventListener("DOMContentLoaded", function () {

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

