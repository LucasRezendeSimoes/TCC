let arquivoSelecionado = null;

// Toggle sidebar
document.getElementById('toggleSidebar').addEventListener('click', function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
});

// Resize estilo VS Code
const resizer = document.getElementById("resizer");
const mainContent = document.getElementById("mainContent");
const bottomPanel = document.getElementById("bottomPanel");

let isResizing = false;

resizer.addEventListener("mousedown", function () {
  isResizing = true;
  document.body.style.cursor = "row-resize";
});

window.addEventListener("mousemove", function (e) {
  if (!isResizing) return;

  const windowHeight = window.innerHeight;
  const newBottomHeight = windowHeight - e.clientY;

  if (newBottomHeight > 50 && newBottomHeight < windowHeight - 100) {
    bottomPanel.style.height = newBottomHeight + "px";
  }
});

window.addEventListener("mouseup", function () {
  isResizing = false;
  document.body.style.cursor = "default";
});

// --------------------- FORM 1: SQL manual
document.getElementById("sqlForm").addEventListener("submit", async function(e) {
  e.preventDefault();

  const sql = this.querySelector("textarea").value;

  try {
    const res = await fetch("/query", {
      method: "POST",
      body: new URLSearchParams({ sql, arquivo: arquivoSelecionado }),
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      bottomPanel.innerHTML = `<pre>Erro ao parsear JSON: ${err}\nResposta:\n${text}</pre>`;
      return;
    }

    bottomPanel.innerHTML = `<pre>${data.result}</pre>`;
  } catch (err) {
    bottomPanel.innerHTML = `<pre>Erro de conexão: ${err}</pre>`;
  }
});

// --------------------- FORM 2: Query automática
document.getElementById("form-consulta").addEventListener("submit", async function (e) {
  e.preventDefault();

  const hash = document.getElementById("hash").value;
  const inicio = document.getElementById("inicio").value;
  const fim = document.getElementById("fim").value;
  const camera = document.getElementById("camera").value;

  const params = new URLSearchParams();
  if (hash) params.append("hash", hash);
  if (inicio) params.append("inicio", inicio);
  if (fim) params.append("fim", fim);
  if (camera) params.append("numero_camera", camera);
  if (arquivoSelecionado) params.append("arquivo", arquivoSelecionado);

  try {
    const res = await fetch("/auto_query", {
      method: "POST",
      body: params,
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      }
    });

    const text = await res.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch (err) {
      bottomPanel.innerHTML = `<pre>Erro ao parsear JSON: ${err}\nResposta:\n${text}</pre>`;
      return;
    }

    bottomPanel.innerHTML = `<pre>${data.result}</pre>`;
  } catch (err) {
    bottomPanel.innerHTML = `<pre>Erro de conexão: ${err}</pre>`;
  }
});

// --------------------- Carregar lista de arquivos
async function carregarArquivos() {
  try {
    const res = await fetch("/arquivos");
    const data = await res.json();

    if (data.arquivos) {
      const lista = document.getElementById("item-list");
      lista.innerHTML = ""; // limpa antes

      data.arquivos.forEach((nome, index) => {
        const li = document.createElement("li");
        li.textContent = nome;
        li.classList.add("arquivo-item");

        li.addEventListener("click", () => {
          arquivoSelecionado = nome;

          // Remover destaque de todos
          document.querySelectorAll(".arquivo-item").forEach(el => el.classList.remove("ativo"));
          li.classList.add("ativo");
        });

        lista.appendChild(li);

        // Seleciona o primeiro arquivo automaticamente
        if (index === 0) {
          li.click();
        }
      });
    } else {
      console.error("Erro ao carregar arquivos:", data.erro);
    }
  } catch (err) {
    console.error("Erro ao buscar arquivos:", err);
  }
}

// Chamar ao carregar a página
carregarArquivos();
