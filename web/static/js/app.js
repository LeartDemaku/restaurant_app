// ==========================================================
// SISTEMI I MENAXHIMIT TË RESTORANTIT - JAVASCRIPT KRYESOR
// Përfshin menaxhimin interaktiv të shportës (+, -, fshirje)
// ==========================================================

let currentOrderItems = [];
let shumaTotale = 0.0;

// 1. SHTIMI I ARTIKULLIT NË POROSI
function shtoNePorosi(emri, cmimi, id = null) {
    cmimi = parseFloat(cmimi);
    
    // Kontrollojmë nëse artikulli ekziston tashmë në porosi
    const existingIndex = currentOrderItems.findIndex(it => it.name === emri);
    if (existingIndex !== -1) {
        currentOrderItems[existingIndex].quantity += 1;
    } else {
        currentOrderItems.push({
            id: id,
            name: emri,
            price: cmimi,
            quantity: 1
        });
    }

    renderPorosiaAktuale();
}

// 2. NDRYSHIMI I SASISË SË ARTIKULLIT (+1 ose -1)
function ndryshoSasi(index, delta) {
    if (index >= 0 && index < currentOrderItems.length) {
        currentOrderItems[index].quantity += delta;
        if (currentOrderItems[index].quantity <= 0) {
            currentOrderItems.splice(index, 1);
        }
        renderPorosiaAktuale();
    }
}

// 3. FSHIRJA E ARTIKULLIT NGA POROSIA
function fshiArtikullNgaPorosia(index) {
    if (index >= 0 && index < currentOrderItems.length) {
        currentOrderItems.splice(index, 1);
        renderPorosiaAktuale();
    }
}

// 4. ANULIMI I VEPRIMIT TË FUNDIT (UNDO)
function anuloTeFundit() {
    if (currentOrderItems.length === 0) return;
    const lastItem = currentOrderItems[currentOrderItems.length - 1];
    lastItem.quantity -= 1;
    if (lastItem.quantity <= 0) {
        currentOrderItems.pop();
    }
    renderPorosiaAktuale();
}

// 5. PASTRIMI I TË GJITHË POROSISË
function pastroPorosi() {
    currentOrderItems = [];
    renderPorosiaAktuale();
}

// 6. RENDERIMI VIZUAL I POROSISË AKTUALE
function renderPorosiaAktuale() {
    const listContainer = document.getElementById('orderItemsList');
    const placeholder = document.getElementById('emptyOrderPlaceholder');
    const labelTotali = document.getElementById('etiketaTotali');
    const badgeCount = document.getElementById('orderItemCount');

    // Llogarisim shumën totale dhe numrin e artikujve
    shumaTotale = currentOrderItems.reduce((acc, it) => acc + (it.price * it.quantity), 0.0);
    const totalArtikuj = currentOrderItems.reduce((acc, it) => acc + it.quantity, 0);

    if (labelTotali) {
        labelTotali.textContent = `Totali: ${shumaTotale.toFixed(2)}€ `;
    }

    if (badgeCount) {
        badgeCount.textContent = `(${totalArtikuj} artikuj)`;
    }

    if (!listContainer) return;

    if (currentOrderItems.length === 0) {
        if (placeholder) placeholder.style.display = 'flex';
        listContainer.innerHTML = '';
        return;
    }

    if (placeholder) placeholder.style.display = 'none';

    let html = '';
    currentOrderItems.forEach((item, index) => {
        const itemSubtotal = (item.price * item.quantity).toFixed(2);
        html += `
            <div class="order-row-item">
                <div class="order-item-left">
                    <span class="order-item-name" title="${item.name}">${item.name}</span>
                    <span class="order-item-unit-price">${item.price.toFixed(2)}€ për copë</span>
                </div>
                <div class="order-item-controls">
                    <button type="button" class="btn-qty btn-minus" onclick="ndryshoSasi(${index}, -1)" title="Zvogëlo sasinë">-</button>
                    <span class="order-item-qty">${item.quantity}</span>
                    <button type="button" class="btn-qty btn-plus" onclick="ndryshoSasi(${index}, 1)" title="Shto edhe një (+1)">+</button>
                    <span class="order-item-subtotal">${itemSubtotal}€</span>
                    <button type="button" class="btn-item-delete" onclick="fshiArtikullNgaPorosia(${index})" title="Fshi këtë artikull">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </div>
            </div>
        `;
    });

    listContainer.innerHTML = html;

    // Scrollim automatik në fund të listës kur shtohet artikull i ri
    const scrollBox = document.getElementById('zonaPorosiContainer');
    if (scrollBox) {
        scrollBox.scrollTop = scrollBox.scrollHeight;
    }
}

