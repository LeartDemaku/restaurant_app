// ===============================================
// RESTAURANT POS CLIENT-SIDE SCRIPT (ULTRA MODERN)
// ===============================================

let cart = [];
let audioCtx = null;

// Audio Chime Synthesizer me Web Audio API (Nuk kërkon skedarë të jashtëm mp3!)
function playNotificationSound(type = 'success') {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        const now = audioCtx.currentTime;

        if (type === 'success') {
            // Tingull i këndshëm 'Ding-Ding' për porosi të re / pagesë
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.setValueAtTime(880.00, now + 0.12); // A5
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
            osc.start(now);
            osc.stop(now + 0.4);
        } else if (type === 'order') {
            // Tingull për kuzhinën
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.setValueAtTime(659.25, now + 0.15); // E5
            osc.frequency.setValueAtTime(783.99, now + 0.3); // G5
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
            osc.start(now);
            osc.stop(now + 0.6);
        } else if (type === 'danger') {
            // Tingull fshirjeje / paralajmërimi
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(320, now);
            osc.frequency.setValueAtTime(220, now + 0.15);
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
            osc.start(now);
            osc.stop(now + 0.35);
        }
    } catch (e) {
        console.warn("Audio Context i bllokuar:", e);
    }
}

// Toast Notifications (Në vend të alert-it klasik)
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    let icon = 'bi-check-circle-fill';
    if (type === 'danger') icon = 'bi-trash-fill';
    if (type === 'warning') icon = 'bi-exclamation-triangle-fill';

    toast.innerHTML = `<i class="bi ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, 3800);
}

// URL Params
function getTableNumberFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('table');
}

// Inicializimi i POS
function initPOS() {
    const presetTable = getTableNumberFromUrl();
    if (presetTable) {
        const tableSelect = document.getElementById('tableSelect');
        if (tableSelect) {
            tableSelect.value = presetTable;
        }
    }

    // Mbushim emrin e fundit të kamarierit nga localStorage
    const waiterInput = document.getElementById('waiterInput');
    const savedWaiter = localStorage.getItem('pos_last_waiter');
    if (waiterInput && savedWaiter) {
        waiterInput.value = savedWaiter;
    }

    // Filtri i kategorive
    const catBtns = document.querySelectorAll('.cat-btn');
    catBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            catBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const cat = btn.getAttribute('data-cat');
            filterItems(cat);
        });
    });

    // Kërkimi i artikujve
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            searchItems(query);
        });
    }

    renderCart();
}

function filterItems(category) {
    const items = document.querySelectorAll('.item-card');
    items.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (category === 'all' || cardCat === category) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

function searchItems(query) {
    const items = document.querySelectorAll('.item-card');
    items.forEach(card => {
        const title = card.querySelector('.item-title').textContent.toLowerCase();
        if (title.includes(query)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Menaxhimi i shportës
function addToCart(id, name, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity += 1;
    } else {
        cart.push({ id, name, price: parseFloat(price), quantity: 1, notes: '' });
    }
    renderCart();
}

function changeQty(id, delta) {
    const item = cart.find(i => i.id === id);
    if (!item) return;
    item.quantity += delta;
    if (item.quantity <= 0) {
        cart = cart.filter(i => i.id !== id);
    }
    renderCart();
}

function clearCart() {
    if (cart.length === 0) return;
    if (confirm("A jeni të sigurt që dëshironi ta pastroni porosinë aktuale?")) {
        cart = [];
        renderCart();
        showToast("Shporta u pastrua", "warning");
    }
}

function renderCart() {
    const cartContainer = document.getElementById('cartItems');
    const totalEl = document.getElementById('cartTotal');
    if (!cartContainer || !totalEl) return;

    if (cart.length === 0) {
        cartContainer.innerHTML = `
            <div style="text-align:center; color:#94a3b8; padding:50px 10px;">
                <i class="bi bi-basket3" style="font-size: 2.2rem; opacity: 0.5;"></i>
                <div style="margin-top: 10px; font-weight: 600;">Porosia është e zbrazët</div>
                <div style="font-size: 0.8rem; margin-top: 4px;">Klikoni artikujt majtas për t'i shtuar</div>
            </div>
        `;
        totalEl.textContent = '0.00 €';
        return;
    }

    let total = 0.0;
    cartContainer.innerHTML = '';

    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        total += subtotal;

        const row = document.createElement('div');
        row.className = 'cart-item-row';
        row.innerHTML = `
            <div class="cart-item-info">
                <div class="cart-item-name">${item.name}</div>
                <div class="cart-item-price">${item.price.toFixed(2)}€ &times; ${item.quantity} = <strong>${subtotal.toFixed(2)}€</strong></div>
            </div>
            <div class="cart-qty-ctrl">
                <button class="qty-btn" onclick="changeQty(${item.id}, -1)">-</button>
                <span style="font-weight:bold; min-width:24px; text-align:center;">${item.quantity}</span>
                <button class="qty-btn" onclick="changeQty(${item.id}, 1)">+</button>
            </div>
        `;
        cartContainer.appendChild(row);
    });

    totalEl.textContent = `${total.toFixed(2)} €`;
}

// Dërgimi i porosisë në server
async function submitOrder() {
    if (cart.length === 0) {
        showToast("Shtoni të paktën një artikull para dërgimit!", "warning");
        return;
    }

    const tableSelect = document.getElementById('tableSelect');
    const waiterInput = document.getElementById('waiterInput');
    const notesInput = document.getElementById('orderNotes');

    const tableNumber = parseInt(tableSelect ? tableSelect.value : 1);
    const waiterName = waiterInput ? waiterInput.value.trim() : "";

    if (!waiterName) {
        showToast("Ju lutem shkruani emrin e kamarierit!", "warning");
        if (waiterInput) waiterInput.focus();
        return;
    }

    const payload = {
        table_number: tableNumber,
        waiter_name: waiterName,
        items: cart,
        notes: notesInput ? notesInput.value : "",
        payment_method: 'Kesh'
    };

    try {
        const res = await fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok) {
            localStorage.setItem('pos_last_waiter', waiterName);
            playNotificationSound('success');
            showToast(`✅ Porosia #${data.order_id} u dërgua për Tavolinën ${tableNumber} nga ${waiterName}!`, "success");
            cart = [];
            if (notesInput) notesInput.value = '';
            renderCart();
        } else {
            showToast(`Gabim: ${data.detail || 'Dështoi ruajtja'}`, "danger");
        }
    } catch (err) {
        showToast("Gabim gjatë lidhjes me serverin: " + err.message, "danger");
    }
}

