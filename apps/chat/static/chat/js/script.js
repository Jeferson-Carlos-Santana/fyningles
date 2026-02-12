document.addEventListener("DOMContentLoaded", () => { // ABRE E FECHA O MENU LATERAL

    const toggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");

    toggle.addEventListener("click", () => {
        sidebar.classList.toggle("collapsed");
    });

    const closeBtn = document.querySelector(".sidebar-close");

    closeBtn.addEventListener("click", () => {
      sidebar.classList.add("collapsed");
    });

    if (window.innerWidth <= 900) {
      sidebar.classList.add("collapsed");
    } else {
      sidebar.classList.remove("collapsed");
    }    
// FIM ABRE E FECHA O MENU LATERAL

// CLICAR FORA DO MENU OU NOS LINKS DO MENU PRA FECHAR
document.addEventListener("click", (e) => {

  if (window.innerWidth > 520) return;
  // só fecha se o menu estiver ABERTO (ou seja: NÃO está collapsed)
  if (sidebar.classList.contains("collapsed")) return;

  // se clicou dentro da sidebar ou no botão toggle, não fecha
  if (sidebar.contains(e.target) || toggle.contains(e.target)) return;

  // clicou fora → fecha
  sidebar.classList.add("collapsed");
});

// CLICAR FORA DO MENU OU NOS LINKS DO MENU PRA FECHAR

const searchInput = document.querySelector(".lesson-search");
const lessonItems = document.querySelectorAll(".lessons li");

if (searchInput) {
  searchInput.addEventListener("input", () => {
    const value = searchInput.value.toLowerCase();

    lessonItems.forEach(li => {
      const text = li.innerText.toLowerCase();
      li.style.display = text.includes(value) ? "block" : "none";
    });
  });
}

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


const creditBtn = document.querySelector(".credit-btn");
const creditModal = document.getElementById("credit-modal");
const creditClose = document.getElementById("credit-close");

if (creditBtn) {
    creditBtn.addEventListener("click", () => {
        creditModal.style.display = "block";
    });
}

if (creditClose) {
    creditClose.addEventListener("click", () => {
        creditModal.style.display = "none";
    });
}

window.addEventListener("click", (e) => {
    if (e.target === creditModal) {
        creditModal.style.display = "none";
    }
});


});
