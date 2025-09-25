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

    // Se tem hash no input
    if (camera) {
      document.getElementById("mapa-frame").src = "/mapa?numero_camera=" + camera;
    } else if (hash) {
        // Faz a requisição para gerar o grafo
      const url = new URL("/hash_mapa", window.location.origin);
      url.searchParams.append("hash", hash);
      if (arquivoSelecionado) {
        url.searchParams.append("arquivo", arquivoSelecionado);
      }
      await fetch(url.toString());

      // Atualiza o iframe com "cache busting"
      const timestamp = new Date().getTime();
      document.getElementById("mapa-frame").src = "/static/mapas/mapa.html?t=" + timestamp;
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

          document.querySelectorAll(".arquivo-item").forEach(el => el.classList.remove("ativo"));
          li.classList.add("ativo");

          const statsVisivel = document.getElementById("stats-container").style.display === "block";
          if (statsVisivel) {
            try {
              await fetchDadosStats();
              atualizarGraficos('1M');
            } catch (err) {
              console.error("Erro ao carregar estatísticas:", err);
            }
          }


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


//-----------------------------------------------------------
// Alternar tema claro/escuro
document.getElementById("tema-escuro").addEventListener("click", () => {
  document.body.classList.remove("light-theme", "theme2077");
  document.body.classList.add("dark-theme");
});

document.getElementById("tema-claro").addEventListener("click", () => {
  document.body.classList.remove("dark-theme", "theme2077");
  document.body.classList.add("light-theme");
});

document.getElementById("tema-cyberpunk").addEventListener("click", () => {
  document.body.classList.remove("light-theme", "dark-theme");
  document.body.classList.add("theme2077");
});

// Salvar e restaurar tema
function aplicarTemaSalvo() {
  const tema = localStorage.getItem("tema");
  if (tema === "claro") {
    document.body.classList.add("light-theme");
  } else {
    document.body.classList.add("dark-theme");
  }
}

document.getElementById("tema-escuro").addEventListener("click", () => {
  document.body.classList.remove("light-theme");
  document.body.classList.add("dark-theme");
  localStorage.setItem("tema", "escuro");
});

document.getElementById("tema-claro").addEventListener("click", () => {
  document.body.classList.remove("dark-theme");
  document.body.classList.add("light-theme");
  localStorage.setItem("tema", "claro");
});

aplicarTemaSalvo(); // chama no início
//-----------------------------------------------------------


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



  // Carregar lista de relatorios
  async function carregarRelatorios() {
  try {
    const res = await fetch("/api/relatorios");
    const data = await res.json();

    const lista = document.getElementById("lista-relatorios");
    lista.innerHTML = "";

    if (data.relatorios.length === 0) {
      lista.innerHTML = "<p>Ainda não há relatórios.</p>";
      return;
    }

    data.relatorios.forEach(nome => {
      const li = document.createElement("li");
      li.textContent = nome;
      lista.appendChild(li);
    });

  } catch (err) {
    console.error("Erro ao buscar relatórios:", err);
  }
}document.querySelector('[data-target="painel-relatorios"]').addEventListener("click", carregarRelatorios);


// Mostrar resposta de pergunta em "Perguntas frequentes"
document.querySelectorAll('.faq-question').forEach(button => {
  button.addEventListener('click', () => {
    const answer = button.nextElementSibling;
    if (answer.classList.contains('active')) {
      // Fecha a resposta
      answer.classList.remove('active');
    } else {
      // Abre a resposta
      answer.classList.add('active');
    }
  });
});


//----------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const btnMapa = document.getElementById("btnMapa");
  const btnStats = document.getElementById("btnStats");
  const mapa = document.getElementById("mapa-container");
  const stats = document.getElementById("stats-container");
  const totalDadosEl = document.getElementById('totalDados');
  const totalTrajetosEl = document.getElementById('totalTrajetos'); // <--- novo elemento
  const timeButtons = document.querySelectorAll('.time-btn');

  let chartEstacoes, chartLinhas, chartRotas;
  let dadosEstacoes = [];  // dados vindos do backend
  let dadosLinhas = [];    // dados vindos do backend
  let rotasOk = 0;
  let rotasErros = 0;

  // Quando clicar no botão "Estatísticas"
  btnStats.addEventListener("click", () => {
    mapa.style.display = "none";
    stats.style.display = "block";
    btnStats.classList.add("active");
    btnMapa.classList.remove("active");
    fetchDadosStats().then(() => {
      // inicia com filtro padrão, por exemplo 1 mês
      atualizarGraficos('1M');
    }).catch(err => {
      console.error("Erro ao buscar estatísticas:", err);
    });
  });

  // Voltar para o mapa
  btnMapa.addEventListener("click", () => {
    mapa.style.display = "block";
    stats.style.display = "none";
    btnMapa.classList.add("active");
    btnStats.classList.remove("active");
  });

  // Evento para cada botão de filtro de tempo
  timeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      timeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const periodo = btn.dataset.range;
      atualizarGraficos(periodo);
    });
  });

  // Função que busca os dados reais do backend
  async function fetchDadosStats() {
    if (!arquivoSelecionado) {
      console.warn("Nenhuma base de dados selecionada para estatísticas.");
      return;
    }

    const url = `/stats?arquivo=${encodeURIComponent(arquivoSelecionado)}`;
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`HTTP error! status: ${resp.status}`);
    }
    const json = await resp.json();
    if (json.erro) {
      throw new Error(json.erro);
    }

    // Pega os dados
    const nomeDB = json.nomeDB; // pega o nome da DB do backend
    const total = json.total;
    const total_trajetos = json.total_trajetos; // <--- pega total de trajetos do backend
    const estacoes_por_dia = json.estacoes_por_dia; // array de { data, estacao, contagem }
    const linhas_por_dia = json.linhas_por_dia;
    rotasOk = json.rotas_ok;
    rotasErros = json.rotas_erros;

    // Atualiza elementos do cartão
    const nomeDBEl = document.getElementById('nomeDB');
    nomeDBEl.textContent = `DB: ${nomeDB}`;  // Atualiza o nome da DB
    totalDadosEl.textContent = `Total de Dados: ${total.toLocaleString()}`;
    totalTrajetosEl.textContent = `Total de Trajetos: ${total_trajetos.toLocaleString()}`;

    // Processar para gráficos: por exemplo somar todas estações por dia
    // Cria mapa data → soma de estações
    const mapaDiaEstacoes = {};
    estacoes_por_dia.forEach(item => {
      const d = item.data;
      if (!mapaDiaEstacoes[d]) mapaDiaEstacoes[d] = 0;
      mapaDiaEstacoes[d] += item.contagem;
    });
    // Ordem das datas
    const labelsEstacoes = Object.keys(mapaDiaEstacoes).sort();
    const valoresEstacoes = labelsEstacoes.map(d => mapaDiaEstacoes[d]);

    // Processar para linhas: separar cada linha, ou se quiser, somar
    // Cria objecto: {
    //   Azul: { data1: contagem, data2: contagem, ... },
    //   Vermelha: { ... },
    //   Verde: { ... }
    // }
    const objLinhas = {};
    linhas_por_dia.forEach(item => {
      const d = item.data;
      const linha = item.linha;
      const cont = item.contagem;
      if (!objLinhas[linha]) objLinhas[linha] = {};
      objLinhas[linha][d] = cont;
    });
    // Descobrir todas as datas que aparecem
    const todasDatasLinhas = Array.from(
      new Set(linhas_por_dia.map(item => item.data))
    ).sort();
    // Para cada linha, criar array de valores no mesmo order das datas
    const linhasNomes = Object.keys(objLinhas);
    const dadosPorLinha = {};
    linhasNomes.forEach(l => {
      dadosPorLinha[l] = todasDatasLinhas.map(d => objLinhas[l][d] || 0);
    });

    // Guardar em variáveis globais para usar no atualizarGrafico
    dadosEstacoes = {
      labels: labelsEstacoes,
      valores: valoresEstacoes
    };
    dadosLinhas = {
      labels: todasDatasLinhas,
      dados: dadosPorLinha
    };

    console.log("Estatísticas atualizadas:", dadosEstacoes, dadosLinhas);
  }

  // Função que atualiza/gera os gráficos com os dados reais
  function atualizarGraficos(periodo) {
    if (!dadosEstacoes.labels || dadosEstacoes.labels.length === 0) {
      // ainda não carregou os dados
      return;
    }

    // gerar labels no período escolhido
    const labelsPeriodo = filtrarLabels(dadosEstacoes.labels, periodo);
    const valoresPeriodoEstacoes = filtrarValores(dadosEstacoes.labels, dadosEstacoes.valores, periodo, labelsPeriodo);

    // Estações
    if (chartEstacoes) chartEstacoes.destroy();
    const ctxE = document.getElementById('graficoEstacoes').getContext('2d');
    chartEstacoes = new Chart(ctxE, {
      type: 'line',
      data: {
        labels: labelsPeriodo,
        datasets: [{
          label: 'Uso de estações por dia',
          data: valoresPeriodoEstacoes,
          borderColor: '#007bff',
          backgroundColor: 'rgba(0,123,255,0.2)',
          tension: 0.3,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

    // Linhas
    const labelsLinhasPeriodo = filtrarLabels(dadosLinhas.labels, periodo);
    if (chartLinhas) chartLinhas.destroy();
    const ctxL = document.getElementById('graficoLinhas').getContext('2d');
    const datasetsLinhas = Object.keys(dadosLinhas.dados).map(linha => {
      return {
        label: `Linha ${linha}`,
        data: filtrarValores(dadosLinhas.labels, dadosLinhas.dados[linha], periodo, labelsLinhasPeriodo),
        borderColor: escolherCorLinha(linha),
        fill: false,
        tension: 0.3
      };
    });
    chartLinhas = new Chart(ctxL, {
      type: 'line',
      data: {
        labels: labelsLinhasPeriodo,
        datasets: datasetsLinhas
      },
      options: {
        responsive: true,
        maintainAspectRatio: false
      }
    });

    // Pizza rotas
    if (chartRotas) chartRotas.destroy();
    const ctxR = document.getElementById('graficoRotas').getContext('2d');
    chartRotas = new Chart(ctxR, {
      type: 'pie',
      data: {
        labels: ['Rotas OK', 'Rotas com Erros'],
        datasets: [{
          data: [rotasOk, rotasErros],
          backgroundColor: ['#28a745', '#dc3545']
        }]
      },
      options: { responsive: true }
    });
  }

  // Auxiliares: filtrar labels & valores baseado no período
  function filtrarLabels(labelsAll, periodo) {
    const today = new Date();
    if (periodo === '1D') {
      return labelsAll.slice(-1);
    } else if (periodo === '7D') {
      return labelsAll.slice(-7);
    } else if (periodo === '1M') {
      return labelsAll.slice(-30);
    } else if (periodo === '1Y') {
      return labelsAll.slice(-365).filter((v,i) => {
        const dt = new Date(v);
        return dt.getDate() === 1;
      });
    } else { // MAX
      return labelsAll;
    }
  }

  function filtrarValores(labelsAll, valoresAll, periodo, labelsPeriodo) {
    const idxMap = {};
    labelsAll.forEach((lab, idx) => idxMap[lab] = idx);
    return labelsPeriodo.map(lab => {
      const idx = idxMap[lab];
      return idx !== undefined ? valoresAll[idx] : 0;
    });
  }

  // Escolher cor dependendo do nome da linha
  function escolherCorLinha(linhaNome) {
    const nm = linhaNome.toLowerCase();
    if (nm.includes('azul')) return '#007bff';
    if (nm.includes('vermelha')) return '#dc3545';
    if (nm.includes('verde')) return '#28a745';
    return '#6c757d';
  }
});


//----------------------------------------------------------------------------------------------------
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