// ===============================================
// FSHIRJA E POROSISË (DELETE ORDER)
// ===============================================
async function deleteOrder(orderId) {
    if (!confirm(`A jeni të sigurt që dëshironi ta fshini plotësisht Porosinë #${orderId}?`)) {
        return;
    }

    try {
        const res = await fetch(`/api/orders/${orderId}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            playNotificationSound('danger');
            showToast(`Porosia #${orderId} u fshi me sukses!`, "danger");
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast("Dështoi fshirja e porosisë!", "danger");
        }
    } catch (e) {
        showToast("Gabim: " + e.message, "danger");
    }
}

// Pastrimi i të gjitha porosive (Clear All Orders)
async function clearAllOrders() {
    const pass = prompt("KUJDES: Kjo do të fshijë TË GJITHA porositë nga sistemi!\nShkruani 'PO' për të konfirmuar:");
    if (pass !== 'PO' && pass !== 'po') {
        return;
    }

    try {
        const res = await fetch('/api/orders/clear-all', {
            method: 'POST'
        });

        if (res.ok) {
            playNotificationSound('danger');
            showToast("Të gjitha porositë u fshinë! Sistemi u resetua në 0.", "success");
            setTimeout(() => window.location.reload(), 700);
        } else {
            showToast("Gabim gjatë fshirjes së të gjitha porosive.", "danger");
        }
    } catch (e) {
        showToast("Gabim: " + e.message, "danger");
    }
}

// ===============================================
// KITCHEN KDS LIVE UPDATE
// ===============================================
async function updateKitchenStatus(orderId, newStatus) {
    try {
        const res = await fetch(`/api/orders/${orderId}/status?status=${encodeURIComponent(newStatus)}`, {
            method: 'PATCH'
        });
        if (res.ok) {
            playNotificationSound('order');
            showToast(`Porosia #${orderId} kaloi në '${newStatus}'`, "success");
            setTimeout(() => window.location.reload(), 400);
        } else {
            showToast("Gabim gjatë përditësimit të statusit!", "danger");
        }
    } catch (e) {
        console.error(e);
    }
}

// Rifreskimi automatik i kuzhinës çdo 6 sekonda
function startKitchenAutoRefresh() {
    setInterval(() => {
        if (window.location.pathname.includes('/kitchen')) {
            window.location.reload();
        }
    }, 6000);
}

// ===============================================
// KALKULATORI I KUSURIT (PAYMENT CHANGE MODAL)
// ===============================================
let currentPayingOrderId = null;
let currentPayingTotal = 0.0;

function openPaymentModal(orderId, total) {
    currentPayingOrderId = orderId;
    currentPayingTotal = parseFloat(total);

    let modal = document.getElementById('paymentModal');
    if (!modal) {
        createPaymentModal();
        modal = document.getElementById('paymentModal');
    }

    document.getElementById('modalTotalAmount').textContent = `${currentPayingTotal.toFixed(2)} €`;
    document.getElementById('cashGivenInput').value = '';
    document.getElementById('changeReturnAmount').textContent = '0.00 €';
    document.getElementById('changeReturnAmount').style.color = '#10b981';

    modal.classList.add('active');
    setTimeout(() => document.getElementById('cashGivenInput').focus(), 150);
}

