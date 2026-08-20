document.addEventListener('DOMContentLoaded', () => {
    // Initialize DataTables
    const table = $('#duplasTable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json',
        },
        // Desativamos a busca nativa para dar prioridade aos filtros SSR do Django (GET)
        searching: false, 
        pageLength: 25,
        ordering: true,
        stateSave: true,
        order: [[7, 'asc']]
    });

    loadMetas();
    loadMetricsCards();

    // Checkbox master (Select all)
    document.getElementById('selectAll').addEventListener('change', (e) => {
        const checkboxes = document.querySelectorAll('.dupla-check');
        checkboxes.forEach(cb => cb.checked = e.target.checked);
        updateDeleteBtn();
    });

    // Bulk Delete
    document.getElementById('btnDeleteSelected').addEventListener('click', async () => {
        const checkboxes = document.querySelectorAll('.dupla-check:checked');
        const ids = Array.from(checkboxes).map(cb => cb.value);
        if (ids.length === 0) return;

        if (confirm(`Tem certeza que deseja deletar permanentemente ${ids.length} inscri\u00e7\u00f5es?`)) {
            try {
                const res = await fetch('/api/duplas/delete/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: ids })
                });
                const data = await res.json();
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Erro ao deletar: ' + data.error);
                }
            } catch (err) { alert(err); }
        }
    });

    // Add Meta
    document.getElementById('formMeta').addEventListener('submit', async (e) => {
        e.preventDefault();
        const potencia = document.getElementById('metaPotencia').value;
        const qtd = document.getElementById('metaQtd').value;

        try {
            const res = await fetch('/api/metas/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ potencia: potencia, meta_quantidade: qtd })
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById('metaPotencia').value = '';
                document.getElementById('metaQtd').value = '';
                loadMetas();
            } else {
                alert('Erro ao salvar meta: ' + data.error);
            }
        } catch (err) { alert(err); }
    });

    // Sync CSV
    const btnSyncCSV = document.getElementById('btnSyncCSV');
    if (btnSyncCSV) {
        btnSyncCSV.addEventListener('click', () => {
            const originalHTML = btnSyncCSV.innerHTML;
            btnSyncCSV.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sincronizando...';
            btnSyncCSV.disabled = true;
            
            fetch('/api/duplas/sync_csv/', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        alert('Sincroniza\u00e7\u00e3o conclu\u00edda!\nNovas inscri\u00e7\u00f5es importadas: ' + data.inserted);
                        window.location.reload();
                    } else {
                        alert('Erro ao sincronizar: ' + data.error);
                    }
                })
                .catch(err => {
                    alert('Erro na requisi\u00e7\u00e3o.');
                    console.error(err);
                })
                .finally(() => {
                    btnSyncCSV.innerHTML = originalHTML;
                    btnSyncCSV.disabled = false;
                });
        });
    }
});

