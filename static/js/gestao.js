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

        data.duplas.forEach(d => {
            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid var(--border-color)';
            
            const trClass = d.valido ? '' : 'style="opacity: 0.5;"';
            const statusClass = d.status_pagamento === 'Confirmado' ? 'status-confirmado' : 'status-pendente';
            const j2 = d.j2 ? d.j2 : '<span style="color:#666">Sem parceiro</span>';

            row.innerHTML = `
                <td style="padding: 12px;"><input type="checkbox" class="custom-checkbox dupla-check" value="${d.id}" onchange="updateDeleteBtn()"></td>
                <td style="padding: 12px; color:var(--text-secondary)">#${d.id}</td>
                <td style="padding: 12px;"><strong>${d.j1}</strong><br><small>${j2}</small></td>
                <td style="padding: 12px;">${d.loja}<br><small style="color:var(--text-secondary)">${d.potencia}</small></td>
                <td style="padding: 12px;"><span class="status-badge ${statusClass}">${d.status_pagamento}</span></td>
                <td style="padding: 12px;">
                    ${d.valido ? '<span style="color:var(--success)"><i class="fa-solid fa-check"></i> Real</span>' : '<span style="color:#ef4444"><i class="fa-solid fa-flask"></i> Teste</span>'}
                </td>
                <td style="padding: 12px;">
                    <div class="table-actions">
                        <button class="btn btn-sm btn-outline" onclick="togglePagamento(${d.id}, '${d.status_pagamento}')">
                            <i class="fa-solid fa-money-bill-wave"></i> $
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="toggleValido(${d.id}, ${d.valido})" title="Marcar como Teste/Real">
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
        list.innerHTML = '';

        data.metas.forEach(m => {
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
