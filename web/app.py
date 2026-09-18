import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Form, Query, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from database import models
from database.seed_data import seed_database
from core.config import APP_NAME, RESTAURANT_NAME, CURRENCY
from core.receipt import generate_html_receipt, generate_text_receipt
from core.auth import verify_pin, generate_auth_token, is_authenticated_token, AUTH_COOKIE_NAME

# Sigurohemi që baza e të dhënave është e inicializuar
seed_database()

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title=APP_NAME)

# Montojmë skedarët statikë dhe shabllonet Jinja2
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def is_request_authenticated(request: Request) -> bool:
    """Kontrollon nëse përdoruesi ka shënuar kodin e saktë të sigurisë."""
    token = request.cookies.get(AUTH_COOKIE_NAME)
    return is_authenticated_token(token)


# ==========================================
# PYDANTIC SCHEMAS PËR API
# ==========================================

class OrderItemSchema(BaseModel):
    id: Optional[int] = None
    name: str
    price: float
    quantity: int = 1
    notes: Optional[str] = ""

class CreateOrderSchema(BaseModel):
    table_number: int
    waiter_name: str
    items: List[OrderItemSchema]
    notes: Optional[str] = ""
    payment_method: Optional[str] = "Kesh"


class VerifyPinSchema(BaseModel):
    pin: str


# ==========================================
# FAQET KRYESORE WEB (HTML UI)
# ==========================================

@app.get("/", response_class=RedirectResponse)
async def root():
    return RedirectResponse(url="/pos")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: Optional[str] = "/reports"):
    """Faqja e autorizimit me kod (PIN) për Meny dhe Raporte."""
    if is_request_authenticated(request):
        return RedirectResponse(url=next or "/reports")
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "active_page": "login",
            "restaurant_name": RESTAURANT_NAME,
            "next_url": next or "/reports",
            "error": None
        }
    )


@app.post("/login")
async def process_login(
    request: Request,
    pin: str = Form(...),
    next: Optional[str] = Form("/reports")
):
    """Përpunon verifikimin e kodit të sigurisë."""
    target_url = next or "/reports"
    if verify_pin(pin):
        token = generate_auth_token()
        response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            max_age=12 * 3600,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return response
    else:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "active_page": "login",
                "restaurant_name": RESTAURANT_NAME,
                "next_url": target_url,
                "error": "Kodi i sigurisë është i pasaktë! Ju lutem provoni përsëri."
            },
            status_code=400
        )


@app.get("/logout")
async def logout_view(request: Request, next: Optional[str] = "/pos"):
    """Çkyçet plotësisht nga sesioni i autorizuar dhe fshin të gjitha kukit."""
    target_url = next or "/pos"
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.set_cookie(AUTH_COOKIE_NAME, "", max_age=0, expires=0, path="/")
    return response


@app.post("/api/auth/logout")
async def api_logout():
    """Endpoint API për çkyçje të menjëhershme."""
    response = JSONResponse(content={"status": "success", "message": "Çkyçja u krye me sukses"})
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")
    response.set_cookie(AUTH_COOKIE_NAME, "", max_age=0, expires=0, path="/")
    return response


@app.get("/api/auth/status")
async def api_auth_status(request: Request):
    """Kthen gjendjen e autorizimit të sesionit."""
    return {"authenticated": is_request_authenticated(request)}


@app.post("/api/auth/verify-pin")
async def api_verify_pin(payload: VerifyPinSchema):
    """API endpoint për verifikimin e kodit nga JavaScript pa ekspozuar të dhëna."""
    if verify_pin(payload.pin):
        token = generate_auth_token()
        response = JSONResponse(content={"status": "success", "message": "Kodi është i saktë"})
        response.set_cookie(
            key=AUTH_COOKIE_NAME,
            value=token,
            max_age=12 * 3600,
            httponly=True,
            samesite="lax",
            path="/"
        )
        return response
    else:
        raise HTTPException(status_code=401, detail="Kodi i sigurisë është i pasaktë")


@app.get("/pos", response_class=HTMLResponse)
async def pos_page(request: Request, tab: Optional[str] = None):
    """Faqja e shitjes POS."""
    auth = is_request_authenticated(request)
    if tab == "statistikat" and not auth:
        return RedirectResponse(url="/login?next=/pos?tab=statistikat")

    categories = models.get_categories()
    items = models.get_menu_items(active_only=True)
    tables = models.get_tables()
    staff = models.get_staff_list()
    pending_orders = models.get_orders(status="E Re")

    return templates.TemplateResponse(
        request=request,
        name="pos.html",
        context={
            "active_page": "pos",
            "restaurant_name": RESTAURANT_NAME,
            "categories": categories,
            "items": items,
            "tables": tables,
            "staff": staff,
            "pending_orders_count": len(pending_orders),
            "is_authenticated": auth
        }
    )


@app.get("/kitchen", response_class=HTMLResponse)
async def kitchen_page(request: Request):
    """Ekrani i kuzhinës (KDS) - shfaq vetëm porositë që kanë ushqim dhe vetëm artikujt e ushqimit."""
    kitchen_orders = models.get_kitchen_orders(limit=100)
    pending_count = len([o for o in kitchen_orders if o["status"] == "E Re"])

    return templates.TemplateResponse(
        request=request,
        name="kitchen.html",
        context={
            "active_page": "kitchen",
            "restaurant_name": RESTAURANT_NAME,
            "orders": kitchen_orders,
            "pending_orders_count": pending_count,
            "is_authenticated": is_request_authenticated(request)
        }
    )


@app.get("/api/kitchen/orders")
async def api_get_kitchen_orders():
    """API që kthen vetëm porositë për kuzhinë (vetëm me artikujt e ushqimit)."""
    return models.get_kitchen_orders()


