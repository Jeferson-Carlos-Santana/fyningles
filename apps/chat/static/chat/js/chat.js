document.addEventListener("DOMContentLoaded", function () {
    // ===== SPEECH RECOGNITION =====
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Seu navegador não suporta reconhecimento de voz.");
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    // ===== ELEMENTOS DO DOM =====
    const chatMessages = document.querySelectorAll(".chat-message");
    const btnStart = document.getElementById("btn-start");
    const btnMic = document.getElementById("btn-mic");

    let currentIndex = 0;

    // Esconde todas as mensagens no início
    chatMessages.forEach(msg => msg.style.display = "none");
    btnMic.disabled = true;

    // Função que mostra a próxima frase e gera áudio
    function showNextSystemMessage() {
        if (currentIndex >= chatMessages.length) {
            btnMic.disabled = true;
            btnStart.disabled = true;
            alert("Lição concluída!");
            return;
        }

        const currentMsg = chatMessages[currentIndex];
        const lineId = currentMsg.dataset.id;

        currentMsg.style.display = "block";

        // Gera TTS no servidor
        fetch("/tts/line/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ line_id: lineId })
        })
        .then(r => r.json())
        .then(data => {
            if (data.file) {
                playWhenReady(data.file);
            } else {
                console.error("Erro ao gerar áudio:", data);
            }
        })
        .catch(err => console.error("Erro no fetch TTS:", err));

        btnMic.disabled = false;
    }

    // Função para tentar tocar áudio quando estiver pronto
    function playWhenReady(file, tries = 30) {
        const url = "/media/cache/" + file + "?t=" + Date.now();
        fetch(url, { method: "HEAD" })
            .then(r => {
                if (!r.ok) throw new Error("Arquivo ainda não pronto");
                const audio = new Audio(url);
                audio.play().catch(() => {
                    if (tries > 0) setTimeout(() => playWhenReady(file, tries - 1), 150);
                });
            })
            .catch(() => {
                if (tries > 0) setTimeout(() => playWhenReady(file, tries - 1), 150);
            });
    }

    // ===== EVENTOS =====
    btnStart.onclick = function () {
        btnStart.disabled = true;
        showNextSystemMessage();
    };

    btnMic.onclick = function () {
        btnMic.disabled = true;
        recognition.start();
    };

    recognition.onresult = function (event) {
        const spokenText = event.results[0][0].transcript;
        
        // Mostra o que o usuário falou
        const userMessage = document.createElement("div");
        userMessage.className = "chat-message user";
        userMessage.textContent = spokenText;
        chatMessages[currentIndex].after(userMessage);

        currentIndex++;
        showNextSystemMessage();
    };

    recognition.onerror = function (event) {
        console.error("Erro no reconhecimento de voz:", event.error);
        btnMic.disabled = false;
    };
});
