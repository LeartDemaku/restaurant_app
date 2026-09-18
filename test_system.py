import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from database import models
from database.seed_data import seed_database
from core.receipt import generate_text_receipt, generate_html_receipt

def run_tests():
    seed_database()

    # 1. Test items
    items = models.get_menu_items()
    print(f"1. Artikuj në meny: {len(items)}")
    assert len(items) >= 70, f"Priteshin mbi 70 artikuj, por jane {len(items)}"

    # 2. Test create order
    order_items = [
        {"id": items[0]["id"], "name": items[0]["name"], "price": items[0]["price"], "quantity": 2, "notes": "freskët"},
        {"id": items[5]["id"], "name": items[5]["name"], "price": items[5]["price"], "quantity": 1, "notes": ""}
    ]
    order_id = models.create_order(table_number=5, waiter_name="Ardit (Kamarier)", items=order_items, notes="Test porosi")
    print(f"2. Porosia e testit u krijua me ID: {order_id}")
    assert order_id > 0

    # 3. Test get order
    order = models.get_order_by_id(order_id)
    print(f"3. Porosia: Tavolina {order['table_number']}, Totali {order['total_amount']}€, Artikuj: {len(order['items'])}")
    assert len(order["items"]) == 2

    # 4. Test status update
    models.update_order_status(order_id, "Në Përgatitje")
    order_updated = models.get_order_by_id(order_id)
    assert order_updated["status"] == "Në Përgatitje"
    print("4. Ndryshimi i statusit në 'Në Përgatitje': OK")

    # 5. Test pay and invoice
    inv_num = models.complete_and_pay_order(order_id, "Kesh")
    print(f"5. Fatura e arkëtimit u gjenerua: {inv_num}")
    assert inv_num is not None

    # 6. Test receipts
    txt_rec = generate_text_receipt(order_updated, inv_num)
    html_rec = generate_html_receipt(order_updated, inv_num)
    assert len(txt_rec) > 100
    assert "Fatura" in html_rec
    print("6. Gjenerimi i faturës termale dhe HTML: OK")

    # 7. Test daily stats
    stats = models.get_daily_statistics()
    print(f"7. Statistikat: {stats['total_orders']} porosi, Xhiroja: {stats['total_revenue']}€")
    assert stats["total_orders"] >= 1

    print("\n✅ TË GJITHA TESTET KANË KALUAR ME SUKSES TË PLOTË!")

if __name__ == "__main__":
    run_tests()