// 7. PRINTIMI I FATURËS
function printoFaturen() {
    if (currentOrderItems.length === 0) {
        alert("Nuk ka porosi për të printuar!");
        return;
    }

    const printWindow = window.open('', '_blank', 'width=460,height=620');
    if (!printWindow) {
        window.print();
        return;
    }

    const now = new Date();
    const dataStr = `${String(now.getDate()).padStart(2, '0')}-${String(now.getMonth()+1).padStart(2, '0')}-${now.getFullYear()} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

    let lines = '';
    currentOrderItems.forEach(item => {
        const namePad = item.name.length > 22 ? item.name.substring(0, 22) : item.name.padEnd(23, ' ');
        const qtyStr = `x${item.quantity}`.padStart(4, ' ');
        const subtotalStr = `${(item.price * item.quantity).toFixed(2)}€`.padStart(9, ' ');
        lines += `${namePad} ${qtyStr} ${subtotalStr}\n`;
    });

    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Faturë Restoranti</title>
            <style>
                body {
                    font-family: 'Consolas', monospace;
                    font-size: 14px;
                    padding: 24px;
                    white-space: pre;
                    line-height: 1.5;
                    color: #000;
                }
            </style>
        </head>
        <body>
=== FATURË RESTORANTI ===
Data: ${dataStr}
----------------------------------------
Artikulli                Sasia    Totali
----------------------------------------
${lines}----------------------------------------
Totali i Faturës:           ${shumaTotale.toFixed(2)}€
========================================
Faleminderit për vizitën tuaj!
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
    }, 250);
}

// 8. RUAJTJA E POROSISË (100% IDENTIKE ME JAVA GUI)
async function ruajPorosi() {
    if (shumaTotale === 0.0 || currentOrderItems.length === 0) {
        alert("Shto artikuj në porosi para ruajtjes!");
        return;
    }

    const lastWaiter = localStorage.getItem('last_waiter') || "";
    const kamarieri = prompt("Shkruani emrin e kamarierit:", lastWaiter);
    if (kamarieri === null) return; // Klikoi cancel
    if (!kamarieri.trim()) {
        alert("Emri i kamarierit është i detyrueshëm!");
        return;
    }

    const numriTavolinesStr = prompt("Shkruani numrin e tavolinës:", "1");
    if (numriTavolinesStr === null) return; // Klikoi cancel
    if (!numriTavolinesStr.trim()) {
        alert("Numri i tavolinës është i detyrueshëm!");
        return;
    }

    const numriTavolines = parseInt(numriTavolinesStr.trim());
    if (isNaN(numriTavolines) || numriTavolines <= 0) {
        alert("Numri i tavolinës duhet të jetë numër!");
        return;
    }

    localStorage.setItem('last_waiter', kamarieri.trim());

    try {
        const payload = {
            table_number: numriTavolines,
            waiter_name: kamarieri.trim(),
            items: currentOrderItems.map(item => ({
                id: item.id || null,
                name: item.name,
                price: item.price,
                quantity: item.quantity,
                notes: ""
            })),
            notes: "",
            payment_method: "Kesh"
        };

        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json();
            alert("Gabim gjatë ruajtjes: " + (err.detail || "Diçka shkoi keq"));
            return;
        }

        alert("Porosia u ruajt me sukses!");
        pastroPorosi();
        rifreskoTabelen();
        perditesoStatistikat();
    } catch (e) {
        alert("Gabim gjatë ruajtjes: " + e.message);
    }
}

// 9. NDRYSHIMI I KATEGORISË SË ARTIKUJVE (Pije, Kafe, Ushqim, Embëlsirë)
function switchCategory(catName, btnEl) {
    document.querySelectorAll('.cat-nav-btn').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    const buttons = document.querySelectorAll('.btn-artikull');
    buttons.forEach(btn => {
        const cat = btn.getAttribute('data-category');
        if (catName === 'all' || (cat && cat.toLowerCase() === catName.toLowerCase())) {
            btn.style.display = 'flex';
        } else {
            btn.style.display = 'none';
        }
    });
}

// 10. TABET KRYESORE (Porositë, Menaxhimi, Statistikat)
function showTab(tabName) {
    // Fshehim të gjitha panelet
    const pPorosite = document.getElementById('panelPorosite');
    const pMenaxhimi = document.getElementById('panelMenaxhimi');
    const pStatistikat = document.getElementById('panelStatistikat');

    if (pPorosite) pPorosite.style.display = 'none';
    if (pMenaxhimi) pMenaxhimi.style.display = 'none';
    if (pStatistikat) pStatistikat.style.display = 'none';

    // Heqim klasën active nga butonat
    const bPorosite = document.getElementById('tabBtnPorosite');
    const bMenaxhimi = document.getElementById('tabBtnMenaxhimi');
    const bStatistikat = document.getElementById('tabBtnStatistikat');

    if (bPorosite) bPorosite.classList.remove('active');
    if (bMenaxhimi) bMenaxhimi.classList.remove('active');
    if (bStatistikat) bStatistikat.classList.remove('active');

    if (tabName === 'menaxhimi') {
        if (pMenaxhimi) pMenaxhimi.style.display = 'block';
        if (bMenaxhimi) bMenaxhimi.classList.add('active');
        rifreskoTabelen();
    } else if (tabName === 'statistikat') {
        if (pStatistikat) pStatistikat.style.display = 'block';
        if (bStatistikat) bStatistikat.classList.add('active');
        perditesoStatistikat();
    } else {
        if (pPorosite) pPorosite.style.display = 'block';
        if (bPorosite) bPorosite.classList.add('active');
    }
}

function handleTabClick(event, tabName) {
    // Nëse paneli ekziston në faqe, ndërrojmë lokalisht pa reload
    const targetPanel = document.getElementById(tabName === 'porosite' ? 'panelPorosite' : (tabName === 'menaxhimi' ? 'panelMenaxhimi' : 'panelStatistikat'));
    if (targetPanel) {
        event.preventDefault();
        showTab(tabName);
        history.replaceState(null, '', `/pos?tab=${tabName}`);
    }
}

// 11. RIFRESKIMI I TABELËS SË POROSIVE (TAB 2: MENAXHIMI)
async function rifreskoTabelen() {
    const tbody = document.getElementById('tabelaPorosiveBody');
    if (!tbody) return;

    try {
        const res = await fetch('/api/orders');
        const orders = await res.json();
        tbody.innerHTML = '';

        if (orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="padding: 24px; color: #94a3b8; font-style: italic;">Nuk ka asnjë porosi të regjistruar në sistem.</td></tr>`;
            return;
        }

        orders.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${p.created_at || ''}</td>
                <td><strong>${p.waiter_name || ''}</strong></td>
                <td>Tavolina ${p.table_number || ''}</td>
                <td style="font-weight: 800; color: #27ae60;">${p.total_amount.toFixed(2)}€</td>
                <td>
                    <select class="status-select" onchange="ndryshoStatusin(${p.id}, this.value)">
                        <option value="E Re" ${p.status === 'E Re' ? 'selected' : ''}>E Re</option>
                        <option value="Në Përgatitje" ${p.status === 'Në Përgatitje' ? 'selected' : ''}>Në Përgatitje</option>
                        <option value="E Përfunduar" ${p.status === 'E Përfunduar' ? 'selected' : ''}>E Përfunduar</option>
                    </select>
                </td>
                <td>
                    <button type="button" class="btn-delete-order" onclick="fshiPorosine(${p.id})">Fshi</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Gabim gjatë rifreskimit të tabelës:", e);
    }
}