async function loadMetas() {
    try {
        const res = await fetch('/api/metas/');
        const data = await res.json();
        const list = document.getElementById('metasList');
        list.innerHTML = '';
        
        data.metas.forEach(m => {
            list.innerHTML += `
                <div class="meta-list-item">
                    <div class="d-flex align-items-center flex-grow-1">
                        <strong>${m.potencia}</strong> 
                        <span class="text-muted ms-3 me-2">Meta:</span>
                        <input type="number" class="form-control form-control-sm bg-dark text-light border-secondary" style="width: 80px;" value="${m.meta}" onchange="updateMeta('${m.potencia}', this.value)">
                    </div>
                    <button class="btn btn-sm btn-outline-danger border-0 ms-2" onclick="deleteMeta(${m.id})"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;
        });
    } catch (e) { console.error(e); }
}

async function loadMetricsCards() {
    try {
        const res = await fetch('/api/metrics/');
        const data = await res.json();
        
        
        // Auditoria da Tríade
        if (data.triade) {
            const setSafe = (id, val) => { const el = document.getElementById(id); if(el) el.innerText = val; };
            setSafe('triadeDuplasTotal', data.triade.duplas.total);
            setSafe('triadeDuplasCompletas', data.triade.duplas.completas);
            setSafe('triadeDuplasSemComp', data.triade.duplas.sem_comprovante);
            setSafe('triadeDuplasSemFicha', data.triade.duplas.manuais_sem_ficha);

            setSafe('triadeComprovantesTotal', data.triade.comprovantes.total);
            setSafe('triadeComprovantesVinc', data.triade.comprovantes.vinculados);
            setSafe('triadeComprovantesOrf', data.triade.comprovantes.orfaos);

            setSafe('triadeFichasTotal', data.triade.fichas.total);
            setSafe('triadeFichasVinc', data.triade.fichas.vinculados);
            setSafe('triadeFichasOrf', data.triade.fichas.orfaos);
        }

        const totalInscritos = document.getElementById('totalInscritos');
        const totalConfirmados = document.getElementById('totalConfirmados');
        const totalManual = document.getElementById('totalManual');
        const confirmadosManual = document.getElementById('confirmadosManual');
        const totalEletronico = document.getElementById('totalEletronico');
        const confirmadosEletronico = document.getElementById('confirmadosEletronico');

        if(totalInscritos) totalInscritos.innerText = data.total;
        if(totalConfirmados) totalConfirmados.innerText = data.confirmados;
        
        if(totalManual) totalManual.innerText = data.total_manual;
        if(confirmadosManual) confirmadosManual.innerText = data.confirmados_manual;
        
        if(totalEletronico) totalEletronico.innerText = data.total_eletronico;
        if(confirmadosEletronico) confirmadosEletronico.innerText = data.confirmados_eletronico;
        
    } catch (e) {
        console.error("Erro ao carregar os cards do dashboard:", e);
    }
}

async function updateMeta(potencia, value) {
    try {
        const res = await fetch('/api/metas/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ potencia: potencia, meta_quantidade: value })
        });
        const data = await res.json();
        if (!data.success) {
            alert('Erro ao atualizar meta: ' + data.error);
            loadMetas();
        }
    } catch (e) { alert(e); }
}

function updateDeleteBtn() {
    const count = document.querySelectorAll('.dupla-check:checked').length;
    const btn = document.getElementById('btnDeleteSelected');
    document.getElementById('selectedCount').innerText = count;
    btn.style.display = count > 0 ? 'inline-block' : 'none';
}

async function togglePagamento(id, currentStatus) {
    const newStatus = currentStatus === 'Confirmado' ? 'Pendente' : 'Confirmado';
    await updateDupla(id, { status_pagamento: newStatus });
}

async function toggleValido(id, currentValido) {
    await updateDupla(id, { valido: !currentValido });
}

async function updateDupla(id, payload) {
    const isFormData = payload instanceof FormData;
    if (isFormData) {
        payload.append('id', id);
    } else {
        payload.id = id;
    }
    
    try {
        const res = await fetch('/api/duplas/update/', {
            method: 'POST',
            headers: isFormData ? {} : { 'Content-Type': 'application/json' },
            body: isFormData ? payload : JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            window.location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    } catch (e) { alert(e); }
}

async function deleteMeta(id) {
    if (confirm('Deletar esta meta?')) {
        try {
            const res = await fetch('/api/metas/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'delete', id: id })
            });
            const data = await res.json();
            if (data.success) {
                loadMetas();
            }
        } catch (e) { alert(e); }
    }
}

// ================= Modal Edit Bootstrap =================
let cachedPotencias = [];
let editModalInstance = null;

async function getPotencias() {
    if (cachedPotencias.length > 0) return cachedPotencias;
    const res = await fetch('/api/metas/');
    const data = await res.json();
    cachedPotencias = data.metas;
    return cachedPotencias;
}

function populateSelect(selectId, selectedValue) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">-- Selecione (Opcional) --</option>';
    cachedPotencias.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.text = p.potencia;
        if (p.id == selectedValue) option.selected = true;
        select.appendChild(option);
    });
}

async function openEditModal(id) {
    await getPotencias();
    
    try {
        const res = await fetch(`/api/duplas/${id}/`);
        const data = await res.json();
        
        if (data.success) {
            const d = data.dupla;
            document.getElementById('editId').value = d.id;
            
            document.getElementById('editNome1').value = d.nome_jogador1;
            document.getElementById('editApelido1').value = d.apelido_jogador1;
            document.getElementById('editCim1').value = d.cim_jogador1;
            document.getElementById('editIdade1').value = d.idade_jogador1;
            document.getElementById('editProf1').value = d.profissao_jogador1;
            document.getElementById('editTel1').value = d.telefone_jogador1;
            document.getElementById('editEmail1').value = d.email_jogador1;
            document.getElementById('editLoja1').value = d.loja_jogador1;
            populateSelect('editPot1', d.potencia_jogador1_id);
            
            document.getElementById('editNome2').value = d.nome_jogador2;
            document.getElementById('editApelido2').value = d.apelido_jogador2;
            document.getElementById('editCim2').value = d.cim_jogador2;
            document.getElementById('editIdade2').value = d.idade_jogador2;
            document.getElementById('editProf2').value = d.profissao_jogador2;
            document.getElementById('editTel2').value = d.telefone_jogador2;
            document.getElementById('editEmail2').value = d.email_jogador2;
            document.getElementById('editLoja2').value = d.loja_jogador2;
            populateSelect('editPot2', d.potencia_jogador2_id);
            
            document.getElementById('editAcompAdultos').value = d.acompanhantes_adultos;
            document.getElementById('editAcompCriancas').value = d.acompanhantes_criancas;
            
            document.getElementById('editOrigem').value = d.origem;
            document.getElementById('editPagamento').value = d.status_pagamento;
            document.getElementById('editValido').value = d.status_inscricao;
            
            document.getElementById('editComprovante').value = '';
            if (d.comprovante_url) {
                document.getElementById('comprovanteStatus').innerHTML = `Comprovante atual: <a href="${d.comprovante_url}" target="_blank" class="text-info">Visualizar Arquivo</a>`;
            } else {
                document.getElementById('comprovanteStatus').innerHTML = 'Nenhum comprovante anexado.';
            }
            document.getElementById('editDataPagamento').value = d.data_pagamento || '';

            document.getElementById('editFicha').value = '';
            const blocoFicha = document.getElementById('blocoFichaInscricao');
            if (d.origem === 'Manual') {
                blocoFicha.style.display = 'block';
                if (d.ficha_url) {
                    document.getElementById('fichaStatus').innerHTML = `Ficha atual: <a href="${d.ficha_url}" target="_blank" class="text-info">Visualizar Arquivo</a>`;
                } else {
                    document.getElementById('fichaStatus').innerHTML = 'Nenhuma ficha anexada.';
                }
            } else {
                blocoFicha.style.display = 'none';
            }
            
            // Adicionar evento para quando a origem mudar no select
            document.getElementById('editOrigem').onchange = function() {
                blocoFicha.style.display = this.value === 'Manual' ? 'block' : 'none';
            };
            
            if (!editModalInstance) {
                editModalInstance = new bootstrap.Modal(document.getElementById('editModal'));
            }
            editModalInstance.show();
        } else {
            alert('Erro ao carregar dados: ' + data.error);
        }
    } catch (e) { alert(e); }
}

document.getElementById('formEditDupla').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('id', document.getElementById('editId').value);
    formData.append('nome_jogador1', document.getElementById('editNome1').value);
    formData.append('apelido_jogador1', document.getElementById('editApelido1').value);
    formData.append('cim_jogador1', document.getElementById('editCim1').value);
    formData.append('idade_jogador1', document.getElementById('editIdade1').value);
    formData.append('profissao_jogador1', document.getElementById('editProf1').value);
    formData.append('telefone_jogador1', document.getElementById('editTel1').value);
    formData.append('email_jogador1', document.getElementById('editEmail1').value);
    formData.append('loja_jogador1', document.getElementById('editLoja1').value);
    formData.append('potencia_jogador1_id', document.getElementById('editPot1').value);
    
    formData.append('nome_jogador2', document.getElementById('editNome2').value);
    formData.append('apelido_jogador2', document.getElementById('editApelido2').value);
    formData.append('cim_jogador2', document.getElementById('editCim2').value);
    formData.append('idade_jogador2', document.getElementById('editIdade2').value);
    formData.append('profissao_jogador2', document.getElementById('editProf2').value);
    formData.append('telefone_jogador2', document.getElementById('editTel2').value);
    formData.append('email_jogador2', document.getElementById('editEmail2').value);
    formData.append('loja_jogador2', document.getElementById('editLoja2').value);
    formData.append('potencia_jogador2_id', document.getElementById('editPot2').value);
    
    formData.append('acompanhantes_adultos', document.getElementById('editAcompAdultos').value);
    formData.append('acompanhantes_criancas', document.getElementById('editAcompCriancas').value);
    
    formData.append('origem', document.getElementById('editOrigem').value);
    formData.append('status_pagamento', document.getElementById('editPagamento').value);
    formData.append('status_inscricao', document.getElementById('editValido').value);
    formData.append('data_pagamento', document.getElementById('editDataPagamento').value);
    
    const fileInput = document.getElementById('editComprovante');
    if (fileInput.files.length > 0) {
        formData.append('comprovante', fileInput.files[0]);
    }
    
    const fichaInput = document.getElementById('editFicha');
    if (fichaInput && fichaInput.files.length > 0) {
        formData.append('ficha_inscricao', fichaInput.files[0]);
    }
    
    await updateDupla(formData.get('id'), formData);
    if (editModalInstance) {
        editModalInstance.hide();
    }
});

let compModalInstance = null;
async function openComprovanteModal(id, url) {
    if (!compModalInstance) {
        compModalInstance = new bootstrap.Modal(document.getElementById('comprovanteModal'));
    }
    const container = document.getElementById('comprovanteContainer');
    const downloadBtn = document.getElementById('comprovanteDownloadBtn');
    
    downloadBtn.href = url;
    
    if (url.toLowerCase().endsWith('.pdf')) {
        container.style.display = 'block';
        container.style.padding = '0';
        container.style.height = '100%';
        container.innerHTML = `<iframe src="${url}" style="width: 100%; height: 100%; border: none; display: block;"></iframe>`;
    } else {
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.justifyContent = 'center';
        container.style.padding = '15px';
        container.innerHTML = `<img src="${url}" alt="Comprovante" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
    }
    
    // Ocultar alerta
    document.getElementById('financeiroSuccessAlert').classList.add('d-none');
    
    // Carregar dados financeiros
    try {
        const res = await fetch(`/api/duplas/${id}/`);
        const data = await res.json();
        if (data.success) {
            const d = data.dupla;
            document.getElementById('financeiroDuplaId').value = id;
            document.getElementById('financeiroStatus').value = d.status_pagamento;
            document.getElementById('financeiroData').value = d.data_pagamento;
            document.getElementById('financeiroPagador').value = d.pagador_comprovante;
            document.getElementById('financeiroBanco').value = d.banco_comprovante;
            document.getElementById('financeiroDoc').value = d.documento_comprovante;
            
            const chkValido = document.getElementById('financeiroValido');
            const lblValido = document.getElementById('financeiroValidoLabel');
            chkValido.value = d.status_inscricao;
            if(d.status_inscricao === 'Validada' || d.status_inscricao === 'Inscrita') {
                lblValido.className = 'form-check-label text-vivid-green fw-bold';
                lblValido.innerText = 'Inscrição Aprovada';
            } else {
                lblValido.className = 'form-check-label text-warning fw-bold';
                lblValido.innerText = 'Aprovar Inscrição?';
            }
        }
    } catch (e) {
        console.error("Erro ao buscar dupla:", e);
    }
    
    compModalInstance.show();
}

document.getElementById('financeiroValido').addEventListener('change', (e) => {
    const lbl = document.getElementById('financeiroValidoLabel');
    const val = e.target.value;
    if(val === 'Validada' || val === 'Inscrita') {
        lbl.className = 'form-check-label text-vivid-green fw-bold';
    } else {
        lbl.className = 'form-check-label text-warning fw-bold';
    }
});

document.getElementById('formFinanceiroModal').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('financeiroDuplaId').value;
    const payload = {
        id: id,
        status_pagamento: document.getElementById('financeiroStatus').value,
        data_pagamento: document.getElementById('financeiroData').value,
        pagador_comprovante: document.getElementById('financeiroPagador').value,
        banco_comprovante: document.getElementById('financeiroBanco').value,
        documento_comprovante: document.getElementById('financeiroDoc').value,
        status_inscricao: document.getElementById('financeiroValido').value
    };
    
    try {
        const res = await fetch('/api/duplas/update/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            const alertBox = document.getElementById('financeiroSuccessAlert');
            alertBox.classList.remove('d-none');
            setTimeout(() => {
                alertBox.classList.add('d-none');
            }, 3000);
            
            // Atualizar o badge na tabela
            const checkbox = document.querySelector(`input.dupla-check[value="${id}"]`);
            if (checkbox) {
                const tr = checkbox.closest('tr');
                if (tr) {
                    const statusBadge = tr.querySelector('.status-badge');
                    if (statusBadge) {
                        if (payload.status_pagamento === 'Confirmado') {
                            statusBadge.className = 'status-badge status-confirmado';
                            statusBadge.innerHTML = '<i class="fa-solid fa-check-circle"></i> Confirmado';
                        } else {
                            statusBadge.className = 'status-badge status-pendente';
                            statusBadge.innerHTML = '<i class="fa-solid fa-clock"></i> Pendente';
                        }
                    }
                    
                    setTimeout(() => location.reload(), 500);
                }
            }
        } else {
            alert('Erro: ' + data.error);
        }
    } catch (err) { alert(err); }
});
