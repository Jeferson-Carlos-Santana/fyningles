// MODAL DELETE
function openDeleteModal(term) {
  document.getElementById("deleteTerm").value = term;
  document.getElementById("deleteModal").style.display = "block";
}
function closeDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
}
//FIM MODAL DELETE

// BUSCA POR SELECT, CONECTA O SELECT DE IDIOMAS COM O BACKEND.
function changeLang(lang) {
  if (!lang) return;
  window.location.href = `?lang=${lang}`;
}
// FIM BUSCA POR SELECT, CONECTA O SELECT DE IDIOMAS COM O BACKEND.

// BUSCA DE UM VALOR NA LIST
const search = document.getElementById("list-search");
search && search.addEventListener("input", () => {
  const v = search.value.toLowerCase();
  document.querySelectorAll(".content-inner ul li").forEach(li => {
    li.style.display = li.textContent.toLowerCase().includes(v) ? "" : "none";
  });
});
// FIM BUSCA DE UM VALOR NA LIST

// ENVIA VALOR PARA CONFIRMACAO DO INSERIMENTO IDIOMA
function confirmForce() {
    document.getElementById("force").value = "1";
    document.getElementById("dict-form").submit();
  }
// FIM ENVIA VALOR PARA CONFIRMACAO DO INSERIMENTO IDIOMA