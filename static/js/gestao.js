document.addEventListener('DOMContentLoaded', () => {
    // Initialize DataTables
    const table = $('#duplasTable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json',
        },
        // Desativamos a busca nativa para dar prioridade aos filtros SSR do Django (GET)
        searching: false, 
        pageLength: 25,
        ordering: true
    });

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
    payload.id = id;
    try {
        const res = await fetch('/api/duplas/update/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
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
            document.getElementById('editValido').checked = d.valido;
            
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
    if (editModalInstance) {
        editModalInstance.hide();
    }
});
