from datetime import datetime
from typing import Dict, Any
from .config import RESTAURANT_NAME, RESTAURANT_ADDRESS, RESTAURANT_PHONE, CURRENCY


def generate_text_receipt(order_data: Dict[str, Any], invoice_number: str = None) -> str:
    """Gjeneron një faturë në format teksti për printer termal (80mm/58mm)."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    table_num = order_data.get("table_number", "N/A")
    waiter = order_data.get("waiter_name", "N/A")
    order_id = order_data.get("id", "N/A")
    items = order_data.get("items", [])
    total = order_data.get("total_amount", 0.0)
    payment_method = order_data.get("payment_method", "Kesh")

    lines = []
    lines.append("=" * 40)
    lines.append(f"{RESTAURANT_NAME:^40}")
    lines.append(f"{RESTAURANT_ADDRESS:^40}")
    lines.append(f"Tel: {RESTAURANT_PHONE:^35}")
    lines.append("=" * 40)
    if invoice_number:
        lines.append(f"Fatura: {invoice_number}")
    lines.append(f"Porosia #{order_id} | Tavolina: {table_num}")
    lines.append(f"Kamarieri: {waiter}")
    lines.append(f"Data: {now_str}")
    lines.append("-" * 40)
    lines.append(f"{'Artikulli':<20} {'Sasia':>5} {'Çmimi':>6} {'Totali':>7}")
    lines.append("-" * 40)

    for item in items:
        name = item.get("item_name") or item.get("name") or "Artikull"
        qty = item.get("quantity", 1)
        price = float(item.get("unit_price") or item.get("price") or 0.0)
        subtotal = float(item.get("subtotal", price * qty))

        # Shkurtojmë emrin nëse është i gjatë për kolonën
        short_name = (name[:18] + "..") if len(name) > 20 else name
        lines.append(f"{short_name:<20} {qty:>5} {price:>6.2f} {subtotal:>6.2f}{CURRENCY}")

    lines.append("-" * 40)
    lines.append(f"{'TOTALI:':<25} {total:>13.2f} {CURRENCY}")
    lines.append(f"Mënyra e Pagesës: {payment_method}")
    lines.append("=" * 40)
    lines.append(f"{'Faleminderit për vizitën tuaj!':^40}")
    lines.append(f"{'Ju mirëpresim përsëri!':^40}")
    lines.append("=" * 40)
    lines.append("\n\n")

    return "\n".join(lines)


def generate_html_receipt(order_data: Dict[str, Any], invoice_number: str = None) -> str:
    """Gjeneron një faturë HTML gati për printim me shfletues (Print Preview / A4 ose 80mm)."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    table_num = order_data.get("table_number", "N/A")
    waiter = order_data.get("waiter_name", "N/A")
    order_id = order_data.get("id", "N/A")
    items = order_data.get("items", [])
    total = float(order_data.get("total_amount", 0.0))
    payment_method = order_data.get("payment_method", "Kesh")
    inv_code = invoice_number or f"POR-{order_id:04d}"

    items_html = ""
    for item in items:
        name = item.get("item_name") or item.get("name") or "Artikull"
        qty = item.get("quantity", 1)
        price = float(item.get("unit_price") or item.get("price") or 0.0)
        subtotal = float(item.get("subtotal", price * qty))
        items_html += f"""
        <tr>
            <td style="padding: 6px 0; border-bottom: 1px dashed #ddd;">{name}</td>
            <td style="text-align: center; border-bottom: 1px dashed #ddd;">{qty}</td>
            <td style="text-align: right; border-bottom: 1px dashed #ddd;">{price:.2f}€</td>
            <td style="text-align: right; border-bottom: 1px dashed #ddd; font-weight: bold;">{subtotal:.2f}€</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="sq">
    <head>
        <meta charset="UTF-8">
        <title>Fatura #{inv_code}</title>
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                background-color: #f5f5f5;
                padding: 20px;
                color: #222;
            }}
            .receipt-box {{
                max-width: 380px;
                margin: auto;
                background: white;
                padding: 24px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border-radius: 8px;
            }}
            .text-center {{ text-align: center; }}
            .text-right {{ text-align: right; }}
            .divider {{ border-top: 1px dashed #888; margin: 12px 0; }}
            .bold {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
            @media print {{
                body {{ background: white; padding: 0; }}
                .receipt-box {{ box-shadow: none; max-width: 100%; padding: 0; }}
                .no-print {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="receipt-box">
            <div class="text-center">
                <h2 style="margin: 0; font-size: 20px;">{RESTAURANT_NAME}</h2>
                <p style="margin: 4px 0; font-size: 13px;">{RESTAURANT_ADDRESS}</p>
                <p style="margin: 2px 0; font-size: 13px;">Tel: {RESTAURANT_PHONE}</p>
            </div>
            
            <div class="divider"></div>
            
            <div style="font-size: 13px;">
                <div><strong>Kodi:</strong> {inv_code}</div>
                <div><strong>Data:</strong> {now_str}</div>
                <div><strong>Tavolina:</strong> {table_num} &nbsp;|&nbsp; <strong>Kamarieri:</strong> {waiter}</div>
            </div>
            
            <div class="divider"></div>
            
            <table>
                <thead>
                    <tr style="border-bottom: 1px solid #333; font-size: 13px;">
                        <th style="text-align: left;">Artikulli</th>
                        <th>Sasia</th>
                        <th style="text-align: right;">Çmimi</th>
                        <th style="text-align: right;">Totali</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div class="divider"></div>
            
            <div style="display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; margin: 8px 0;">
                <span>TOTALI:</span>
                <span>{total:.2f} €</span>
            </div>
            <div style="font-size: 13px;">
                <span>Pagesa: <strong>{payment_method}</strong></span>
            </div>
            
            <div class="divider"></div>
            
            <div class="text-center" style="font-size: 13px; margin-top: 15px;">
                <p style="margin: 3px 0;">Faleminderit për vizitën tuaj!</p>
                <p style="margin: 3px 0;">Ju mirëpresim përsëri!</p>
            </div>

            <div class="no-print" style="margin-top: 25px; text-align: center;">
                <button onclick="window.print()" style="padding: 10px 20px; background: #27ae60; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer;">
                    🖨️ Printo Faturën
                </button>
            </div>
        </div>
    </body>
    </html>
    """
    return html
