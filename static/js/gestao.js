document.addEventListener('DOMContentLoaded', () => {
    loadDuplas();
    loadMetas();

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

        if (confirm(`Tem certeza que deseja deletar permanentemente ${ids.length} inscrições?`)) {
            try {
                const res = await fetch('/api/duplas/delete/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ids: ids })
                });
                const data = await res.json();
                if (data.success) {
                    loadDuplas();
                    document.getElementById('selectAll').checked = false;
                    updateDeleteBtn();
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
});

async function loadDuplas() {
    try {
        const res = await fetch('/api/duplas/');
        const data = await res.json();
        const tbody = document.getElementById('duplasTbody');
        tbody.innerHTML = '';

        data.duplas.forEach(dupla => {
            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid var(--border-color)';
            
            const statusClass = dupla.status_pagamento === 'Confirmado' ? 'status-confirmado' : 'status-pendente';
            const j2 = dupla.j2 && dupla.j2.trim() !== '' ? dupla.j2 : 'Sem parceiro';
            const loja = dupla.loja ? dupla.loja : 'Não Informado';
            const potencia = dupla.potencia ? dupla.potencia : 'Não Informado';
            const origemIcon = dupla.origem === 'Manual' ? '<i class="fa-solid fa-pen-nib" style="color: #d2a8ff;" title="Ficha Manual"></i> Manual' : '<i class="fa-solid fa-laptop-code" style="color: #79c0ff;" title="Eletrônico"></i> Eletrônico';
            
            row.innerHTML = `
                <td style="padding: 12px;">
                    <input type="checkbox" class="row-checkbox custom-checkbox dupla-check" value="${dupla.id}" onchange="updateDeleteBtn()">
                </td>
                <td style="padding: 12px; font-weight: 500; color: #8b949e;">#${dupla.id}</td>
                <td style="padding: 12px;">
                    <div style="font-weight: 500; color: #e6edf3;">${dupla.j1}</div>
                    <div style="font-size: 12px; color: #8b949e; margin-top: 2px;">& ${j2}</div>
                </td>
                <td style="padding: 12px;">
                    <div style="color: #e6edf3;">${loja}</div>
                    <div style="font-size: 11px; color: #8b949e; margin-top: 2px;">${potencia}</div>
                </td>
                <td style="padding: 12px; font-size: 12px;">
                    ${origemIcon}
                </td>
                <td style="padding: 12px;"><span class="status-badge ${statusClass}">${dupla.status_pagamento}</span></td>
                <td style="padding: 12px;">
                    ${dupla.valido ? '<span style="color:var(--success)"><i class="fa-solid fa-check"></i> Real</span>' : '<span style="color:#ef4444"><i class="fa-solid fa-flask"></i> Teste</span>'}
                </td>
                <td style="padding: 12px;">
                    <div class="table-actions">
                        <button class="btn btn-sm btn-primary" onclick="openEditModal(${dupla.id})" title="Editar Cadastro" style="margin-right: 5px;">
                            <i class="fa-solid fa-pen"></i>
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="togglePagamento(${dupla.id}, '${dupla.status_pagamento}')">
                            <i class="fa-solid fa-money-bill-wave"></i> $
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="toggleValido(${dupla.id}, ${dupla.valido})" title="Marcar como Teste/Real">
                            <i class="fa-solid fa-flask"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadMetas() {
    try {
        const res = await fetch('/api/metas/');
        const data = await res.json();
        const list = document.getElementById('metasList');
        const selectPotencia = document.getElementById('metaPotencia');
        list.innerHTML = '';
        
        if (selectPotencia) {
            selectPotencia.innerHTML = '<option value="" disabled selected>Selecione a Potência...</option>';
        }
        
        data.metas.forEach(m => {
            if (selectPotencia) {
                const option = document.createElement('option');
                option.value = m.potencia;
                option.text = m.potencia;
                selectPotencia.appendChild(option);
            }
            
            list.innerHTML += `
                <div class="meta-list-item">
                    <div>
                        <strong>${m.potencia}</strong> <span style="color:var(--text-secondary); margin-left:10px;">Meta: ${m.meta}</span>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="deleteMeta(${m.id})"><i class="fa-solid fa-trash"></i></button>
                </div>
            `;
        });
    } catch (e) { console.error(e); }
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
    payload.id = id;
    try {
        const res = await fetch('/api/duplas/update/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            loadDuplas();
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

// ================= Modal Edit =================

let cachedPotencias = [];

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
            document.getElementById('editId').value = data.dupla.id;
            
            document.getElementById('editNome1').value = data.dupla.nome_jogador1;
            document.getElementById('editApelido1').value = data.dupla.apelido_jogador1;
            document.getElementById('editCim1').value = data.dupla.cim_jogador1;
            document.getElementById('editIdade1').value = data.dupla.idade_jogador1;
            document.getElementById('editProf1').value = d.profissao_jogador1;
            document.getElementById('editTel1').value = d.telefone_jogador1;
            document.getElementById('editEmail1').value = d.email_jogador1;
            document.getElementById('editLoja1').value = d.loja_jogador1;
            populateSelect('editPot1', d.potencia_jogador1_id);
            
            document.getElementById('editNome2').value = data.dupla.nome_jogador2;
            document.getElementById('editApelido2').value = data.dupla.apelido_jogador2;
            document.getElementById('editCim2').value = data.dupla.cim_jogador2;
            document.getElementById('editIdade2').value = data.dupla.idade_jogador2;
            document.getElementById('editProf2').value = d.profissao_jogador2;
            document.getElementById('editTel2').value = d.telefone_jogador2;
            document.getElementById('editEmail2').value = d.email_jogador2;
            document.getElementById('editLoja2').value = d.loja_jogador2;
            populateSelect('editPot2', d.potencia_jogador2_id);
            
            document.getElementById('editAcompAdultos').value = d.acompanhantes_adultos;
            document.getElementById('editAcompCriancas').value = d.acompanhantes_criancas;
            
            document.getElementById('editOrigem').value = d.origem;
            document.getElementById('editPagamento').value = d.status_pagamento;
            document.getElementById('editValido').checked = d.valido;
            
            document.getElementById('editModal').style.display = 'block';
        } else {
            alert('Erro ao carregar dados: ' + data.error);
        }
    } catch (e) { alert(e); }
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

document.getElementById('formEditDupla').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        id: document.getElementById('editId').value,
        nome_jogador1: document.getElementById('editNome1').value,
        apelido_jogador1: document.getElementById('editApelido1').value,
        cim_jogador1: document.getElementById('editCim1').value,
        idade_jogador1: document.getElementById('editIdade1').value,
        profissao_jogador1: document.getElementById('editProf1').value,
        telefone_jogador1: document.getElementById('editTel1').value,
        email_jogador1: document.getElementById('editEmail1').value,
        loja_jogador1: document.getElementById('editLoja1').value,
        potencia_jogador1_id: document.getElementById('editPot1').value,
        
        nome_jogador2: document.getElementById('editNome2').value,
        apelido_jogador2: document.getElementById('editApelido2').value,
        cim_jogador2: document.getElementById('editCim2').value,
        idade_jogador2: document.getElementById('editIdade2').value,
        profissao_jogador2: document.getElementById('editProf2').value,
        telefone_jogador2: document.getElementById('editTel2').value,
        email_jogador2: document.getElementById('editEmail2').value,
        loja_jogador2: document.getElementById('editLoja2').value,
        potencia_jogador2_id: document.getElementById('editPot2').value,
        
        acompanhantes_adultos: document.getElementById('editAcompAdultos').value,
        acompanhantes_criancas: document.getElementById('editAcompCriancas').value,
        
        origem: document.getElementById('editOrigem').value,
        status_pagamento: document.getElementById('editPagamento').value,
        valido: document.getElementById('editValido').checked
    };
    
    await updateDupla(payload.id, payload);
    closeEditModal();
});


document.addEventListener('DOMContentLoaded', () => {
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
                        alert('Sincroniza��o conclu�da!\nNovas inscri��es importadas: ' + data.inserted);
                        fetchDuplas();
                    } else {
                        alert('Erro ao sincronizar: ' + data.error);
                    }
                })
                .catch(err => {
                    alert('Erro na requisi��o.');
                    console.error(err);
                })
                .finally(() => {
                    btnSyncCSV.innerHTML = originalHTML;
                    btnSyncCSV.disabled = false;
                });
        });
    }
});
