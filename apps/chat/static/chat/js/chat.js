const USER_NAME = document.body.dataset.username || "";

  //const USER_NAME = "{{ username|escapejs }}";

  function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]").value;
  }

  const nivelClose = document.querySelector(".nivel-close");

  if (nivelClose) {
    nivelClose.onclick = () => {
      document.getElementById("nivel-modal").style.display = "none";
    };
  }

  
  // ENVIAR MENSAGEM
  function enviarMensagem() {
    const input = document.getElementById("mensagem");
    const texto = input.value.trim();
    if (!texto) return;

    input.value = "";

    window.recognition.onresult({
      results: [[{ transcript: texto }]]
    });
  }
  
  // ATUALIZAR OS PONTOS EM TEMPO REAL
  function atualizarPontosTotais() {
    fetch("/progress/total/", { credentials: "same-origin" })
      .then(r => r.json())
      .then(data => {
        const el = document.getElementById("total-points");
        if (!el) return;
        el.textContent = Number(data.total || 0).toLocaleString("pt-BR");
      });
  }
  
  document.addEventListener("DOMContentLoaded", function () {   
     
      const audioPlayer = new Audio();
    
      let filaVoz = Promise.resolve();

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn("SpeechRecognition não suportado neste browser");
        return;
      }
      const recognition = new SpeechRecognition(); 
      window.recognition = recognition;
      recognition.lang = "en-GB";
      recognition.continuous = false;
      recognition.interimResults = false;

      const msgs = document.querySelectorAll(".chat-message");
      const btnStart = document.getElementById("btn-start");
      // const btnStop = document.getElementById("btn-stop");
      const btnMic = document.getElementById("btn-mic");
      const btnEnviar = document.getElementById("btnEnviar");
      // btnStop.disabled = true;
      let index = 0;
      let esperandoResposta = false;
      let expectedAtual = "";
      const MAX_TENTATIVAS = 3;  
      let tocando = false; 
      let lastMsgEl = null; 
      let lastFalandoEl = null;
      let tentativas = 0;    
      const chatArea = document.querySelector(".chat-area");
      let micTimeout = null;
      const btnAutoMic = document.getElementById("btnAutoMic");
      let autoMicAtivo = false;
      const btnAutoSkip = document.getElementById("btnAutoSkip");
      let autoSkipAtivo = false;

      let TEMPO_BASE = 5000;          // 3s mínimos
      let TEMPO_POR_PALAVRA = 1000;   // 0.7s por palavra
      let TEMPO_MAX = 12000;         // 12s máximo 

      const beepPlayer = new Audio("/static/chat/audio/beep.mp3");
      beepPlayer.volume = 0.9;

      const TEMPO_LIMITE_MIN = 30;
      let timerResetAula = null;
     
      let timerIntervaloVisual = null;
      let tempoRestanteSeg = 0;
      const timerEl = document.getElementById("timer-aula");

      let pontosAndamento = 0;
      const META_DO_DIA = 1000;      

      const lessonId = document.body.dataset.lessonId;

      let FLAG = 0;
      let professorLock = false;
      let execAtiva = false;

      let offlinePause = false;

      // começa desabilitado
      if (btnStart) {
        btnStart.disabled = true;
      }

      // se estiver em /chat/<id>/, habilita
      if (lessonId && lessonId !== "") {
        btnStart.disabled = false;
      }

    atualizarPontosFaltam(0);
    atualizarPontosFeitos();
    atualizarPontosTotais();    
    
    // PONTOS QUE FALTAM PARA A META DO DIA
    function atualizarPontosFaltam(pontosFeitos) {
      const el = document.getElementById("points-faltam");
      if (!el) return;

      const faltam = Math.max(META_DO_DIA - pontosFeitos, 0);
      el.textContent = faltam;    
    }
    
     // PONTOS FEITO NO DIA CORRENTE
    function atualizarPontosFeitos() {
      fetch("/progress/feitos/", { credentials: "same-origin" })
        .then(r => r.json())
        .then(data => {
          const feitos = Number(data.total || 0);

          const el = document.getElementById("points-feitos");
          if (el) el.textContent = feitos;

          atualizarPontosFaltam(feitos);
        });
    }

     // ATUALIZAR PONTOS EM ANDAMENTO
    function atualizarPontosAndamento() {
      const el = document.getElementById("points-andamento");
      if (el) el.textContent = pontosAndamento;
    }
    
    const CORRECOES_VOZ = {
        "daive": "they have",
        "dave": "they have",
        "ive": "i have",
        "youre": "you are",
        "cant": "cannot",
        "david": "they've",
        "everyday": "every day",
        "ivy": "I've",
        "hue": "He'll",
        "cole": "call",
        "gunn": "gone",
        "gunt": "gone",
        "dare": "they're",
        "81": "It won't",
        "workout": "work out",
        "seedan": "see then",
        "realized": "realised",
        "sherwood": "she would",
        "abeat": "a bit",
        "ishi": "is she",
        "taiwah": "they were",
        "Whitney": "were they",
        "alito": "a little",
        "shilco": "She'll call",
        "tay": "they",
        "iopant": "i opened",
        "ican": "i can",
        "sthey": "stay",
        "dtu": "Did you",
        "itches": "it's",
        "payen": "paying",
        "ital": "It'll",
        "leche": "Let's",
        "letis": "Let's",
        "hippies": "He pays",
        "dylan": "they learn",
        "dyland": "they learn",
        "daylan": "they learn",
        "dayland": "they learn",
        "okay": "ok",
        "sims": "seems",
        "olivia": "i leave",
        "reuse": "we use",
        "uday": "will they",
        "udai": "will they", 
        "goodnight": "good night",
        "giveaway": "give way",
        "daycare": "take care",
        "itchy": "it",
        "galway": "go away",
        "weezer": "we've",
        "norris": "no worries",
        "itihas": "it has",
        "itihaas": "it has",
        "does to": "does it",
        "hey": "he",
        "ri": "he",
        "how did yourself": "hold it yourself",
        "are you up in the door": "i open the door",
        "are you open the door": "i open the door",
        "are you ok the door": "i open the door",
        "play lenny fast": "they learn fast",
        "play learn fast": "they learn fast",
        "dei learn fast": "they learn fast",
        "today tell stories": "do they tell stories",
        "play meet today": "they meet today",
        "i'll wait to bed": "i went to bed",
        "he doesn't often cold": "he doesn't often call",
        "he doesn't off the cold": "he doesn't often call",
        "alright": "all right"
      };

    function aplicarCorrecoesVoz(texto) {
      let t = texto.toLowerCase();
      for (const errado in CORRECOES_VOZ) {
        const certo = CORRECOES_VOZ[errado];
        const re = new RegExp(`\\b${errado}\\b`, "g");
        t = t.replace(re, certo);
      }
      return t;
    }
    
    if (btnAutoSkip) {
      btnAutoSkip.onclick = function () {
        autoSkipAtivo = !autoSkipAtivo;

        if (autoSkipAtivo) {
          btnAutoSkip.classList.remove("auto-off");
          btnAutoSkip.classList.add("auto-on");
          btnAutoSkip.innerHTML = "SKIP<br>ON";
        } else {
          btnAutoSkip.classList.remove("auto-on");
          btnAutoSkip.classList.add("auto-off");
          btnAutoSkip.innerHTML = "SKIP<br>OFF";
        }
      };
    }
    
    if (btnAutoMic) {
      btnAutoMic.onclick = function () {
        autoMicAtivo = !autoMicAtivo;

        if (autoMicAtivo) {
          btnAutoMic.classList.remove("auto-off");
          btnAutoMic.classList.add("auto-on");
          btnAutoMic.innerHTML = "MIC<br>ON";
        } else {
          btnAutoMic.classList.remove("auto-on");
          btnAutoMic.classList.add("auto-off");
          btnAutoMic.innerHTML = "MIC<br>OFF";
        }
      };
    }

    function tocarBeep() {
      beepPlayer.currentTime = 0;
      beepPlayer.play().catch(() => {});
    }

    function calcularTempoMic(frase) {
      if (!frase) return TEMPO_BASE;
      const qtdPalavras = frase.trim().split(/\s+/).length;
      return Math.min(
        TEMPO_BASE + qtdPalavras * TEMPO_POR_PALAVRA,
        TEMPO_MAX
      );
    }

    function abrirMicrofoneComTempo() {
      if (FLAG !== 1) return;
      if (btnMic.disabled) return;

      // visual de gravando
      btnMic.textContent = "🎙️";
      btnMic.classList.add("mic-gravando");

      recognition.start();

      // calcula tempo com base na frase esperada atual
      const tempoMic = calcularTempoMic(expectedAtual);

      if (micTimeout) clearTimeout(micTimeout);

      micTimeout = setTimeout(() => {
        if (esperandoResposta) {
          // fecha mic
          try { recognition.stop(); } catch (e) {}
          btnMic.textContent = "🎤";
          btnMic.classList.remove("mic-gravando");

          // 🔹 DECISÃO AQUI
          if (autoSkipAtivo) {
            bloquearEntrada();

            const skip = document.createElement("div");
            skip.className = "chat-message system";
            skip.textContent = "Tempo esgotado. Avançando.";
            (lastMsgEl || msgs[index]).after(skip);

            esperandoResposta = false;
            expectedAtual = "";
            tentativas = 0;
            
            setTimeout(() => {
              FLAG = 0;
              index++;
              lastMsgEl = null;
              mostrarSistema();
            }, 150);
          }
        }
      }, tempoMic);

    }

    function encerrarMicrofone() {
      if (micTimeout) {
        clearTimeout(micTimeout);
        micTimeout = null;
      }

      try {
        recognition.stop();
      } catch (e) {}

      btnMic.textContent = "🎤";
      btnMic.classList.remove("mic-gravando");
    }

    function bloquearEntrada() {
      if(btnMic){
        btnMic.disabled = true;
      }
      if(btnEnviar){
        btnEnviar.disabled = true;
      }
      if (btnMic) {
        btnMic.textContent = "🔇";
        btnMic.classList.remove("mic-ready");
        btnMic.classList.add("mic-disabled");
      }
      if (btnEnviar) {
        btnEnviar.classList.remove("btn-ready");
        btnEnviar.classList.add("btn-disabled");
      }      
    }

    function liberarEntrada() {
      btnMic.disabled = false;
      btnEnviar.disabled = false;

      btnMic.textContent = "🎤";
      btnMic.classList.remove("mic-disabled");
      btnMic.classList.add("mic-ready");

      btnEnviar.classList.remove("btn-disabled");
      btnEnviar.classList.add("btn-ready");
    }

    function iniciarTimerVisual() {
      tempoRestanteSeg = TEMPO_LIMITE_MIN * 60;

      atualizarTimerVisual();

      if (timerIntervaloVisual) {
        clearInterval(timerIntervaloVisual);
      }

      timerIntervaloVisual = setInterval(() => {
        tempoRestanteSeg--;

        atualizarTimerVisual();

        if (tempoRestanteSeg <= 0) {
          clearInterval(timerIntervaloVisual);
          timerIntervaloVisual = null;
        }
      }, 1000);
    }

    function atualizarTimerVisual() {
      if (!timerEl) return;

      const min = Math.floor(tempoRestanteSeg / 60);
      const sec = tempoRestanteSeg % 60;

      timerEl.textContent =
        `⏱️ ${min}:${sec.toString().padStart(2, "0")}`;
    }
    
    function resetarAula() {
      // NOVO — reset total dos pontos visuais
      pontosAndamento = 0;
      atualizarPontosAndamento();

      // para áudio
      try {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
      } catch (e) {}

      filaVoz = Promise.resolve();

      if (micTimeout) {
        clearTimeout(micTimeout);
        micTimeout = null;
      }

      if (timerIntervaloVisual) {
        clearInterval(timerIntervaloVisual);
        timerIntervaloVisual = null;
      }

      if (timerResetAula) {
        clearTimeout(timerResetAula);
        timerResetAula = null;
      }

      // ZERA ESTADO
      index = 0;
      tentativas = 0;
      esperandoResposta = false;
      tocando = false;
      expectedAtual = "";
      lastMsgEl = null;
      lastFalandoEl = null;

      // LIMPA COMPLETAMENTE O CHAT (CHAVE)
      // remove apenas mensagens dinâmicas (feedback, user, system)
      chatArea.querySelectorAll(".chat-message:not(.base)").forEach(el => el.remove());

      // esconde novamente as frases base
      msgs.forEach(m => {
        m.style.display = "none";
        m.classList.remove("falando");
      });

      // RESET VISUAL DO TIMER
      if (timerEl) {
        timerEl.textContent = "⏱️ 00:00";
      }

      // MENSAGEM FINAL
      const fim = document.createElement("div");
      fim.className = "chat-message system fim-aula";
      fim.textContent =
        "⏱️ Tempo máximo da aula atingido. A aula foi encerrada.";
      chatArea.appendChild(fim);
      scrollChatToBottom();
      bloquearEntrada();
      btnStart.disabled = false;
    }

    function agendarResetAula() {
      // evita múltiplos timers
      if (timerResetAula) {
        clearTimeout(timerResetAula);
      }

      timerResetAula = setTimeout(() => {
        resetarAula();
      }, TEMPO_LIMITE_MIN * 60 * 1000);
    }

    function micGravando() {
      btnMic.textContent = "🎙️";
      btnMic.classList.add("mic-gravando");
    }
    
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
    
    // MANTEM O CHAT EM TELA
    function scrollChatToBottom() {
      chatArea.scrollTop = chatArea.scrollHeight;
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
    
    // TIRA ABREVIACAO PARA SER COMPARADO COM O expected_en
    function expandContractionsEn(t) {
      return (t || "")
        .replace(/\bi[’']?m\b/gi, "i am")
        .replace(/\byou[’']?re\b/gi, "you are")
        .replace(/\bweren[’']?t\b/gi, "were not")
        .replace(/\bwe[’']?re\b/gi, "we are")
        .replace(/\bthey[’']?re\b/gi, "they are")
        .replace(/\bi[’']?ve\b/gi, "i have")
        .replace(/\byou[’']?ve\b/gi, "you have")
        .replace(/\bwe[’']?ve\b/gi, "we have")
        .replace(/\bthey[’']?ve\b/gi, "they have")
        .replace(/\bi[’']?ll\b/gi, "i will")
        .replace(/\byou[’']?ll\b/gi, "you will")
        .replace(/\bwe[’']?ll\b/gi, "we will")
        .replace(/\bthey[’']?ll\b/gi, "they will")
        .replace(/\bdon[’']?t\b/gi, "do not")
        .replace(/\bdoesn[’']?t\b/gi, "does not")
        .replace(/\bdidn[’']?t\b/gi, "did not")    
        .replace(/\bwon[’']?t\b/gi, "will not")
        .replace(/\bisn[’']?t\b/gi, "is not")
        .replace(/\baren[’']?t\b/gi, "are not")        
        .replace(/\bhe[’']?s\b/gi, "he is")
        .replace(/\bshe[’']?s\b/gi, "she is")
        .replace(/\bit[’']?s\b/gi, "it is")
        .replace(/\bthat[’']?s\b/gi, "that is")
        .replace(/\bthere[’']?s\b/gi, "there is")
        .replace(/\bthere[’']?re\b/gi, "there are")
        .replace(/\bwho[’']?s\b/gi, "who is")
        .replace(/\bwhat[’']?s\b/gi, "what is")
        .replace(/\bwhere[’']?s\b/gi, "where is")
        .replace(/\bwhen[’']?s\b/gi, "when is")
        .replace(/\bhow[’']?s\b/gi, "how is")
        .replace(/\bi[’']?d\b/gi, "i had")
        .replace(/\byou[’']?d\b/gi, "you had")
        .replace(/\bhe[’']?d\b/gi, "he had")
        .replace(/\bshe[’']?d\b/gi, "she had")
        .replace(/\bwe[’']?d\b/gi, "we had")
        .replace(/\bthey[’']?d\b/gi, "they had")
        .replace(/\bcouldn[’']?t\b/gi, "could not")
        .replace(/\bshouldn[’']?t\b/gi, "should not")
        .replace(/\bwouldn[’']?t\b/gi, "would not")
        .replace(/\bmustn[’']?t\b/gi, "must not")
        .replace(/\bmayn[’']?t\b/gi, "may not")
        .replace(/\bmightn[’']?t\b/gi, "might not")
        .replace(/\bhasn[’']?t\b/gi, "has not")
        .replace(/\bhaven[’']?t\b/gi, "have not")
        .replace(/\bhadn[’']?t\b/gi, "had not")
        .replace(/\bhe[’']?ll\b/gi, "he will")
        .replace(/\bshe[’']?ll\b/gi, "she will")
        .replace(/\bit[’']?ll\b/gi, "it will")
        .replace(/\bgonna\b/gi, "going to")
        .replace(/\blet[’']?s\b/gi, "let us")
        .replace(/\bcan[’']?t\b/gi, "can not")

         return t;
    }
    // RETIRA AS ABREVIACOES ACIMA, PARA SER COMPARADO COM O expected_en.
    function normEn(s) {
      let t = (s || "").toLowerCase();
      // normaliza aspas
      t = t.replace(/[’]/g, "'").replace(/[“”]/g, '"');
      // EXPANDE ANTES DE TUDO
      t = expandContractionsEn(t);
      // remove pontuação
      t = t.replace(/[^\w\s]/g, " ");
      // normaliza espaços
      t = t.replace(/\s+/g, " ").trim();
      return t;
    }

    const FEEDBACK_OK = [
      "ótimo desempenho nessa.",
      "rápido e claro.",
      "ótimo acerto nessa.",
      "nítida resposta.",
      "ágil resposta.",
      "fantástico.",
      "ágil e preciso.",
      "ótimo trabalho nessa.",
      "ótimo desempenho.",
      "ótimo foco nessa.",
      "você falou corretamente.",
      "rápido acerto.",
      "ótima execução nessa.",
      "útil e claro.",
      "ótima execução.",
      "única e excelente.",
      "ótima expressão.",
      "ótimo controle.",
      "ótima pronúncia.",
      "ótimo trabalho.",
      "ótimo foco.",
      "ótima leitura nessa.",
      "sólido e claro.",
      "ótima resposta.",
      "ótimo, bem claro.",
      "básico perfeito.",
      "rápida e perfeita.",
      "ótima pronúncia nessa.",
      "única e perfeita.",
      "nítida pronúncia.",
      "sólido progresso.",
      "ótima melhora nessa.",
      "ótima fluência.",
      "ótima fluência nessa.",
      "ótima resposta nessa.",
      "ótimo, bom ritmo.",
      "ágil e firme.",
      "rápido e correto.",
      "ótima melhora.",
      "admirável expressão.",
      "útil e correto.",
      "ótimo progresso nessa.",
      "ótimo, bem feito.",
      "sólido e correto.",
      "ágil progresso.",
      "extraordinária resposta.",
      "ágil e direto.",
      "ótimo ritmo nessa.",
      "êxito total nessa.",
      "êxito total.",
      "ótima clareza.",
      "útil progresso.",
      "ótimo, siga assim.",
      "ágil e perfeita.",
      "ágil e excelente.",
      "incrível expressão.",
      "ótima entonação nessa.",
      "admirável trabalho.",
      "ótimo controle nessa.",
      "ágil e certeiro.",
      "ótimo, vá em frente.",
      "incrível trabalho.",
      "ótimo acerto.",
      "ágil acerto.",
      "rápida e excelente.",
      "ótimo progresso.",
      "sólida resposta.",
      "ágil e correto.",
      "útil e rápido.",
      "ótima dicção nessa.",
      "ágil e consistente.",
      "fantástica resposta.",
      "ágil execução.",
      "ágil e limpo.",
      "ágil e eficaz.",
      "você foi muito bem.",
      "rápido e firme.",
      "ágil e forte.",
      "ótimo, continue assim.",
      "rápido e preciso.",
      "útil resposta.",
      "único e perfeito.",
      "ótima evolução.",
      "ótimo resultado nessa.",
      "ágil e confiante.",
      "ótima clareza nessa.",
      "ótima expressão nessa.",
      "ótimo resultado.",
      "ótimo avanço.",
      "ágil e seguro.",
      "nítido e claro.",
      "extraordinário.",
      "útil expressão.",
      "ótima evolução nessa.",
      "você respondeu corretamente.",
      "ótimo avanço nessa.",
      "útil e preciso.",
      "fantástico trabalho.",
      "nítido e correto.",
      "admirável resposta.",
      "ótimo ritmo.",
      "ótimo esforço.",
      "ótimo entendimento.",
      "ágil e claro.",
      "você acertou.",
      "incrível resposta.",
      "ótima fala nessa."
    ].map(msg =>
      USER_NAME ? `${USER_NAME}, ${msg}` : msg
    );

    const FEEDBACK_ERR = [  
      "Essa ficou errada.",        
      "Não está bem certo.",   
      "Vamos tentar novamente.",   
      "Você cometeu um erro.",
      "Errar faz parte.",
      "Quer tentar outra vez?",
      "Não acertou.",   
      "Essa não está correta.",
      "Quase acertou.",
      "Pode tentar outra vez?",
      "Não foi dessa vez.",
      "Erro pequeno.",
      "Cometeu um errinho.",
      "Tente mais uma vez.",
      "Não acertou essa.",
      "Essa ficou incorreta.",
      "Vamos tentar de novo.",
      "Errinho básico.",
      "Não está certo.",
      "Pode tentar novamente?",
      "Essa não foi a certa.",
      "Errar é normal.",
      "Não acertou dessa vez.",
      "Não está correto.",
      "Falhou!",
      "Cometeu um erro.",
      "Cometeu uma falha.",
      "Errou um detalhe.",
      "Errinho simples.",
      "Essa não acertou.",
      "Essa deu errado.",
      "Deu errado.",
      "Deu errado essa.",
      "Resposta incorreta.",
      "Essa errou.",
      "Errou essa.",
      "Errou!",
      "Não deu certo.",
      "Essa ficou ruim.",
      "Não funcionou.",
      "Essa foi errada.",
      "Essa saiu errada.",
      "Resposta falha.",
      "Essa não deu certo.",
      "Tentativa errada.",
      "Essa tropeçou.",
      "Não valeu.",
      "Essa falhou.",
      "Essa não funcionou.",
      "Tentativa falha.",
      "Não foi boa.",
      "Tudo bem errar.",
      "Tudo bem falhar.",
      "Falhar faz parte."      
    ];  

    const MSG_AVANCO = [
      "não marcou pontos, continuamos.",
      "não foi dessa vez, continuamos.",
      "você falhou nessa, continuamos.",      
      "não marcou pontos, seguimos.",
      "não foi dessa vez, seguimos.",
      "você falhou nessa, seguimos.",
      "você errou, vamos continuar.",
      "você falhou, vamos continuar.",
      "você errou, vamos seguir.",
      "você falhou, vamos seguir.",    
      "você falhou, seguimos em frente.",
      "você errou, seguimos em frente.",
      "você errou, seguimos à próxima.",
      "você falhou, passamos à próxima.",
      "você errou, seguimos avante.",
      "você falhou, seguimos avante.",
      "você errou, continuamos então.",
      "você falhou, continuamos então.",
      "você falhou, vamos à próxima.",
      "você errou, vamos à próxima.",      
      "está errada, continuamos então.",
      "está errada, próxima então.",
      "você falhou, passamos à seguinte.",
      "você errou, vamos à seguinte.",
      "não deu certo, continuamos.",
      "não acertou, continuamos.",
      "você falhou, continuamos.",
      "está errada, seguimos.",
      "você errou, seguimos.",
      "você errou, continuamos.",
      "você falhou, seguimos.",      
      "está errada, continuamos.",     
      "está errada, seguimos então.",
      "não deu certo, seguimos."     
    ].map(msg =>
      USER_NAME ? `${USER_NAME}, ${msg}` : msg
    );

      // ESCONDE TODAS
      msgs.forEach(m => m.style.display = "none");

      bloquearEntrada();      

      // MOSTRA FRASE + FALA   
      function mostrarSistema() {        
        if (offlinePause) return;
        if (execAtiva) return;
          execAtiva = true;

        if (professorLock) {
          execAtiva = false;
          return;
        }
        professorLock = true;

        const unlock = () => {
          execAtiva = false;
          professorLock = false;
        };

        if (FLAG !== 0) {
          professorLock = false;
          unlock();
          return;
        }      
        
        if (tocando) { 
          professorLock = false;
          unlock();
          return;
        }

        if (index >= msgs.length) {
          if (timerResetAula) {
            clearTimeout(timerResetAula);
            timerResetAula = null;
          }
          bloquearEntrada();
          btnStart.disabled = false;

          // fim da lição, zera pontos visuais
          pontosAndamento = 0;
          atualizarPontosAndamento();
          professorLock = false;
          unlock();
          return;
        }

        const msg = msgs[index];

        if (lastFalandoEl && lastFalandoEl !== msg) {
          lastFalandoEl.classList.remove("falando");
        }
        const lineId = msg.dataset.id;
        const auto = parseInt(msg.dataset.auto || "0");
        const end  = parseInt(msg.dataset.end  || "0");      
        
        msg.style.display = "block";
        lastMsgEl = msg;
        scrollChatToBottom();
        msg.classList.add("falando");
        lastFalandoEl = msg;

        bloquearEntrada();   

        fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ line_id: lineId })
        })
        
        .then(r => {
          if (!r.ok) {
            
            offlinePause = true;

            FLAG = 0;
            tocando = false;
            esperandoResposta = false;

            bloquearEntrada();

            // encerra silenciosamente este ciclo
            throw new Error("offline");
          }
          return r.json();
        })

        // .then(r => r.json())
        .then(async d => {
          try {
          if (d.files && d.files.length) { 
            tocando = true;     

            await new Promise(r => setTimeout(r, 100));
            await falarComoAntigo(d.files); 

            // ===== PRÉ-GERA ÁUDIO DA PRÓXIMA FRASE (SEM TOCAR) =====
            const nextMsg = msgs[index + 1];
            if (nextMsg) {
              fetch("/tts/line/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ line_id: nextMsg.dataset.id })
              });

              // PRELOAD DA PRÓXIMA FRASE
              const nextLineId = nextMsg.dataset.id;
              const nextUrl = "/media/cache/line_" + nextLineId;
              const preload = new Audio(nextUrl);
              preload.preload = "auto";
              preload.load();
            }

            tocando = false;            

            if (auto === 1) {
              FLAG = 0;   
            } else {
              tocarBeep();
              FLAG = 1;  
              if (autoMicAtivo) {
                setTimeout(() => abrirMicrofoneComTempo(), 150);
              }
            }
            
          }      

          // SÓ AGORA DECIDE O PRÓXIMO PASSO
          if (end === 1) {
            bloquearEntrada(); 
            index++;
            return;
          }

          if (auto === 1) {            
            index++;
            setTimeout(() => mostrarSistema(), 0);            
            return mostrarSistema();
          }

          esperandoResposta = true;
          expectedAtual = msg.dataset.expected || "";
          tentativas = 0;
          liberarEntrada();
          } finally {
            professorLock = false;
            unlock();
          }
        });
      } 

    // SEM INTERNET
    window.addEventListener("offline", () => {
        offlinePause = true;

        // pausa tudo
        try { recognition.stop(); } catch(e) {}
        try { audioPlayer.pause(); audioPlayer.currentTime = 0; } catch(e) {}

        tocando = false;
        esperandoResposta = false;
        FLAG = 0;

        bloquearEntrada();

        const aviso = document.createElement("div");
        aviso.className = "chat-message system";
        aviso.textContent = "Sem conexão. Aguardando internet...";
        chatArea.appendChild(aviso);
        scrollChatToBottom();
      });

      window.addEventListener("online", () => {
        if (!offlinePause) return;

        offlinePause = false;

        // remove aviso
        chatArea.querySelectorAll(".chat-message.system")
          .forEach(el => {
            if (el.textContent.includes("Sem conexão")) el.remove();
          });

        mostrarSistema();
      });
      // FIM SEM INTERNET


      // INCIAR LICAO
      function iniciarLicao() {
        FLAG = 0;
        // btnStart.disabled = true;
        // remove mensagem de fim de aula, se existir
        chatArea.querySelectorAll(".fim-aula").forEach(el => el.remove());
        // LIMPA TUDO QUE FOI GERADO NA EXECUÇÃO ANTERIOR
        chatArea.querySelectorAll(".chat-message:not(.base)").forEach(el => el.remove());

        index = 0;
        tentativas = 0;
        esperandoResposta = false;
        expectedAtual = "";

        pontosAndamento = 0;
        atualizarPontosAndamento();

        lastMsgEl = null;
        lastFalandoEl = null;

        // ESCONDE TODAS AS FRASES BASE
        msgs.forEach(m => {
          m.style.display = "none";
          m.classList.remove("falando");
        });

        // INICIA TIMER
        iniciarTimerVisual();
        agendarResetAula();
        mostrarSistema();
      }      
      
      if (btnStart) {
        btnStart.onclick = async function () {
          // SE ESTIVER EM STOP → PARAR (refresh)
          if (btnStart.classList.contains("stop-madeira-velha")) {
            location.reload();
            return;
          }

          // SE ESTIVER EM START → INICIAR (sem refresh)
          const r = await fetch("/user/nivel/");
          const data = await r.json();
              

          if (!data.exists || data.nivel === 0) {
            document.getElementById("nivel-modal").style.display = "block";
            return;
          }

          btnStart.classList.remove("play-madeira-velha");
          btnStart.classList.add("stop-madeira-velha");

          iniciarLicao();
        }  
      };

      // BOTÃO MICROFONE
      if (btnMic) {
        btnMic.onclick = function () {
          abrirMicrofoneComTempo();
        };
      }      

      // RESPOSTA DO USUÁRIO
      // ===== escreve avaliação do professor =====
      function escreverProfessor(text, afterEl) {
        const div = document.createElement("div");
        div.className = "chat-message system";
        div.textContent = text;
        afterEl.after(div);
        return div;
      }

      // ENVIA DADOS PARA SALVAR NA TABELA progress
      function salvarProgresso({ chatId, lessonId, points }) {
        fetch("/progress/save/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: chatId,
            lesson_id: lessonId,
            points: points
          })
        })  
      }

      // ENVIA DADOS PARA SALVAR NA TABELA progress_tmp
      function salvarProgressoTmp({ chatId, points }) {
        fetch("/progress/tmp/save/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: chatId,
            points: points
          })
        });
      }
      
      // ########################################
      // NORMALIZACOES
      // ########################################
      // FUNCAO NORMALIZAR O THEY
      function normalizeThey(words, i) {
        const w = words[i];
        const next = words[i + 1];
        // INCLUIR AQUI PALAVRAS SEMELHANTES A THEY
        if (!["day", "dey", "dei", "tei", "thei"].includes(w)) return w;
        // INCLUIR AQUI A PALAVRA DEPOIS DO THEY
        if (["are","were","have","will","do","need","follow","hear","learn","like","want","go","get","make","take","see","know","say","think","come","meet","can","understand","worked","help","ask","come","be","heard"].includes(next)) {
          return "they";
        }
        return "day";
      }

      function normalizeTheyAnywhere(texto) {
        const words = texto.split(" ");

        for (let i = 0; i < words.length - 1; i++) {
          words[i] = normalizeThey(words, i);
        }
        return words.join(" ");
      }

      function normalizeAskTense(texto, expectedEn) {
        // Se a expected claramente indica passado, não altera
        const pastIndicators = /\b(asked|was|were|did|had|yesterday|last|ago|before|earlier|previously|already)\b/i;
        if (pastIndicators.test(expectedEn)) return texto;

        // Substitui apenas "asked" isolado como verbo principal (não seguido de preposição)
        return texto.replace(/\basked\b(?!\s+(to|for|about|if|whether|me|him|her|them)\b)/gi, "ask");
      }
     
      // ########################################
      // FIM NORMALIZACOES
      // ########################################    

      // ===== RESPOSTA DO USUÁRIO =====
      recognition.onresult = async function (e) {
        if (FLAG !== 1) return;
        const textoBruto = e.results[0][0].transcript;        
        if (!esperandoResposta) return;
        const textoCorrigido = aplicarCorrecoesVoz(textoBruto);
        //const texto = normEn(textoBruto);
        const texto = normEn(textoCorrigido);        

        if (["next", "skip"].includes(texto)) {
          // corta mic imediatamente
          encerrarMicrofone();

          // bloqueia entradas
          bloquearEntrada();

          // mensagem visual opcional (recomendado)
          const skip = document.createElement("div");
          skip.className = "chat-message system";
          skip.textContent = "Frase pulada.";
          (lastMsgEl || msgs[index]).after(skip);

          // limpa estado
          esperandoResposta = false;
          expectedAtual = "";
          tentativas = 0;

          // avança para próxima frase
          setTimeout(() => {
            index++;
            lastMsgEl = null;
            mostrarSistema();
          }, 150);

          FLAG = 0;

          return;
        }

        encerrarMicrofone();
        bloquearEntrada(); 

        // COMPARADO
        let recebido = normEn(textoCorrigido);
        recebido = normalizeTheyAnywhere(recebido);
        recebido = normalizeAskTense(recebido, expectedAtual);

        // ===== escreve ALUNO (sempre após a última mensagem) =====
        const user = document.createElement("div");
        user.className = "chat-message user";
        
        // FALADO
        let exibicao = textoCorrigido;
        exibicao = normalizeTheyAnywhere(exibicao);
        exibicao = normalizeAskTense(exibicao, expectedAtual);
        user.textContent = exibicao;

        (lastMsgEl || msgs[index]).after(user);
        lastMsgEl = user;        

        // divide expected_en por OR / or
        const esperados = (expectedAtual || "")
          .split(/\s+or\s+/i)
          .map(e => normEn(e));          

        const LESSON_ID = Number(document.body.dataset.lessonId);
        const MODO_NOVO = (LESSON_ID === 4);

        if (MODO_NOVO) {   

        function normalizeLikeBackend(text) {
          if (!text) return "";

          let t = text.toLowerCase();
          
          const contractions = { 
                "i'm": "i am",
                "you're": "you are",
                "he's": "he is",
                "she's": "she is",
                "it's": "it is",
                "we're": "we are",
                "they're": "they are",
                "i've": "i have",
                "you've": "you have",
                "we've": "we have",
                "they've": "they have",
                "i'd": "i would",
                "you'd": "you would",
                "he'd": "he would",
                "she'd": "she would",
                "we'd": "we would",
                "they'd": "they would",
                "i'll": "i will",
                "you'll": "you will",
                "he'll": "he will",
                "she'll": "she will",
                "we'll": "we will",
                "they'll": "they will",
                "isn't": "is not",
                "aren't": "are not",
                "wasn't": "was not",
                "weren't": "were not",
                "don't": "do not",
                "doesn't": "does not",
                "didn't": "did not",
                "haven't": "have not",
                "hasn't": "has not",
                "hadn't": "had not",
                "can't": "can not",
                "couldn't": "could not",
                "shouldn't": "should not",
                "wouldn't": "would not",
                "mightn't": "might not",
                "mustn't": "must not",
                "won't": "will not",
                "shan't": "shall not",
                "could've": "could have",
                "should've": "should have",
                "would've": "would have",
                "might've": "might have",
                "must've": "must have",
                "what's": "what is",
                "where's": "where is",
                "who's": "who is",
                "how's": "how is",
                "when's": "when is",
                "why's": "why is",
                "there's": "there is",
                "here's": "here is",
                "that's": "that is",
                "this's": "this is",
                "let's": "let us",
                "gonna": "going to",
                "wanna": "want to",
                "gotta": "got to"
            };

          for (const c in contractions) {
            const esc = c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            t = t.replace(new RegExp(`\\b${esc}\\b`, "g"), contractions[c]);
          }

          const numbers = {
            "zero":"0",
            "one":"1",
            "two":"2",
            "three":"3",
            "four":"4",
            "five":"5",
            "six":"6",
            "seven":"7",
            "eight":"8",
            "nine":"9",
            "ten":"10"
          };
          for (const w in numbers) {
            t = t.replace(new RegExp(`\\b${w}\\b`, "g"), numbers[w]);
          }

          // horas "oclock" (hora exata)
          const hours = {
            "one":"1",
            "two":"2",
            "three":"3",
            "four":"4",
            "five":"5",
            "six":"6",
            "seven":"7",
            "eight":"8",
            "nine":"9",
            "ten":"10",
            "eleven":"11",
            "twelve":"12"
          };
          for (const w in hours) {
            t = t.replace(new RegExp(`\\b${w}\\s+oclock\\b`, "g"), `${hours[w]}:00`);
          }

          //t = t.replace(/[^\w\s]/g, "").replace(/\s+/g, " ").trim();
          t = t.replace(/[^\w\s:]/g, "").replace(/\s+/g, " ").trim();

          return t;
        }

        function lcsMatchedIndices(expectedTokens, spokenTokens) {
          const n = expectedTokens.length, m = spokenTokens.length;
          const dp = Array.from({ length: n + 1 }, () => Array(m + 1).fill(0));

          for (let i = 1; i <= n; i++) {
            for (let j = 1; j <= m; j++) {
              dp[i][j] = (expectedTokens[i - 1] === spokenTokens[j - 1])
                ? dp[i - 1][j - 1] + 1
                : Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
          }

          const ok = new Set();
          let i = n, j = m;
          while (i > 0 && j > 0) {
            if (expectedTokens[i - 1] === spokenTokens[j - 1]) {
              ok.add(j - 1);
              i--; j--;
            } else if (dp[i - 1][j] >= dp[i][j - 1]) {
              i--;
            } else {
              j--;
            }
          }
          return ok;
        }

        function marcarErros(expected, spoken) {
          const exp = normalizeLikeBackend(expected).split(" ").filter(Boolean);
          const spkNorm = normalizeLikeBackend(spoken).split(" ").filter(Boolean);
          const spkRaw  = spoken.split(/\s+/);

          const okIdx = lcsMatchedIndices(exp, spkNorm);

          return spkRaw.map((w, idx) =>
            okIdx.has(idx) ? w : `<span style="color:red;font-weight:bold">${w}</span>`
          ).join(" ");
        }

          // uma frase de 10 palvras : 3s + (10*0.8s) = 11s
          let TEMPO_BASE = 3000;          // 3s mínimos
          let TEMPO_POR_PALAVRA = 500;   // 0.8s por palavra
          let TEMPO_MAX = 20000;         // 12s máximo
          
          // chama avaliação (backend)
          const rEval = await fetch("/speech/evaluate/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              expected: expectedAtual,
              spoken: textoCorrigido
            })
          });

          const data = await rEval.json();

          const pontos = Number(data.correct || 0);

          const totalEsperado = normalizeLikeBackend(expectedAtual).split(" ").length;
          const totalFalado   = normalizeLikeBackend(textoCorrigido).split(" ").length;
          const penalidade = Math.abs(totalFalado - totalEsperado);


          // ===== FEEDBACK VISUAL (mesmo padrão do else) =====
          const userMsgEl = lastMsgEl;
          const prof = document.createElement("div");
          prof.className = "chat-message system";
          //prof.textContent = `Você acertou ${pontos} palavras, ganhou ${pontos} pontos.`;
          const saldo = Math.max(pontos - penalidade, 0);
          prof.textContent = `Você acertou ${pontos} palavras, penalidade ${penalidade}, total ${saldo} pontos.`;


          (lastMsgEl || msgs[index]).after(prof);
          lastMsgEl = prof;
          scrollChatToBottom();

          if (pontos > 0) {
            prof.classList.add("correto");
            if (prof) setTimeout(() => prof.classList.remove("correto"), 6000);
          } else {
            if (prof) prof.classList.add("errado");
            if (prof) setTimeout(() => prof.classList.remove("errado"), 6000);
          }

          if (userMsgEl) userMsgEl.innerHTML = marcarErros(expectedAtual, textoCorrigido);

          // ===== FEEDBACK POR VOZ (mesmo padrão do else: /tts/line/) =====
          FLAG = 2;
          if (FLAG !== 2) return;

          const rTts = await fetch("/tts/line/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: prof.textContent, lang: "pt" })
          });

          const d = await rTts.json();
          if (d.files && d.files.length) {
            tocando = true;
            await new Promise(r => setTimeout(r, 1100));
            await tocarUm(d.files[0]);
            tocando = false;
          }

          // ===== PONTOS VISUAIS (mesmo padrão do else) =====
          pontosAndamento += pontos;
          atualizarPontosAndamento();

          // ===== SALVA NAS 2 TABELAS (mesmas funções do else) =====
          salvarProgresso({
            chatId: msgs[index].dataset.id,
            lessonId: LESSON_ID,
            points: pontos
          });

          salvarProgressoTmp({
            chatId: msgs[index].dataset.id,
            points: pontos
          });

          atualizarPontosTotais();
          atualizarPontosFeitos();

          // ===== AVANÇA SEM REPETIR (modo novo) =====
          FLAG = 0;
          esperandoResposta = false;
          expectedAtual = "";
          tentativas = 0;

          setTimeout(() => {
            index++;
            lastMsgEl = null;
            mostrarSistema();
          }, 150);

          return;

        } else {

        const ok = esperados.includes(recebido);

        // bloqueia mic enquanto avalia
        bloquearEntrada(); 

        // ===== escolhe feedback =====
        const msg = ok
        ? FEEDBACK_OK[Math.floor(Math.random() * FEEDBACK_OK.length)]
        : FEEDBACK_ERR[Math.floor(Math.random() * FEEDBACK_ERR.length)];

        // ===== monta feedback FINAL (antes de imprimir) =====
        let feedbackText = msg;
        let feedbackHTML = msg;

        const tentativaAgora = tentativas + 1;
        if (!ok) {          
          if (tentativaAgora < MAX_TENTATIVAS) {
            const expectedRaw = expectedAtual || "";
            feedbackText = `${msg} Repita comigo: ${expectedRaw}`;
            feedbackHTML = `${msg} <span class="hint">Repita comigo: <span style="color: red;">${expectedRaw}</span></span>`;
          }
        }
        
        let prof = null;      
        if (ok || tentativaAgora < MAX_TENTATIVAS) {
          prof = document.createElement("div");
          prof.className = "chat-message system";
          prof.innerHTML = feedbackHTML;

          lastMsgEl.after(prof);
          lastMsgEl = prof;
          scrollChatToBottom();
        }  
        // const LESSON_ID = Number(document.body.dataset.lessonId);
        // ===== decisão de fluxo =====
        if (ok) {
          FLAG = 2;
          if (prof) prof.classList.add("correto");
          if (prof) setTimeout(() => prof.classList.remove("correto"), 6000);

          if (FLAG !== 2) return;
          const r = await fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: msg, lang: "pt" })
        });  

        const d = await r.json(); 
        if (d.files && d.files.length) {
          tocando = true;
          await new Promise(r => setTimeout(r, 1100));
          await tocarUm(d.files[0]);
          tocando = false;
        }

        // === SALVA PROGRESSO (ACERTO) ===
        const pontos =
          tentativas === 0 ? 5 :
          tentativas === 1 ? 3 :
          1;
          
          pontosAndamento += pontos;
          atualizarPontosAndamento();
          
          salvarProgresso({
            chatId: msgs[index].dataset.id,
            lessonId: LESSON_ID,
            points: pontos
          });          

          salvarProgressoTmp({
            chatId: msgs[index].dataset.id,
            points: pontos
          });

          atualizarPontosTotais();
          
          atualizarPontosFeitos();
          
          FLAG = 0;

          esperandoResposta = false;
          expectedAtual = "";
          tentativas = 0;
                    
          setTimeout(() => {
            index++;
            lastMsgEl = null;
            mostrarSistema();
          }, 150);
          return;          
        }

        // errou
        tentativas++;
        if (prof) prof.classList.add("errado");
        if (prof) setTimeout(() => prof.classList.remove("errado"), 7000);

      if ((!ok) && (tentativas < MAX_TENTATIVAS)) {
        if (FLAG !== 1) return;
        const r = await fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: feedbackText, lang: "pt" })
        });

        const d = await r.json();
        if (d.files && d.files.length) {
          tocando = true;
          await new Promise(r => setTimeout(r, 1100));
          await falarComoAntigo(d.files);
          tocando = false;

          tocarBeep();

          if (autoMicAtivo) {
            setTimeout(() => {
                abrirMicrofoneComTempo();
              }, 150);
            }  
        }
        esperandoResposta = true;
        liberarEntrada();
        return;
      }

      if (tentativas >= MAX_TENTATIVAS) {
        if (FLAG !== 1) return;
        salvarProgresso({
          chatId: msgs[index].dataset.id,
          lessonId: LESSON_ID,
          attempts: MAX_TENTATIVAS,
          points: 0
        });

        // mensagem de avanço (SUBSTITUI o último "Let's try again")
        const msgAvanco = MSG_AVANCO[Math.floor(Math.random() * MSG_AVANCO.length)];

        const avanco = document.createElement("div");
        avanco.className = "chat-message system errado";
        avanco.textContent = msgAvanco;

        lastMsgEl.after(avanco);
        lastMsgEl = avanco;
        scrollChatToBottom();

        setTimeout(() => avanco.classList.remove("errado"), 8000);
        
        // fala a mensagem de avanço
        const r = await fetch("/tts/line/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: msgAvanco, lang: "pt" })
        });

        const d = await r.json();
        if (d.files && d.files.length) {
          tocando = true;
          await new Promise(r => setTimeout(r, 1100));
          await tocarUm(d.files[0]);
          tocando = false;
        }

        // reseta e avança
        FLAG = 0;
        esperandoResposta = false;
        expectedAtual = "";
        tentativas = 0;
        index++;
        lastMsgEl = null;
        return mostrarSistema();
      }

        // pode tentar de novo
        esperandoResposta = true;
        liberarEntrada();     
        
        } // essa chave fexa
      };
    });    
    
    const btnSalvarNivel = document.getElementById("btn-salvar-nivel");
    if (btnSalvarNivel) {
      btnSalvarNivel.onclick = async function () {
        const nivel = document.querySelector("input[name='nivel']:checked");

        if (!nivel) {
          alert("Escolha um nível");
          return;
        }

        const r = await fetch("/user/nivel/set/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
          },
          body: JSON.stringify({ nivel: nivel.value })
        });

        if (!r.ok) {
          alert("Erro ao salvar nível");
          return;
        }

        document.getElementById("nivel-modal").style.display = "none";
        iniciarLicao();
        location.reload();
      };
    }