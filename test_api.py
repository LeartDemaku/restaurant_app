import sys
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from starlette.testclient import TestClient
from web.app import app
from database import models

client = TestClient(app)

def test_endpoints():
    # 1. Test GET /pos
    res = client.get("/pos")
    assert res.status_code == 200
    assert "Porosia Aktuale" in res.text
    print("Test GET /pos: OK (Status 200)")

    # 2. Test GET /kitchen
    res = client.get("/kitchen")
    assert res.status_code == 200
    assert "Ekrani i Kuzhinës" in res.text
    print("Test GET /kitchen: OK (Status 200)")

    # 3. Test GET /tables
    res = client.get("/tables")
    assert res.status_code == 200
    assert "Harta e Tavolinave" in res.text
    print("Test GET /tables: OK (Status 200)")

    # 4. Test GET /reports
    res = client.get("/reports")
    assert res.status_code == 200
    assert "Statistikat" in res.text
    print("Test GET /reports: OK (Status 200)")

    # 5. Test API items
    res = client.get("/api/items")
    assert res.status_code == 200
    items = res.json()
    assert len(items) >= 70
    print(f"Test GET /api/items: OK ({len(items)} artikuj)")

    # 6. Test API create order
    payload = {
        "table_number": 2,
        "waiter_name": "Ardit Test",
        "items": [
            {"id": items[0]["id"], "name": items[0]["name"], "price": items[0]["price"], "quantity": 2, "notes": "pa akull"},
            {"id": items[1]["id"], "name": items[1]["name"], "price": items[1]["price"], "quantity": 1, "notes": ""}
        ],
        "notes": "Porosi e shpejte",
        "payment_method": "Kesh"
    }
    res = client.post("/api/orders", json=payload)
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["status"] == "success"
    order_id = res_data["order_id"]
    print(f"Test POST /api/orders: OK (Krijuar Porosia #{order_id})")

    # 7. Test invoice view
    res = client.get(f"/invoice/{order_id}")
    assert res.status_code == 200
    assert "Fatura" in res.text
    print("Test GET /invoice: OK")

    # 8. Test Pay order
    res = client.post(f"/api/orders/{order_id}/pay?payment_method=Kesh")
    assert res.status_code == 200
    assert "FAT-" in res.json()["invoice_number"]
    print("Test POST /api/orders/{id}/pay: OK")

    # 9. Test Delete order
    res = client.delete(f"/api/orders/{order_id}")
    assert res.status_code == 200
    print(f"Test DELETE /api/orders/{order_id}: OK")

    # 10. Test Kitchen Food Filter: porositë me pije nuk shfaqen në kuzhinë, kurse me ushqim shfaqet vetëm ushqimi
    p_drinks = client.post("/api/orders", json={
        "table_number": 3,
        "waiter_name": "Test Pije",
        "items": [{"name": "Coca Cola 0.33l", "price": 1.5, "quantity": 1, "notes": ""}]
    }).json()["order_id"]

    p_mix = client.post("/api/orders", json={
        "table_number": 4,
        "waiter_name": "Test Miks",
        "items": [
            {"name": "Fanta Orange 0.33l", "price": 1.5, "quantity": 1, "notes": ""},
            {"name": "Pleskavicë Sharri", "price": 4.5, "quantity": 1, "notes": "e pjekur mire"}
        ]
    }).json()["order_id"]

    kitchen_orders = models.get_kitchen_orders()
    assert any(k["id"] == p_mix for k in kitchen_orders), "Porosia me ushqim duhet te shfaqet ne kuzhine"
    assert not any(k["id"] == p_drinks for k in kitchen_orders), "Porosia vetem me pije NUK duhet te shfaqet ne kuzhine"

    mix_k_order = next(k for k in kitchen_orders if k["id"] == p_mix)
    mix_items = [i["item_name"] for i in mix_k_order["items"]]
    assert "Pleskavicë Sharri" in mix_items
    assert "Fanta Orange 0.33l" not in mix_items, "Pija nuk duhet te shfaqet ne kuzhine!"
    print("Test Kitchen Food Filter: OK (Vetëm ushqimi shkon dhe shfaqet në kuzhinë)")

    # 11. Test Clear all orders
    models.clear_all_orders()
    assert len(models.get_orders()) == 0
    print("Test clear_all_orders(): OK (Numri i porosive tani: 0)")

    print("\n✅ TË GJITHA TESTET DHE FUNKSIONET E REJA (FSHIRJE, RESET, KUZHINË-FILTER) KALUAN ME SUKSES!")

if __name__ == "__main__":
    test_endpoints()