@app.get("/tables", response_class=HTMLResponse)
async def tables_page(request: Request):
    """Harta e tavolinave."""
    tables = models.get_tables()
    pending_orders = models.get_orders(status="E Re")

    return templates.TemplateResponse(
        request=request,
        name="tables.html",
        context={
            "active_page": "tables",
            "restaurant_name": RESTAURANT_NAME,
            "tables": tables,
            "pending_orders_count": len(pending_orders),
            "is_authenticated": is_request_authenticated(request)
        }
    )


@app.get("/admin/menu", response_class=HTMLResponse)
async def admin_menu_page(request: Request):
    """Menaxhimi i menusë (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        return RedirectResponse(url="/login?next=/admin/menu")

    items = models.get_menu_items(active_only=True)
    categories = models.get_categories()
    pending_orders = models.get_orders(status="E Re")

    return templates.TemplateResponse(
        request=request,
        name="admin_menu.html",
        context={
            "active_page": "menu",
            "restaurant_name": RESTAURANT_NAME,
            "items": items,
            "categories": categories,
            "pending_orders_count": len(pending_orders)
        }
    )


@app.post("/admin/menu/add", response_class=RedirectResponse)
async def admin_add_item(
    request: Request,
    name: str = Form(...),
    category_id: int = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(100),
    description: str = Form("")
):
    """Shton një artikull të ri nga forma e administratorit (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        return RedirectResponse(url="/login?next=/admin/menu")

    models.add_menu_item(name, category_id, price, stock_quantity, description)
    return RedirectResponse(url="/admin/menu", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/menu/delete/{item_id}", response_class=RedirectResponse)
async def admin_delete_item(request: Request, item_id: int):
    """Fshin një artikull nga menyja (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        return RedirectResponse(url="/login?next=/admin/menu")

    models.delete_menu_item(item_id)
    return RedirectResponse(url="/admin/menu", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, date: Optional[str] = None):
    """Raportet dhe statistikat ditore (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        return RedirectResponse(url="/login?next=/reports")

    target_date = date or datetime.now().strftime("%Y-%m-%d")
    stats = models.get_daily_statistics(target_date)
    pending_orders = models.get_orders(status="E Re")

    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "active_page": "reports",
            "restaurant_name": RESTAURANT_NAME,
            "stats": stats,
            "target_date": target_date,
            "pending_orders_count": len(pending_orders)
        }
    )


@app.get("/invoice/{order_id}", response_class=HTMLResponse)
async def invoice_view(order_id: int):
    """Gjeneron faturën HTML gati për printim."""
    order = models.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Porosia nuk u gjet")
    html_content = generate_html_receipt(order)
    return HTMLResponse(content=html_content)


# ==========================================
# REST API ENDPOINTS
# ==========================================

@app.get("/api/categories")
async def api_get_categories():
    return models.get_categories()


@app.get("/api/items")
async def api_get_items(category_id: Optional[int] = None):
    return models.get_menu_items(category_id=category_id, active_only=True)


@app.get("/api/tables")
async def api_get_tables():
    return models.get_tables()


@app.get("/api/orders")
async def api_get_orders(status: Optional[str] = None):
    return models.get_orders(status=status)


@app.post("/api/orders")
async def api_create_order(payload: CreateOrderSchema):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Porosia nuk mund të jetë e zbrazët")

    items_list = [item.model_dump() for item in payload.items]
    order_id = models.create_order(
        table_number=payload.table_number,
        waiter_name=payload.waiter_name,
        items=items_list,
        notes=payload.notes or "",
        payment_method=payload.payment_method or "Kesh"
    )
    return {"status": "success", "order_id": order_id, "message": "Porosia u krijua me sukses"}


@app.get("/api/orders/{order_id}")
async def api_get_order(order_id: int):
    order = models.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Porosia nuk u gjet")
    return order


@app.patch("/api/orders/{order_id}/status")
async def api_update_status(order_id: int, status: str = Query(...)):
    success = models.update_order_status(order_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Porosia nuk u gjet")
    return {"status": "success", "order_id": order_id, "new_status": status}


@app.post("/api/orders/{order_id}/pay")
async def api_pay_order(order_id: int, payment_method: str = "Kesh"):
    inv_num = models.complete_and_pay_order(order_id, payment_method)
    if not inv_num:
        raise HTTPException(status_code=404, detail="Porosia nuk u gjet")
    return {"status": "success", "order_id": order_id, "invoice_number": inv_num}


@app.delete("/api/orders/{order_id}")
async def api_delete_order(order_id: int):
    success = models.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Porosia nuk u gjet ose nuk mund të fshihet")
    return {"status": "success", "message": f"Porosia #{order_id} u fshi me sukses"}


@app.post("/api/orders/{order_id}/delete")
async def api_post_delete_order(order_id: int):
    """Pranon thirrje POST per fshirje nga HTML form."""
    models.delete_order(order_id)
    return RedirectResponse(url="/reports", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/api/orders/clear-all")
async def api_clear_all_orders(request: Request):
    """Fshin te gjitha porosite nga sistemi (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        raise HTTPException(status_code=401, detail="Kërkohet autorizim me kod")
    models.clear_all_orders()
    return RedirectResponse(url="/reports", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/api/stats/daily")
async def api_daily_stats(request: Request, date: Optional[str] = None):
    """Kthen statistikat ditore (Kërkon kod sigurie)."""
    if not is_request_authenticated(request):
        raise HTTPException(status_code=401, detail="Kërkohet autorizim me kod")
    return models.get_daily_statistics(date)
