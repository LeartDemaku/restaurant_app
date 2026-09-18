import sys
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
from typing import List, Dict, Any

from database import models
from database.seed_data import seed_database
from core.config import APP_NAME, RESTAURANT_NAME, CURRENCY, get_web_url
from core.receipt import generate_text_receipt
from .theme import *
from .dialogs import OrderSaveDialog, ReceiptPreviewDialog, AddItemDialog, PaymentWithChangeDialog


# Konfigurimi fillestar i CustomTkinter
ctk.set_appearance_mode("Light")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")


class RestaurantAppGUI(ctk.CTk):
    """Aplikacioni Kryesor Desktop per Menaxhimin e Restorantit."""

    def __init__(self):
        super().__init__()

        # Sigurohemi që baza e të dhënave është gati
        seed_database()

        # Dritarja kryesore
        self.title(f"{APP_NAME} - {RESTAURANT_NAME}")
        self.geometry("1400x820")
        self.minsize(1100, 680)

        # Variablat e shportës POS
        self.current_cart: List[Dict[str, Any]] = []
        self.total_amount: float = 0.0
        self.selected_category: str = "Të Gjitha"

        # Ndërtimi i UI
        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        # Ngarkimi i të dhënave fillestare
        self.load_categories()
        self.load_menu_items()
        self.refresh_orders_table()

    # ============================================================
    # 1. HEADER & STATUSBAR
    # ============================================================

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, height=54, fg_color=ACCENT_COLOR, corner_radius=0)
        header_frame.pack(fill="x", side="top")

        lbl_brand = ctk.CTkLabel(
            header_frame,
            text=f"☕ {RESTAURANT_NAME} - Sistemi POS & Menaxhimi",
            font=FONT_TITLE,
            text_color="white"
        )
        lbl_brand.pack(side="left", padx=20, pady=10)

        # Butoni per Dark / Light mode
        self.switch_theme = ctk.CTkSwitch(
            header_frame,
            text="Dark Mode",
            command=self.toggle_theme,
            font=FONT_BODY,
            text_color="white"
        )
        self.switch_theme.pack(side="right", padx=20, pady=10)

        # Web Server URL link
        lbl_web = ctk.CTkLabel(
            header_frame,
            text=f"🌐 Qasja Web: {get_web_url()}",
            font=FONT_BODY_BOLD,
            text_color="#f1c40f"
        )
        lbl_web.pack(side="right", padx=20, pady=10)

    def _build_statusbar(self):
        status_frame = ctk.CTkFrame(self, height=30, fg_color="#eaedf0", corner_radius=0)
        status_frame.pack(fill="x", side="bottom")

        self.lbl_status = ctk.CTkLabel(
            status_frame,
            text="Gati. Baza e të dhënave SQLite e sinkronizuar.",
            font=("Segoe UI", 10),
            text_color="#555"
        )
        self.lbl_status.pack(side="left", padx=15, pady=2)

        lbl_author = ctk.CTkLabel(
            status_frame,
            text="Python Desktop + Web POS System",
            font=("Segoe UI", 10, "italic"),
            text_color="#777"
        )
        lbl_author.pack(side="right", padx=15, pady=2)

    def toggle_theme(self):
        if self.switch_theme.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")

    # ============================================================
    # 2. MAIN TABS
    # ============================================================

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        # Krijimi i skedave
        self.tab_pos = self.tabview.add("🛒 Porositë (POS)")
        self.tab_orders = self.tabview.add("📋 Menaxhimi i Porosive")
        self.tab_tables = self.tabview.add("🪑 Tavolinat")
        self.tab_menu = self.tabview.add("📖 Menaxhimi i Menysë")
        self.tab_stats = self.tabview.add("📊 Statistikat Ditore")

        self._build_pos_tab()
        self._build_orders_tab()
        self._build_tables_tab()
        self._build_menu_tab()
        self._build_stats_tab()

    # ============================================================
    # TAB 1: POS / POROSITË
    # ============================================================

    def _build_pos_tab(self):
        self.tab_pos.grid_columnconfigure(0, weight=3)
        self.tab_pos.grid_columnconfigure(1, weight=2)
        self.tab_pos.grid_rowconfigure(0, weight=1)

        # Paneli i Majtë: Artikujt dhe Kategoritë
        left_frame = ctk.CTkFrame(self.tab_pos, corner_radius=8)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 10), pady=5)
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # Shiriti i kategorive
        self.cat_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.cat_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        # Search Bar
        search_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.entry_pos_search = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Kërko artikull (p.sh. Kafe, Burger, Trileçe)...",
            height=36
        )
        self.entry_pos_search.pack(fill="x", expand=True)
        self.entry_pos_search.bind("<KeyRelease>", lambda e: self.filter_items_search())

        # Rrjeti i artikujve (Scrollable)
        self.scroll_items = ctk.CTkScrollableFrame(left_frame, corner_radius=6)
        self.scroll_items.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # Paneli i Djathtë: Porosia Aktuale (Cart)
        right_frame = ctk.CTkFrame(self.tab_pos, corner_radius=8)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=5)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Titulli i Porosisë Aktuale
        lbl_cart_title = ctk.CTkLabel(right_frame, text="🧾 Porosia Aktuale", font=FONT_TITLE)
        lbl_cart_title.grid(row=0, column=0, sticky="w", padx=15, pady=(12, 6))

        # Zona e artikujve në shportë (Scrollable frame)
        self.scroll_cart = ctk.CTkScrollableFrame(right_frame, corner_radius=6)
        self.scroll_cart.grid(row=1, column=0, sticky="nsew", padx=12, pady=5)

        # Totali dhe Butonat e Veprimit
        bottom_cart = ctk.CTkFrame(right_frame, fg_color="transparent")
        bottom_cart.grid(row=2, column=0, sticky="ew", padx=12, pady=10)

        self.lbl_pos_total = ctk.CTkLabel(
            bottom_cart,
            text="Totali: 0.00 €",
            font=FONT_TOTAL,
            text_color=SUCCESS_COLOR
        )
        self.lbl_pos_total.pack(anchor="e", pady=(0, 10))

        # Butonat
        btn_grid = ctk.CTkFrame(bottom_cart, fg_color="transparent")
        btn_grid.pack(fill="x")

        btn_print = ctk.CTkButton(
            btn_grid,
            text="Printo",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.print_current_cart,
            height=40
        )
        btn_print.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_clear = ctk.CTkButton(
            btn_grid,
            text="Pastro",
            fg_color=DANGER_COLOR,
            hover_color=DANGER_HOVER,
            command=self.clear_cart,
            height=40
        )
        btn_clear.pack(side="left", expand=True, fill="x", padx=4)

        btn_save = ctk.CTkButton(
            btn_grid,
            text="Ruaj Porosinë",
            fg_color=SUCCESS_COLOR,
            hover_color=SUCCESS_HOVER,
            command=self.save_cart_order,
            height=40
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(4, 0))

    def load_categories(self):
        """Ngarkon butonat e kategorive."""
        for widget in self.cat_frame.winfo_children():
            widget.destroy()

        categories = models.get_categories()
        all_cats = ["Të Gjitha"] + [c["name"] for c in categories]

        for cat in all_cats:
            color_cfg = CATEGORY_COLORS.get(cat, {"bg": ACCENT_COLOR, "hover": ACCENT_HOVER})
            btn = ctk.CTkButton(
                self.cat_frame,
                text=cat,
                fg_color=color_cfg["bg"],
                hover_color=color_cfg["hover"],
                command=lambda c=cat: self.filter_category(c),
                height=34,
                width=90,
                font=FONT_BODY_BOLD
            )
            btn.pack(side="left", padx=4, pady=2)

    def load_menu_items(self):
        """Ngarkon kartat e artikujve ne rrjet."""
        for widget in self.scroll_items.winfo_children():
            widget.destroy()

        items = models.get_menu_items(active_only=True)
        search_query = self.entry_pos_search.get().strip().lower()

        filtered = []
        for item in items:
            if self.selected_category != "Të Gjitha" and item["category_name"] != self.selected_category:
                continue
            if search_query and search_query not in item["name"].lower():
                continue
            filtered.append(item)

        cols = 3  # 3 artikuj per rresht si ne Java GUI
        for idx, item in enumerate(filtered):
            row = idx // cols
            col = idx % cols

            color_cfg = CATEGORY_COLORS.get(item["category_name"], {"bg": PRIMARY_COLOR, "hover": PRIMARY_HOVER})

            # Butoni i artikullit me stil te pasur
            btn_text = f"{item['name']}\n\n{item['price']:.2f} €"
            btn = ctk.CTkButton(
                self.scroll_items,
                text=btn_text,
                fg_color=color_cfg["bg"],
                hover_color=color_cfg["hover"],
                height=85,
                font=FONT_SUBTITLE,
                command=lambda it=item: self.add_to_cart(it)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.scroll_items.grid_columnconfigure(col, weight=1)

    def filter_category(self, cat_name: str):
        self.selected_category = cat_name
        self.load_menu_items()

    def filter_items_search(self):
        self.load_menu_items()

    # ============================================================
    # SHPORTA POS (CART ACTIONS)
    # ============================================================

    def add_to_cart(self, item: Dict[str, Any]):
        existing = next((i for i in self.current_cart if i["id"] == item["id"]), None)
        if existing:
            existing["quantity"] += 1
        else:
            self.current_cart.append({
                "id": item["id"],
                "name": item["name"],
                "price": float(item["price"]),
                "quantity": 1,
                "notes": ""
            })
        self.render_cart()

    def change_cart_qty(self, item_id: int, delta: int):
        item = next((i for i in self.current_cart if i["id"] == item_id), None)
        if not item:
            return
        item["quantity"] += delta
        if item["quantity"] <= 0:
            self.current_cart = [i for i in self.current_cart if i["id"] != item_id]
        self.render_cart()

    def clear_cart(self):
        if not self.current_cart:
            return
        if messagebox.askyesno("Pastro", "A dëshironi ta pastroni porosinë aktuale?"):
            self.current_cart = []
            self.render_cart()

    def render_cart(self):
        for widget in self.scroll_cart.winfo_children():
            widget.destroy()

        if not self.current_cart:
            lbl_empty = ctk.CTkLabel(
                self.scroll_cart,
                text="Porosia është e zbrazët.\nZgjidhni artikuj nga menyja majtas.",
                text_color="gray",
                font=FONT_BODY
            )
            lbl_empty.pack(pady=40)
            self.total_amount = 0.0
            self.lbl_pos_total.configure(text="Totali: 0.00 €")
            return

        total = 0.0
        for item in self.current_cart:
            subtotal = item["price"] * item["quantity"]
            total += subtotal

            row_frame = ctk.CTkFrame(self.scroll_cart, fg_color="transparent")
            row_frame.pack(fill="x", pady=4, padx=4)

            lbl_info = ctk.CTkLabel(
                row_frame,
                text=f"{item['name']}\n{item['price']:.2f}€ × {item['quantity']} = {subtotal:.2f}€",
                justify="left",
                font=FONT_BODY_BOLD
            )
            lbl_info.pack(side="left", padx=4)

            # Butonat + dhe -
            btn_minus = ctk.CTkButton(
                row_frame,
                text="-",
                width=28,
                height=28,
                fg_color="#95a5a6",
                hover_color="#7f8c8d",
                command=lambda id=item["id"]: self.change_cart_qty(id, -1)
            )
            btn_minus.pack(side="right", padx=2)

            lbl_qty = ctk.CTkLabel(row_frame, text=str(item["quantity"]), width=25, font=FONT_BODY_BOLD)
            lbl_qty.pack(side="right", padx=2)

            btn_plus = ctk.CTkButton(
                row_frame,
                text="+",
                width=28,
                height=28,
                fg_color=PRIMARY_COLOR,
                hover_color=PRIMARY_HOVER,
                command=lambda id=item["id"]: self.change_cart_qty(id, 1)
            )
            btn_plus.pack(side="right", padx=2)

        self.total_amount = total
        self.lbl_pos_total.configure(text=f"Totali: {total:.2f} €")

    def print_current_cart(self):
        if not self.current_cart:
            messagebox.showwarning("Kujdes", "Nuk ka porosi aktive për të printuar!")
            return

        order_data = {
            "id": "AKTIV",
            "table_number": 1,
            "waiter_name": "Kasa Kryesore",
            "items": self.current_cart,
            "total_amount": self.total_amount,
            "payment_method": "Kesh"
        }
        receipt_text = generate_text_receipt(order_data)
        ReceiptPreviewDialog(self, receipt_text)

    def save_cart_order(self):
        if not self.current_cart:
            messagebox.showwarning("Kujdes", "Shtoni artikuj në porosi para se ta ruani!")
            return

        tables = models.get_tables()
        staff = models.get_staff_list()

        dialog = OrderSaveDialog(self, tables, staff)
        if not dialog.result:
            return

        table_num = dialog.result["table_number"]
        waiter = dialog.result["waiter_name"]
        payment = dialog.result["payment_method"]
        notes = dialog.result["notes"]

        order_id = models.create_order(
            table_number=table_num,
            waiter_name=waiter,
            items=self.current_cart,
            notes=notes,
            payment_method=payment
        )

        messagebox.showinfo("Sukses", f"✅ Porosia #{order_id} u ruajt me sukses për Tavolinën {table_num}!")

        # Pastrojmë shportën dhe rifreskojmë tabelat
        self.current_cart = []
        self.render_cart()
        self.refresh_orders_table()
        self.refresh_tables_view()

    # ============================================================
    # TAB 2: MENAXHIMI I POROSIVE (ORDERS MANAGEMENT)
    # ============================================================

    def _build_orders_tab(self):
        top_bar = ctk.CTkFrame(self.tab_orders, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)

        lbl_filter = ctk.CTkLabel(top_bar, text="Filtro sipas Statusit:", font=FONT_BODY_BOLD)
        lbl_filter.pack(side="left", padx=(0, 10))

        self.cmb_order_status = ctk.CTkComboBox(
            top_bar,
            values=["Të Gjitha", "E Re", "Në Përgatitje", "Gati", "E Përfunduar"],
            command=lambda s: self.refresh_orders_table()
        )
        self.cmb_order_status.pack(side="left", padx=(0, 15))

        lbl_waiter_f = ctk.CTkLabel(top_bar, text="Kërko Kamarierin:", font=FONT_BODY_BOLD)
        lbl_waiter_f.pack(side="left", padx=(10, 8))

        self.entry_waiter_filter = ctk.CTkEntry(
            top_bar,
            placeholder_text="Emri i kamarierit...",
            width=180
        )
        self.entry_waiter_filter.pack(side="left", padx=(0, 10))
        self.entry_waiter_filter.bind("<KeyRelease>", lambda e: self.refresh_orders_table())

        btn_clear_all = ctk.CTkButton(
            top_bar,
            text="⚠️ Pastro të Gjitha Porositë",
            fg_color=DANGER_COLOR,
            hover_color=DANGER_HOVER,
            command=self.clear_all_orders_gui
        )
        btn_clear_all.pack(side="right", padx=(10, 0))

        btn_refresh = ctk.CTkButton(
            top_bar,
            text="🔄 Rifresko Tabelën",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.refresh_orders_table
        )
        btn_refresh.pack(side="right")

        # Tabela me Treeview
        tree_frame = ctk.CTkFrame(self.tab_orders)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "date", "table", "waiter", "total", "status", "payment")
        self.tree_orders = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        self.tree_orders.heading("id", text="ID")
        self.tree_orders.heading("date", text="Data dhe Ora")
        self.tree_orders.heading("table", text="Tavolina")
        self.tree_orders.heading("waiter", text="Kamarieri")
        self.tree_orders.heading("total", text="Totali")
        self.tree_orders.heading("status", text="Statusi")
        self.tree_orders.heading("payment", text="Mënyra Pagesës")

        self.tree_orders.column("id", width=60, anchor="center")
        self.tree_orders.column("date", width=160, anchor="center")
        self.tree_orders.column("table", width=100, anchor="center")
        self.tree_orders.column("waiter", width=160, anchor="center")
        self.tree_orders.column("total", width=110, anchor="center")
        self.tree_orders.column("status", width=140, anchor="center")
        self.tree_orders.column("payment", width=130, anchor="center")

        # Stilimi i Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background=ACCENT_COLOR, foreground="white")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_orders.yview)
        self.tree_orders.configure(yscrollcommand=scrollbar.set)
        self.tree_orders.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Butonat e Veprimeve poshtë tabelës
        action_bar = ctk.CTkFrame(self.tab_orders, fg_color="transparent")
        action_bar.pack(fill="x", padx=10, pady=10)

        btn_view_receipt = ctk.CTkButton(
            action_bar,
            text="🧾 Shiko Faturën",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.view_selected_receipt
        )
        btn_view_receipt.pack(side="left", padx=5)

        btn_set_prep = ctk.CTkButton(
            action_bar,
            text="⏳ Në Përgatitje",
            fg_color=WARNING_COLOR,
            hover_color=WARNING_HOVER,
            command=lambda: self.change_selected_order_status("Në Përgatitje")
        )
        btn_set_prep.pack(side="left", padx=5)

        btn_set_ready = ctk.CTkButton(
            action_bar,
            text="✅ Gati për Shërbim",
            fg_color=SUCCESS_COLOR,
            hover_color=SUCCESS_HOVER,
            command=lambda: self.change_selected_order_status("Gati")
        )
        btn_set_ready.pack(side="left", padx=5)

        btn_set_complete = ctk.CTkButton(
            action_bar,
            text="💰 Arkëto / Llogarit Kusurin",
            fg_color="#10b981",
            hover_color="#059669",
            command=self.complete_selected_order
        )
        btn_set_complete.pack(side="left", padx=5)

        btn_delete = ctk.CTkButton(
            action_bar,
            text="🗑️ Fshij Porosinë",
            fg_color=DANGER_COLOR,
            hover_color=DANGER_HOVER,
            command=self.delete_selected_order
        )
        btn_delete.pack(side="right", padx=5)

    def refresh_orders_table(self):
        for item in self.tree_orders.get_children():
            self.tree_orders.delete(item)

        status_filter = self.cmb_order_status.get()
        waiter_filter = self.entry_waiter_filter.get().strip().lower() if hasattr(self, "entry_waiter_filter") else ""
        orders = models.get_orders(status=status_filter, limit=150)

        for o in orders:
            if waiter_filter and waiter_filter not in o["waiter_name"].lower():
                continue

            self.tree_orders.insert("", "end", values=(
                f"#{o['id']}",
                o["created_at"],
                f"Tavolina {o['table_number']}",
                o["waiter_name"],
                f"{o['total_amount']:.2f} €",
                o["status"],
                o["payment_method"]
            ))

    def _get_selected_order_id(self) -> int:
        selected = self.tree_orders.selection()
        if not selected:
            messagebox.showwarning("Kujdes", "Ju lutem përzgjidhni një porosi nga tabela!")
            return 0
        values = self.tree_orders.item(selected[0], "values")
        order_id_str = values[0].replace("#", "")
        return int(order_id_str)

    def change_selected_order_status(self, new_status: str):
        order_id = self._get_selected_order_id()
        if not order_id:
            return
        models.update_order_status(order_id, new_status)
        self.refresh_orders_table()
        self.refresh_tables_view()

    def complete_selected_order(self):
        order_id = self._get_selected_order_id()
        if not order_id:
            return
        order = models.get_order_by_id(order_id)
        if not order:
            return

        dialog = PaymentWithChangeDialog(self, float(order["total_amount"]), order_id)
        if not dialog.result:
            return

        payment_method = dialog.result["method"]
        inv_num = models.complete_and_pay_order(order_id, payment_method)
        messagebox.showinfo("Arkëtuar", f"✅ Porosia #{order_id} u përfundua me sukses me {payment_method}!\nLëshuar Fatura: {inv_num}")
        self.refresh_orders_table()
        self.refresh_tables_view()
        self.refresh_stats_view()

    def delete_selected_order(self):
        order_id = self._get_selected_order_id()
        if not order_id:
            return
        if messagebox.askyesno("Konfirmim Fshirjeje", f"A jeni të sigurt që dëshironi ta fshini plotësisht Porosinë #{order_id}?"):
            success = models.delete_order(order_id)
            if success:
                messagebox.showinfo("Fshirë", f"Porosia #{order_id} u fshi me sukses!")
                self.refresh_orders_table()
                self.refresh_tables_view()
                self.refresh_stats_view()
            else:
                messagebox.showerror("Gabim", "Dështoi fshirja e porosisë!")

    def clear_all_orders_gui(self):
        if messagebox.askyesno("PARALAJMËRIM", "A jeni të sigurt që dëshironi të fshini TË GJITHA porositë dhe faturat nga sistemi?\nKjo do të resetoje të gjitha tavolinat në të lira."):
            models.clear_all_orders()
            messagebox.showinfo("Pastruar", "Të gjitha porositë u fshinë me sukses! Sistemi u resetua në 0.")
            self.refresh_orders_table()
            self.refresh_tables_view()
            self.refresh_stats_view()

    def view_selected_receipt(self):
        order_id = self._get_selected_order_id()
        if not order_id:
            return
        order = models.get_order_by_id(order_id)
        if not order:
            return
        receipt_text = generate_text_receipt(order)
        ReceiptPreviewDialog(self, receipt_text)

    # ============================================================
    # TAB 3: TAVOLINAT (TABLES VIEW)
    # ============================================================

    def _build_tables_tab(self):
        top_bar = ctk.CTkFrame(self.tab_tables, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)

        lbl_info = ctk.CTkLabel(
            top_bar,
            text="Gjendja e Tavolinave në Kohë Reale (E Gjelbër = E Lirë, E Kuqe = E Zënë me Faturë Aktive)",
            font=FONT_SUBTITLE
        )
        lbl_info.pack(side="left")

        btn_refresh = ctk.CTkButton(
            top_bar,
            text="🔄 Rifresko",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.refresh_tables_view
        )
        btn_refresh.pack(side="right")

        self.scroll_tables = ctk.CTkScrollableFrame(self.tab_tables)
        self.scroll_tables.pack(fill="both", expand=True, padx=10, pady=5)
        self.refresh_tables_view()

    def refresh_tables_view(self):
        for w in self.scroll_tables.winfo_children():
            w.destroy()

        tables = models.get_tables()
        cols = 4

        for idx, t in enumerate(tables):
            row = idx // cols
            col = idx % cols

            is_occupied = t["status"] == "e_zene"
            border_col = DANGER_COLOR if is_occupied else SUCCESS_COLOR

            card = ctk.CTkFrame(self.scroll_tables, border_width=2, border_color=border_col, corner_radius=10)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.scroll_tables.grid_columnconfigure(col, weight=1)

            lbl_num = ctk.CTkLabel(card, text=f"Tavolina {t['table_number']}", font=FONT_TITLE)
            lbl_num.pack(pady=(12, 4))

            lbl_sec = ctk.CTkLabel(card, text=f"{t['section']} ({t['capacity']} vende)", font=FONT_BODY, text_color="gray")
            lbl_sec.pack(pady=(0, 8))

            if is_occupied and t.get("active_order"):
                ord_info = t["active_order"]
                lbl_waiter = ctk.CTkLabel(card, text=f"👤 {ord_info['waiter_name']}", font=FONT_BODY_BOLD)
                lbl_waiter.pack()

                lbl_tot = ctk.CTkLabel(card, text=f"Totali: {ord_info['total_amount']:.2f} €", font=FONT_SUBTITLE, text_color=DANGER_COLOR)
                lbl_tot.pack(pady=4)
            else:
                lbl_free = ctk.CTkLabel(card, text="E LIRË", font=FONT_BODY_BOLD, text_color=SUCCESS_COLOR)
                lbl_free.pack(pady=12)

    # ============================================================
    # TAB 4: MENAXHIMI I MENYSË (MENU CRUD)
    # ============================================================

    def _build_menu_tab(self):
        top_bar = ctk.CTkFrame(self.tab_menu, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)

        btn_add = ctk.CTkButton(
            top_bar,
            text="➕ Shto Artikull të Ri",
            fg_color=SUCCESS_COLOR,
            hover_color=SUCCESS_HOVER,
            command=self.open_add_item_dialog
        )
        btn_add.pack(side="left", padx=(0, 10))

        btn_delete = ctk.CTkButton(
            top_bar,
            text="🗑️ Fshij Artikullin",
            fg_color=DANGER_COLOR,
            hover_color=DANGER_HOVER,
            command=self.delete_selected_menu_item
        )
        btn_delete.pack(side="left")

        btn_refresh = ctk.CTkButton(
            top_bar,
            text="🔄 Rifresko Menynë",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.refresh_menu_tree
        )
        btn_refresh.pack(side="right")

        tree_frame = ctk.CTkFrame(self.tab_menu)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "name", "category", "price", "stock", "description")
        self.tree_menu = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)

        self.tree_menu.heading("id", text="ID")
        self.tree_menu.heading("name", text="Emri i Artikullit")
        self.tree_menu.heading("category", text="Kategoria")
        self.tree_menu.heading("price", text="Çmimi")
        self.tree_menu.heading("stock", text="Stoku")
        self.tree_menu.heading("description", text="Përshkrimi")

        self.tree_menu.column("id", width=60, anchor="center")
        self.tree_menu.column("name", width=240)
        self.tree_menu.column("category", width=120, anchor="center")
        self.tree_menu.column("price", width=100, anchor="center")
        self.tree_menu.column("stock", width=100, anchor="center")
        self.tree_menu.column("description", width=250)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_menu.yview)
        self.tree_menu.configure(yscrollcommand=scrollbar.set)
        self.tree_menu.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.refresh_menu_tree()

    def refresh_menu_tree(self):
        for item in self.tree_menu.get_children():
            self.tree_menu.delete(item)

        items = models.get_menu_items(active_only=True)
        for it in items:
            self.tree_menu.insert("", "end", values=(
                f"#{it['id']}",
                it["name"],
                it["category_name"],
                f"{it['price']:.2f} €",
                it["stock_quantity"],
                it["description"] or "-"
            ))

    def open_add_item_dialog(self):
        cats = models.get_categories()
        dialog = AddItemDialog(self, cats)
        if dialog.result:
            models.add_menu_item(
                name=dialog.result["name"],
                category_id=dialog.result["category_id"],
                price=dialog.result["price"],
                stock_quantity=dialog.result["stock_quantity"],
                description=dialog.result["description"]
            )
            messagebox.showinfo("Sukses", f"Artikulli '{dialog.result['name']}' u shtua me sukses!")
            self.refresh_menu_tree()
            self.load_menu_items()

    def delete_selected_menu_item(self):
        selected = self.tree_menu.selection()
        if not selected:
            messagebox.showwarning("Kujdes", "Ju lutem përzgjidhni një artikull nga tabela!")
            return
        values = self.tree_menu.item(selected[0], "values")
        item_id = int(values[0].replace("#", ""))
        item_name = values[1]

        if messagebox.askyesno("Konfirmim", f"A jeni të sigurt që dëshironi ta fshini artikullin '{item_name}'?"):
            models.delete_menu_item(item_id)
            self.refresh_menu_tree()
            self.load_menu_items()

    # ============================================================
    # TAB 5: STATISTIKAT DITORE (ANALYTICS)
    # ============================================================

    def _build_stats_tab(self):
        top_bar = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=10)

        lbl_title = ctk.CTkLabel(top_bar, text="Pasqyra Financiare dhe Shitjet e Ditës", font=FONT_TITLE)
        lbl_title.pack(side="left")

        btn_refresh = ctk.CTkButton(
            top_bar,
            text="🔄 Rifresko Statistikat",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            command=self.refresh_stats_view
        )
        btn_refresh.pack(side="right")

        # Kartat e numrave
        cards_frame = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.card_revenue = self._create_stat_card(cards_frame, "XHIROJA TOTALE DITORE", "0.00 €", SUCCESS_COLOR)
        self.card_revenue.pack(side="left", expand=True, fill="x", padx=5)

        self.card_orders = self._create_stat_card(cards_frame, "NUMRI I POROSIVE", "0", PRIMARY_COLOR)
        self.card_orders.pack(side="left", expand=True, fill="x", padx=5)

        self.card_avg = self._create_stat_card(cards_frame, "MESATARJA PËR POROSI", "0.00 €", WARNING_COLOR)
        self.card_avg.pack(side="left", expand=True, fill="x", padx=5)

        # Zona e tekstit për detajet
        self.txt_stats = ctk.CTkTextbox(self.tab_stats, font=FONT_RECEIPT, height=350)
        self.txt_stats.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_stats_view()

    def _create_stat_card(self, parent, label_text: str, default_val: str, color: str):
        card = ctk.CTkFrame(parent, corner_radius=10)
        lbl_sub = ctk.CTkLabel(card, text=label_text, font=("Segoe UI", 11, "bold"), text_color="gray")
        lbl_sub.pack(pady=(12, 4))
        lbl_main = ctk.CTkLabel(card, text=default_val, font=FONT_TOTAL, text_color=color)
        lbl_main.pack(pady=(0, 12))
        card.main_label = lbl_main
        return card

    def refresh_stats_view(self):
        stats = models.get_daily_statistics()
        self.card_revenue.main_label.configure(text=f"{stats['total_revenue']:.2f} €")
        self.card_orders.main_label.configure(text=str(stats['total_orders']))
        self.card_avg.main_label.configure(text=f"{stats['average_order']:.2f} €")

        lines = []
        lines.append("=" * 60)
        lines.append(f"STATISTIKAT FINANCIARE DITORE - {stats['date']}")
        lines.append("=" * 60)
        lines.append(f"Xhiroja Totale:        {stats['total_revenue']:.2f} €")
        lines.append(f"Numri i Porosive:      {stats['total_orders']}")
        lines.append(f"Mesatarja për Faturë:  {stats['average_order']:.2f} €")
        lines.append("-" * 60)
        lines.append("TOP 5 ARTIKUJT MË TË SHITUR:")
        for idx, item in enumerate(stats["popular_items"], 1):
            lines.append(f" {idx}. {item['item_name']:<30} {item['total_qty']} copë | {item['total_sum']:.2f}€")
        lines.append("-" * 60)
        lines.append("XHIROJA DHE POROSITË SIPAS ÇDO KAMARIERI:")
        if not stats.get("waiter_stats"):
            lines.append(" Nuk ka shitje të regjistruara për kamarierët në këtë datë.")
        else:
            for w in stats["waiter_stats"]:
                pct = (w["total_sales"] / stats["total_revenue"] * 100) if stats["total_revenue"] > 0 else 0
                lines.append(f" • {w['waiter_name']:<22} {w['total_orders']:>3} porosi | {w['total_sales']:>8.2f}€ ({pct:>5.1f}%) | Mes: {w['average_sales']:>5.2f}€")
        lines.append("-" * 60)
        lines.append("DETAJET E POROSIVE TË DITËS:")
        for o in stats["orders"]:
            time_part = o['created_at'].split(' ')[1] if ' ' in o['created_at'] else o['created_at']
            lines.append(f" #{o['id']:<4} {time_part} | Tavolina {o['table_number']:<2} | {o['waiter_name']:<18} | {o['total_amount']:>7.2f}€ | {o['status']}")
        lines.append("=" * 60)

        self.txt_stats.configure(state="normal")
        self.txt_stats.delete("1.0", "end")
        self.txt_stats.insert("1.0", "\n".join(lines))
        self.txt_stats.configure(state="disabled")


def start_desktop_app():
    """Nis aplikacionin desktop."""
    app = RestaurantAppGUI()
    app.mainloop()


if __name__ == "__main__":
    start_desktop_app()