function closePaymentModal() {
    const modal = document.getElementById('paymentModal');
    if (modal) modal.classList.remove('active');
}

function setQuickCash(amount) {
    const input = document.getElementById('cashGivenInput');
    if (!input) return;
    input.value = amount === 'exact' ? currentPayingTotal.toFixed(2) : amount;
    calculateChange();
}

function calculateChange() {
    const givenStr = document.getElementById('cashGivenInput').value;
    const given = parseFloat(givenStr) || 0.0;
    const change = given - currentPayingTotal;
    const changeEl = document.getElementById('changeReturnAmount');

    if (change < 0) {
        changeEl.textContent = `Mungojnë ${Math.abs(change).toFixed(2)} €`;
        changeEl.style.color = '#ef4444';
    } else {
        changeEl.textContent = `${change.toFixed(2)} €`;
        changeEl.style.color = '#10b981';
    }
}

async function confirmPayment(method = 'Kesh') {
    if (!currentPayingOrderId) return;

    try {
        const res = await fetch(`/api/orders/${currentPayingOrderId}/pay?payment_method=${encodeURIComponent(method)}`, {
            method: 'POST'
        });

        if (res.ok) {
            playNotificationSound('success');
            showToast(`✅ Fatura u arkëtua me sukses me ${method}!`, 'success');
            closePaymentModal();
            setTimeout(() => window.location.reload(), 600);
        } else {
            showToast("Dështoi arkëtimi!", 'danger');
        }
    } catch (e) {
        showToast("Gabim: " + e.message, 'danger');
    }
}

function createPaymentModal() {
    const modal = document.createElement('div');
    modal.id = 'paymentModal';
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                <h3 style="font-weight:800; color:#0f172a; display:flex; align-items:center; gap:8px;">
                    <i class="bi bi-cash-coin" style="color:#10b981;"></i> Arkëtimi i Faturës
                </h3>
                <button onclick="closePaymentModal()" style="background:none; border:none; font-size:1.4rem; cursor:pointer; color:#94a3b8;">&times;</button>
            </div>

            <div style="background:#f8fafc; border-radius:12px; padding:16px; text-align:center; margin-bottom:18px; border:1px solid #e2e8f0;">
                <div style="font-size:0.85rem; font-weight:700; color:#64748b; text-transform:uppercase;">Totali për Pagesë</div>
                <div id="modalTotalAmount" style="font-size:2.2rem; font-weight:800; color:#0f172a; margin-top:4px;">0.00 €</div>
            </div>

            <!-- BUTONAT E SHPEJTË TË KESHIT -->
            <div style="margin-bottom:14px;">
                <div style="font-size:0.82rem; font-weight:700; color:#64748b; margin-bottom:6px;">Prano Para të Gatshme:</div>
                <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:8px;">
                    <button type="button" class="cash-quick-btn" onclick="setQuickCash('exact')">E Saktë</button>
                    <button type="button" class="cash-quick-btn" onclick="setQuickCash(5)">5 €</button>
                    <button type="button" class="cash-quick-btn" onclick="setQuickCash(10)">10 €</button>
                    <button type="button" class="cash-quick-btn" onclick="setQuickCash(20)">20 €</button>
                    <button type="button" class="cash-quick-btn" onclick="setQuickCash(50)">50 €</button>
                </div>
            </div>

            <div style="margin-bottom:16px;">
                <label style="display:block; font-size:0.85rem; font-weight:700; color:#334155; margin-bottom:4px;">Shuma e Dhënë nga Klienti (€):</label>
                <input type="number" step="0.50" id="cashGivenInput" oninput="calculateChange()" class="search-input" style="font-size:1.3rem; font-weight:800; text-align:center;" placeholder="0.00">
            </div>

            <!-- KUSURI -->
            <div style="background:#ecfdf5; border-radius:10px; padding:12px; display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; border:1px solid #a7f3d0;">
                <span style="font-weight:700; color:#065f46;">Kusuri për t'u kthyer:</span>
                <span id="changeReturnAmount" style="font-size:1.5rem; font-weight:800; color:#10b981;">0.00 €</span>
            </div>

            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
                <button type="button" class="btn btn-outline" onclick="confirmPayment('Kartelë')">
                    <i class="bi bi-credit-card"></i> Pagesë me Kartelë
                </button>
                <button type="button" class="btn btn-success" onclick="confirmPayment('Kesh')">
                    <i class="bi bi-check2-circle"></i> Arkëto me Kesh
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Inicializimi në ngarkim
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('cartItems')) {
        initPOS();
    }
    if (window.location.pathname.includes('/kitchen')) {
        startKitchenAutoRefresh();
    }
});
