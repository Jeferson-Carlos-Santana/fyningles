document.addEventListener("DOMContentLoaded", () => { // ABRE E FECHA O MENU LATERAL

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


      
     


      const audioPlayer = new Audio();
      let filaVoz = Promise.resolve();

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn("SpeechRecognition não suportado neste browser");
        return; // sai do DOMContentLoaded com segurança
      }
      // const recognition = new SpeechRecognition();
      // recognition.lang = "en-GB";
      // recognition.continuous = false;
      // recognition.interimResults = false;

      const msgs = document.querySelectorAll(".chat-message");
      const btnStart = document.getElementById("btn-start");
      const btnMic = document.getElementById("btn-mic");

      let index = 0;
      let esperandoResposta = false;
      let expectedAtual = "";
      const MAX_TENTATIVAS = 3;  
      let tocando = false; 
      let lastMsgEl = null; 
      let tentativas = 0;


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

    // AUDIO – PLAYER ÚNICO     
    function limparHTML(html) {
      return html.replace(/<[^>]+>/g, "");
    }

    // TOCA UM ÚNICO AUDIO E ESPERA
    function tocarUm(file, tries = 300, delay = 300) {
      return new Promise(resolve => {
        const baseUrl = "/media/cache/" + file; 
        const audioUrl = baseUrl + "?t=" + Date.now(); 

        function tentar(n) {
          fetch(baseUrl, { method: "HEAD", cache: "no-store" })
          .then(r => {
            if (!r.ok) throw new Error("not ready");

            // LIMPA QUALQUER AUDIO EM ANDAMENTO
            audioPlayer.pause();
            audioPlayer.currentTime = 0;
            audioPlayer.onended = null;
            audioPlayer.onerror = null;

            audioPlayer.src = audioUrl;
            audioPlayer.onended = resolve;
            audioPlayer.onerror = resolve;

            audioPlayer.play().catch(resolve);
          })
          .catch(() => {
            if (n > 0) return setTimeout(() => tentar(n - 1), delay);
            resolve();
          });
        }

        tentar(tries);
      });
    }    

    function falarComoAntigo(files) {
      filaVoz = filaVoz.then(async () => {
        for (const file of files) {
          await tocarUm(file);
        }
      }).catch(() => {});

      return filaVoz;
    }

    function expandContractionsEn(t) {
      return (t || "")
        .replace(/\bi['’]?m\b/gi, "i am")
        .replace(/\byou['’]?re\b/gi, "you are")
        .replace(/\bhe['’]?s\b/gi, "he is")
        .replace(/\bshe['’]?s\b/gi, "she is")
        .replace(/\bit['’]?s\b/gi, "it is")
        .replace(/\bwe['’]?re\b/gi, "we are")
        .replace(/\bthey['’]?re\b/gi, "they are")
        .replace(/\bcan['’]?t\b/gi, "cannot")
        .replace(/\bdon['’]?t\b/gi, "do not");
    }

    function normText(s) {
      let t = (s || "").toLowerCase().replace(/[’]/g, "'");
      t = expandContractionsEn(t);     
      t = t.replace(/[^\w\s]/g, " ");
      t = t.replace(/\s+/g, " ").trim();
      return t;
    }

    const FEEDBACK_OK = [
      "Very good!",
      "Muito bem!",
      "Excelente!", 
      "Excellent!",
      "Perfect!",
      "Perfeito!",    
      "Well done!",
      "Muito bem feito!",  
      "Great job!",
      "Ótimo trabalho!"
    ];

    const FEEDBACK_ERR = [
      "Try again.",
      "Tente novamente.",
      "Almost, try again.",
      "Quase lá, tente novamente.",
      "Not quite right.",
      "Não está bem certo.",
      "Let's try again.",
      "Vamos tentar novamente.",
      "You made a mistake, try again.",
      "Você cometeu um erro, tente novamente."
    ];   

      // ESCONDE TODAS
      msgs.forEach(m => m.style.display = "none");
      btnMic.disabled = true;
    
      // MOSTRA FRASE + FALA   
      function mostrarSistema() {
        if (tocando) return;
        if (index >= msgs.length) {
          btnMic.disabled = true;
          btnStart.disabled = true;
          return;
        }

        const msg = msgs[index];
        const lineId = msg.dataset.id;
        const auto = parseInt(msg.dataset.auto || "0");
        const end  = parseInt(msg.dataset.end  || "0");

        // APARECE AGORA
        msg.innerHTML = limparHTML(msg.innerHTML);
        msg.style.display = "block";
        lastMsgEl = msg;

        // ENQUANTO FALA NAO DEIXA MIC
        btnMic.disabled = true;   

        fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ line_id: lineId })
        })

        .then(r => r.json())
        .then(async d => {

          if (d.files && d.files.length) { 
            tocando = true;
            await new Promise(r => setTimeout(r, 500));
            await falarComoAntigo(d.files);
            tocando = false;
          }  

          // SÓ AGORA DECIDE O PRÓXIMO PASSO
          if (end === 1) {
            btnMic.disabled = true;
            btnStart.disabled = true;
            index++;
            return;
          }

          if (auto === 1) {
            index++;
            return mostrarSistema();
          }

          esperandoResposta = true;
          expectedAtual = msg.dataset.expected || "";
          tentativas = 0;
          btnMic.disabled = false;

        });
      }

      // BOTÃO INICIAR
      btnStart.onclick = function () {
        btnStart.disabled = true;
        index = 0;
        msgs.forEach(m => m.style.display = "none");      
        mostrarSistema();
      };

      // BOTÃO MICROFONE
      btnMic.onclick = function () {
        btnMic.disabled = true;
        recognition.start();
      };

      // RESPOSTA DO USUÁRIO
      // ===== escreve avaliação do professor =====
      function escreverProfessor(text, afterEl) {
        const div = document.createElement("div");
        div.className = "chat-message system";
        div.textContent = text;
        afterEl.after(div); // mantém ordem: aluno → avaliação
        return div;
      }

      // ===== RESPOSTA DO USUÁRIO =====
      recognition.onresult = async function (e) {
        const texto = e.results[0][0].transcript;

        if (!esperandoResposta) return;

        // ===== escreve ALUNO (sempre após a última mensagem) =====
        const user = document.createElement("div");
        user.className = "chat-message user";
        user.textContent = texto;

        (lastMsgEl || msgs[index]).after(user);
        lastMsgEl = user;

        const expected = expectedAtual || "";
        const expectedNorms = new Set([
        normText(expected),
        normText(expandContractionsEn(expected))
        ]);
        const ok = expectedNorms.has(normText(texto));

        // bloqueia mic enquanto avalia
        btnMic.disabled = true;

        // ===== escolhe feedback =====
        const msg = ok
        ? FEEDBACK_OK[Math.floor(Math.random() * FEEDBACK_OK.length)]
        : FEEDBACK_ERR[Math.floor(Math.random() * FEEDBACK_ERR.length)];

        // ===== escreve AVALIAÇÃO (PROFESSOR) =====
        const prof = document.createElement("div");
        prof.className = "chat-message system";
        prof.textContent = msg;

        lastMsgEl.after(prof);
        lastMsgEl = prof;

        // ===== fala AVALIAÇÃO (bloqueante) =====
        const r = await fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: msg })
        });  

        const d = await r.json(); 
        if (d.files && d.files.length) {
          tocando = true;

          await new Promise(r => setTimeout(r, 1000));
          await tocarUm(d.files[0]);

          tocando = false;
        }  

        // ===== decisão de fluxo =====
        if (ok) {
          esperandoResposta = false;
          expectedAtual = "";
          tentativas = 0;
          setTimeout(() => {
            index++;
            lastMsgEl = null;
            mostrarSistema();
          }, 600);
          return;
        }

        // errou
        tentativas++;
        if (tentativas >= MAX_TENTATIVAS) {
          esperandoResposta = false;
          expectedAtual = "";
          tentativas = 0;
          index++;
          lastMsgEl = null;
          return mostrarSistema();
        }

        // pode tentar de novo
        esperandoResposta = true;
        btnMic.disabled = false;
      };
      
    

});