// 12. NDRYSHIMI I STATUSIT TË POROSISË
async function ndryshoStatusin(orderId, status) {
    try {
        const res = await fetch(`/api/orders/${orderId}/status?status=${encodeURIComponent(status)}`, {
            method: 'PATCH'
        });
        if (res.ok) {
            perditesoStatistikat();
        }
    } catch (e) {
        alert("Gabim gjatë ndryshimit të statusit: " + e.message);
    }
}

// 13. FSHIRJA E NJË POROSIE NGA TABELA
async function fshiPorosine(orderId) {
    if (!confirm(`A jeni të sigurt që dëshironi ta fshini porosinë #${orderId}?`)) return;
    try {
        const res = await fetch(`/api/orders/${orderId}`, { method: 'DELETE' });
        if (res.ok) {
            rifreskoTabelen();
            perditesoStatistikat();
        } else {
            alert("Nuk mund të fshihet porosia.");
        }
    } catch (e) {
        alert("Gabim gjatë fshirjes: " + e.message);
    }
}

// 14. FSHIRJA E TË GJITHA POROSIVE NGA SISTEMI
async function pastroTeGjithaPorosite() {
    if (!confirm("⚠️ KUJDES: A dëshironi të fshini TË GJITHA porositë nga sistemi? Asnjë porosi nuk do të mbetet.")) return;
    try {
        const res = await fetch('/api/orders/clear-all', { method: 'POST' });
        if (res.ok) {
            alert("Të gjitha porositë u fshinë me sukses!");
            rifreskoTabelen();
            perditesoStatistikat();
        }
    } catch (e) {
        alert("Gabim: " + e.message);
    }
}

