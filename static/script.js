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

resizer.addEventListener("mousedown", () => {
  isResizing = true;
  document.body.style.cursor = "row-resize";
});

window.addEventListener("mousemove", (e) => {
  if (!isResizing) return;
  const containerRect = document.querySelector(".right-side").getBoundingClientRect();
  const newHeight = containerRect.bottom - e.clientY;

  if (newHeight > 50 && newHeight < window.innerHeight - 100) {
    bottomPanel.style.height = newHeight + "px";
  }
});

window.addEventListener("mouseup", () => {
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
  const linha = document.getElementById("linha").value;
  const estacao = document.getElementById("estacao").value;

  const params = new URLSearchParams();
  if (hash) params.append("hash", hash);
  if (inicio) params.append("inicio", inicio);
  if (fim) params.append("fim", fim);
  if (camera) params.append("numero_camera", camera);
  if (arquivoSelecionado) params.append("arquivo", arquivoSelecionado);
  if (linha) params.append("linha", linha);
  if (estacao) params.append("estacao", estacao);

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

    if (camera) {
      document.getElementById("mapa-frame").src = "/mapa?numero_camera=" + camera;
    } else {
      document.getElementById("mapa-frame").src = "/mapa";
    }


  } catch (err) {
    bottomPanel.innerHTML = `<pre>Erro de conexão: ${err}</pre>`;
  }
});

// --------------------- Carregar lista de arquivos e conteúdo ao clicar
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

        li.addEventListener("click", async () => {
          arquivoSelecionado = nome;

          // Remover destaque de todos
          document.querySelectorAll(".arquivo-item").forEach(el => el.classList.remove("ativo"));
          li.classList.add("ativo");

          // Carregar conteúdo da base
          const formData = new FormData();
          formData.append("arquivo", nome);

          try {
            const res = await fetch("/carregar_base", {
              method: "POST",
              body: formData
            });

            const text = await res.text();
            const data = JSON.parse(text);
            bottomPanel.innerHTML = `<pre>${data.result}</pre>`;
          } catch (err) {
            bottomPanel.innerHTML = `<pre>Erro ao carregar base: ${err}</pre>`;
          }
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

// --------------------- Lista da sidebar é atualizada automaticamente com arquivo adicionado
document.getElementById("csvInput").addEventListener("change", async function () {
  const file = this.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("arquivo_csv", file);

  try {
    const res = await fetch("/upload_csv", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    bottomPanel.innerHTML = `<pre>${data.result}</pre>`;

    // Recarrega a lista de arquivos
    carregarArquivos();

  } catch (err) {
    bottomPanel.innerHTML = `<pre>Erro ao enviar arquivo: ${err}</pre>`;
  }
});


// Alternar painéis da barra lateral ao clicar nos ícones
document.querySelectorAll('.icon-button').forEach(button => {
      button.addEventListener('click', () => {
        const targetId = button.getAttribute('data-target');

        // Marcar botão ativo
        document.querySelectorAll('.icon-button').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        // Alternar painéis
        document.querySelectorAll('.sidebar-content').forEach(painel => {
          if (painel.id === targetId) {
            painel.classList.add('active');
            painel.style.display = 'block';
          } else {
            painel.classList.remove('active');
            painel.style.display = 'none';
          }
        });

        // Expandir sidebar se estiver colapsada
        document.getElementById('sidebar').classList.remove('collapsed');
      });
  });



 // Exportar conteúdo do log
document.getElementById('saveBtn').addEventListener('click', function(e) {
  e.preventDefault();

  const terminalElement = document.getElementById('bottomPanel');
  if (!terminalElement) {
    console.log("Elemento bottomPanel não encontrado");
    return;
  }

  const linhas = terminalElement.innerText.split('\n');

  const linhasFiltradas = linhas
    .map(line => line.trim())
    .filter(line => {
      if (!line) return false;
      if (line.toLowerCase() === "none") return false;
      if (/^\d+\s+resultado\(s\)\s+encontrado\(s\)/i.test(line)) return false;
      return true;
    });

  if (linhasFiltradas.length === 0) {
    alert("Nenhum dado encontrado para salvar.");
    return;
  }

  const csvData = linhasFiltradas.map((line, index) => {
    // Se for o cabeçalho (primeira linha), separa por qualquer espaço(s)
    const parts = index === 0
      ? line.split(/\s+/)
      : line.split(/\s{2,}/);

    // Aspas para campos com vírgulas
    return parts.map(part => {
      const trimmed = part.trim();
      return trimmed.includes(',') ? `"${trimmed}"` : trimmed;
    }).join(',');
  });

  const csvContent = csvData.join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const fileName = prompt("Digite o nome do arquivo para salvar (com extensão .csv):", "terminal_output.csv");
  if (!fileName) {
    URL.revokeObjectURL(url);
    return;
  }

  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  link.style.display = 'none';

  document.body.appendChild(link);
  link.click();

  document.body.removeChild(link);
  URL.revokeObjectURL(url);
});








// Carrega os arquivos ao iniciar
carregarArquivos();
