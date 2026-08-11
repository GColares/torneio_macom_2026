let barChart = null;
let pieChart = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();

    // Export PDF Event Listener
    document.getElementById('exportPdfBtn').addEventListener('click', () => {
        const chartCanvas = document.getElementById('potenciaPieChart');
        if (chartCanvas && pieChart) {
            // MUDA A COR PARA PRETO ANTES DE TIRAR A FOTO PARA O PDF
            pieChart.options.plugins.legend.labels.color = '#000000';
            pieChart.update('none'); // Update sem animação
            
            const img = document.createElement('img');
            img.src = chartCanvas.toDataURL('image/png');
            img.id = 'printChartImg';
            img.style.maxWidth = '100%';
            img.style.maxHeight = '280px'; 
            img.style.objectFit = 'contain'; // Impede achatamento (efeito oval)
            img.style.display = 'block';
            img.style.margin = '0 auto';
            
            chartCanvas.style.display = 'none';
            chartCanvas.parentNode.insertBefore(img, chartCanvas);
            
            window.print();
            
            // Restaura o canvas interativo e a cor clara após a impressão
            setTimeout(() => {
                const tempImg = document.getElementById('printChartImg');
                if (tempImg) tempImg.remove();
                chartCanvas.style.display = 'block';
                pieChart.options.plugins.legend.labels.color = '#e6edf3';
                pieChart.update('none');
            }, 500);
        } else {
            window.print();
        }
    });

    // Refresh Event Listener
    document.getElementById('refreshBtn').addEventListener('click', () => {
        const btn = document.getElementById('refreshBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sincronizando...';
        btn.disabled = true;
        
        // Primeiro sincroniza o CSV, depois atualiza os gráficos
        fetch('/api/duplas/sync_csv/', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if(data.success && data.inserted > 0) {
                    alert(`Sincronização do Google Forms concluída! ${data.inserted} novas inscrições encontradas.`);
                }
            })
            .catch(err => console.error("Erro ao sincronizar CSV:", err))
            .finally(() => {
                fetchDashboardData().finally(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                });
            });
    });
});

function fetchDashboardData() {
    return fetch('/api/metrics/')
        .then(response => {
            if (!response.ok) throw new Error('Falha ao conectar com o servidor local.');
            return response.json();
        })
        .then(data => {
            updateMetrics(data);
            updateMetas(data.potencia);
            updatePieChart(data.potencia);
            updateTabelas(data.tabela_duplas, data.tabela_jogadores);
        })
        .catch(error => {
            document.getElementById('errorAlert').style.display = 'block';
            document.getElementById('errorText').innerText = error.message;
        });
}

function updateMetrics(data) {
    document.getElementById('totalInscritos').innerText = data.total || 0;
    document.getElementById('totalConfirmados').innerText = data.confirmados || 0;
    
    document.getElementById('totalManual').innerText = data.total_manual || 0;
    document.getElementById('confirmadosManual').innerText = data.confirmados_manual || 0;
    
    document.getElementById('totalEletronico').innerText = data.total_eletronico || 0;
    document.getElementById('confirmadosEletronico').innerText = data.confirmados_eletronico || 0;
    
    document.getElementById('fileNameDisplay').innerText = data.file_name || 'Desconhecido';
}

function updateMetas(potenciasRealizadas) {
    const container = document.getElementById('metasContainer');
    const gridAbsoluto = document.getElementById('metaGridAbsoluto');
    
    container.style.display = 'flex';
    gridAbsoluto.innerHTML = '';
    
    const metaFixa = 30; // Conforme solicitado
    
    Object.keys(potenciasRealizadas).forEach(potencia => {
        const realizado = potenciasRealizadas[potencia] || 0;
        const porcentagem = Math.min(100, Math.round((realizado / metaFixa) * 100));
        
        // --- Gráfico 1: Valores Absolutos ---
        const itemAbsoluto = document.createElement('div');
        itemAbsoluto.className = 'meta-item';
        itemAbsoluto.innerHTML = `
            <div class="meta-header" style="margin-bottom: 8px; display: flex; flex-direction: column;">
                <span class="meta-title" style="margin-bottom: 4px;">${potencia}</span>
                <span style="font-weight: 600; font-size: 13px; color: var(--text-primary);">${realizado} duplas</span>
            </div>
            <div class="meta-progress-bar">
                <div class="meta-progress-fill" style="width: ${porcentagem}%;"></div>
            </div>
        `;
        gridAbsoluto.appendChild(itemAbsoluto);
    });
}

function updatePieChart(potenciaData) {
    const labels = Object.keys(potenciaData);
    const data = Object.values(potenciaData);

    const bgColors = [
        'rgba(197, 160, 89, 0.85)',   // Classic Gold
        'rgba(114, 47, 55, 0.85)',    // Burgundy/Wine
        'rgba(44, 62, 80, 0.85)'      // Deep Navy
    ];
    const borderColors = bgColors.map(color => color.replace('0.85', '1'));

    Chart.defaults.color = '#8b949e';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.register(ChartDataLabels);

    const pieCtx = document.getElementById('potenciaPieChart').getContext('2d');
    if (pieChart) pieChart.destroy();
    
    pieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: bgColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: { 
                    position: 'bottom',
                    align: 'start',
                    labels: { 
                        color: '#e6edf3', // Claro para a tela escura
                        font: { size: 12 }, 
                        padding: 10,
                        boxWidth: 12
                    }
                },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 14 },
                    formatter: (value, ctx) => {
                        let sum = 0;
                        let dataArr = ctx.chart.data.datasets[0].data;
                        dataArr.map(data => { sum += data; });
                        if (sum === 0) return '0%';
                        let percentage = (value * 100 / sum).toFixed(0) + "%";
                        return value > 0 ? percentage : '';
                    }
                }
            }
        }
    });
}

function updateTabelas(tabelaDuplas, tabelaJogadores) {
    // Ordenar ambas as tabelas (maior quantidade primeiro)
    tabelaDuplas.sort((a, b) => b.quantidade - a.quantidade);
    tabelaJogadores.sort((a, b) => b.quantidade - a.quantidade);
    
    const tbodyDuplas = document.getElementById('tabelaDuplasBody');
    tbodyDuplas.innerHTML = '';
    tabelaDuplas.forEach(row => {
        tbodyDuplas.innerHTML += `
            <tr>
                <td><strong>${row.potencia}</strong></td>
                <td>${row.loja}</td>
                <td><strong>${row.quantidade}</strong></td>
            </tr>
        `;
    });
    
    const tbodyJogadores = document.getElementById('tabelaJogadoresBody');
    tbodyJogadores.innerHTML = '';
    tabelaJogadores.forEach(row => {
        let duplasHtml = row.nomes_duplas.map(d => `<li>${d}</li>`).join('');
        tbodyJogadores.innerHTML += `
            <tr>
                <td><strong>${row.potencia}</strong></td>
                <td>${row.loja}</td>
                <td>
                    <ul style="list-style-type: disc; margin-left: 20px; color:var(--text-secondary);">
                        ${duplasHtml}
                    </ul>
                </td>
            </tr>
        `;
    });
}

// Chart.js removido conforme solicitado para adoção do modelo de barras CSS puras.