// 15. STATISTIKAT DITORE (TAB 3: STATISTIKAT)
function rifreskoStatistikat() {
    perditesoStatistikat();
}

async function perditesoStatistikat() {
    const area = document.getElementById('zonaStatistikat');
    if (!area) return;

    try {
        const res = await fetch('/api/stats/daily');
        const stats = await res.json();

        const now = new Date();
        const dataSot = `${String(now.getDate()).padStart(2, '0')}-${String(now.getMonth()+1).padStart(2, '0')}-${now.getFullYear()}`;

        let sb = "";
        sb += `STATISTIKAT PËR DATËN: ${dataSot}\n`;
        sb += `===================================================\n\n`;
        sb += `Numri total i porosive: ${stats.total_orders}\n`;
        sb += `Totali i xhiros ditore: ${stats.total_revenue.toFixed(2)}€\n`;
        sb += `Mesatarja për porosi:   ${stats.average_order.toFixed(2)}€\n\n`;

        sb += `PËRMBLEDHJA SIPAS KAMARIERËVE:\n`;
        sb += `---------------------------------------------------\n`;
        if (!stats.waiter_stats || stats.waiter_stats.length === 0) {
            sb += `(Nuk ka shitje të regjistruara për kamarierët)\n\n`;
        } else {
            stats.waiter_stats.forEach(w => {
                const waiterPad = w.waiter_name.padEnd(16, ' ');
                sb += `Kamarieri: ${waiterPad} | Porosi: ${String(w.total_orders).padStart(2, ' ')} | Xhiro: ${w.total_sales.toFixed(2).padStart(7, ' ')}€ | Mesatare: ${w.average_sales.toFixed(2)}€\n`;
            });
            sb += `\n`;
        }

        sb += `DETAJET E POROSIVE:\n`;
        sb += `---------------------------------------------------\n`;
        if (!stats.orders || stats.orders.length === 0) {
            sb += `(Nuk ka porosi të regjistruara)\n`;
        } else {
            stats.orders.forEach(p => {
                const dateStr = p.created_at || '';
                const waiterStr = (p.waiter_name || '').padEnd(14, ' ');
                const tavStr = `Tavolina: ${String(p.table_number).padStart(2, ' ')}`;
                const totStr = `Totali: ${p.total_amount.toFixed(2).padStart(7, ' ')}€`;
                const statStr = `Statusi: ${p.status}`;
                sb += `${dateStr} | ${waiterStr} | ${tavStr} | ${totStr} | ${statStr}\n`;
            });
        }

        area.value = sb;
    } catch (e) {
        console.error("Gabim gjatë marrjes së statistikave:", e);
    }
}

// 16. FUNKSIONET NDIHMËSE PËR KUZHINËN & RAPORTET
async function updateKitchenStatus(orderId, newStatus) {
    await ndryshoStatusin(orderId, newStatus);
    window.location.reload();
}

async function deleteOrder(orderId) {
    await fshiPorosine(orderId);
    window.location.reload();
}

async function clearAllOrders() {
    await pastroTeGjithaPorosite();
    window.location.reload();
}

// 17. INICIALIZIMI ME NGARKIMIN E FAQES
document.addEventListener('DOMContentLoaded', () => {
    // Caktojmë kategorinë e parë 'Pije' si aktive në POS
    const firstCatBtn = document.querySelector('.cat-nav-btn');
    if (firstCatBtn) {
        switchCategory('Pije', firstCatBtn);
    }

    // Inicializojmë listën bosh të porosisë
    renderPorosiaAktuale();

    // Kontrollojmë nëse URL ka parametër ?tab=...
    const urlParams = new URLSearchParams(window.location.search);
    const tabParam = urlParams.get('tab');
    if (tabParam) {
        showTab(tabParam);
    }

    // Ngarkojmë paraprakisht të dhënat e tabelës dhe statistikave
    rifreskoTabelen();
    perditesoStatistikat();
});
