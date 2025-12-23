// // ABRE E FECHA O MENU LATERAL
// document.addEventListener("DOMContentLoaded", () => {
//     const toggle = document.querySelector(".menu-toggle");
//     const sidebar = document.querySelector(".sidebar");

//     toggle.addEventListener("click", () => {
//         sidebar.classList.toggle("collapsed");
//     });
// });
// // FIM ABRE E FECHA O MENU LATERAL

// // BUSCA LICOES NO MENU LATERAL
// const searchInput = document.querySelector(".lesson-search");
// const lessonItems = document.querySelectorAll(".lessons li");
// searchInput.addEventListener("input", () => {
//     const value = searchInput.value.toLowerCase();
//     lessonItems.forEach(li => {
//         const text = li.innerText.toLowerCase();
//         li.style.display = text.includes(value) ? "block" : "none";
//     });
// });
// // FIM BUSCA LICOES NO MENU LATERAL

// // TEMPO DA MENSAGEM DE SUCESSO SUMIR
//   setTimeout(() => {
//     document.querySelectorAll(".msg-success").forEach(el => {
//       el.style.display = "none";
//     });
//   }, 5000);

//   setTimeout(() => {
//     document.querySelectorAll(".msg-warning").forEach(el => {
//       el.style.display = "none";
//     });
//   }, 5000);

//   setTimeout(() => {
//     document.querySelectorAll(".msg-primary").forEach(el => {
//       el.style.display = "none";
//     });
//   }, 5000);

//   setTimeout(() => {
//     document.querySelectorAll(".msg-secondary").forEach(el => {
//       el.style.display = "none";
//     });
//   }, 5000);

//   setTimeout(() => {
//     document.querySelectorAll(".msg-danger").forEach(el => {
//       el.style.display = "none";
//     });
//   }, 5000);
// // FIM TEMPO DA MENSAGEM DE SUCESSO SUMIR


document.addEventListener("DOMContentLoaded", () => {

  const msgs = document.querySelectorAll(".chat-message");
  const btn = document.getElementById("btn-next");
  const player = document.getElementById("player");

  let index = 0;

  if (!btn || !player || msgs.length === 0) {
    console.error("Elementos não encontrados");
    return;
  }

  // esconde todas no início
  msgs.forEach(m => m.style.display = "none");

  btn.addEventListener("click", () => {

    // acabou
    if (index >= msgs.length) {
      btn.textContent = "✔️ Fim";
      btn.disabled = true;
      return;
    }

    // 🔑 pega a frase atual E JÁ AVANÇA
    const msg = msgs[index];
    const lineId = msg.dataset.id;
    index++; // <<< ISSO GARANTE PRÓXIMA FRASE

    // mostra a frase correta
    msg.style.display = "block";

    // força reset do player (evita repetir o mesmo áudio)
    player.pause();
    player.src = "";
    player.load();

    // gera áudio dessa frase
    fetch("/tts/line/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ line_id: lineId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.file) {
        // cache-buster pra nunca reaproveitar áudio
        player.src = "/media/cache/" + data.file + "?t=" + Date.now();
        player.play().catch(() => {});
      }
    })
    .catch(err => console.error(err));

  });

});