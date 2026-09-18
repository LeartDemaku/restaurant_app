import customtkinter as ctk
from typing import Optional, Dict, Any, List
from .theme import *


class OrderSaveDialog(ctk.CTkToplevel):
    """Dritare modale per zgjedhjen e tavolines dhe kamarierit para ruajtjes se porosise."""

    def __init__(self, parent, tables: List[Dict[str, Any]], staff: List[Dict[str, Any]]):
        super().__init__(parent)
        self.title("Konfirmo Porosinë")
        self.geometry("400x420")
        self.resizable(False, False)
        self.result = None

        # E mbajmë sipër
        self.transient(parent)
        self.grab_set()

        # Titulli
        lbl_title = ctk.CTkLabel(self, text="Të Dhënat e Porosisë", font=FONT_TITLE)
        lbl_title.pack(pady=(16, 12))

        # Zgjedhja e Tavolinës
        lbl_table = ctk.CTkLabel(self, text="Numri i Tavolinës:", font=FONT_BODY_BOLD)
        lbl_table.pack(anchor="w", padx=30, pady=(6, 2))
        table_options = [f"Tavolina {t['table_number']} ({t['section']})" for t in tables]
        self.cmb_table = ctk.CTkComboBox(self, values=table_options, width=340)
        self.cmb_table.pack(padx=30, pady=(0, 10))

        # Shkrimi i Emrit të Kamarierit
        lbl_waiter = ctk.CTkLabel(self, text="Emri i Kamarierit:", font=FONT_BODY_BOLD)
        lbl_waiter.pack(anchor="w", padx=30, pady=(6, 2))
        self.entry_waiter = ctk.CTkEntry(self, placeholder_text="Shkruani emrin e kamarierit (p.sh. Ardit)...", width=340)
        self.entry_waiter.pack(padx=30, pady=(0, 10))

        # Mënyra e Pagesës
        lbl_payment = ctk.CTkLabel(self, text="Mënyra e Pagesës:", font=FONT_BODY_BOLD)
        lbl_payment.pack(anchor="w", padx=30, pady=(6, 2))
        self.cmb_payment = ctk.CTkComboBox(self, values=["Kesh", "Kartelë"], width=340)
        self.cmb_payment.pack(padx=30, pady=(0, 10))

        # Shënime
        lbl_notes = ctk.CTkLabel(self, text="Shënime (opsionale):", font=FONT_BODY)
        lbl_notes.pack(anchor="w", padx=30, pady=(6, 2))
        self.entry_notes = ctk.CTkEntry(self, placeholder_text="p.sh. Pa kripë, kafe pa sheqer", width=340)
        self.entry_notes.pack(padx=30, pady=(0, 16))

        # Butonat
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(10, 16))

        btn_cancel = ctk.CTkButton(btn_frame, text="Anulo", fg_color=DANGER_COLOR, hover_color=DANGER_HOVER, width=150, command=self.on_cancel)
        btn_cancel.pack(side="left", padx=(0, 10))

        btn_confirm = ctk.CTkButton(btn_frame, text="Ruaj Porosinë", fg_color=SUCCESS_COLOR, hover_color=SUCCESS_HOVER, width=150, command=self.on_confirm)
        btn_confirm.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window()

    def on_confirm(self):
        waiter = self.entry_waiter.get().strip()
        if not waiter:
            from tkinter import messagebox
            messagebox.showwarning("Kujdes", "Emri i kamarierit është i detyrueshëm!")
            self.entry_waiter.focus_set()
            return

        table_raw = self.cmb_table.get()
        import re
        m = re.search(r"Tavolina\s+(\d+)", table_raw)
        table_num = int(m.group(1)) if m else 1

        payment = self.cmb_payment.get()
        notes = self.entry_notes.get().strip()

        self.result = {
            "table_number": table_num,
            "waiter_name": waiter,
            "payment_method": payment,
            "notes": notes
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class ReceiptPreviewDialog(ctk.CTkToplevel):
    """Dritare modale per shfaqjen e fatures dhe mundesi printimi."""

    def __init__(self, parent, receipt_text: str):
        super().__init__(parent)
        self.title("Fatura e Restorantit")
        self.geometry("440x560")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="Pamja e Faturës (Thermal 80mm)", font=FONT_TITLE)
        lbl_title.pack(pady=(14, 10))

        self.txt_box = ctk.CTkTextbox(self, font=FONT_RECEIPT, width=400, height=420)
        self.txt_box.pack(padx=20, pady=5)
        self.txt_box.insert("1.0", receipt_text)
        self.txt_box.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=12)

        btn_close = ctk.CTkButton(btn_frame, text="Mbyll", fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, command=self.destroy)
        btn_close.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_print = ctk.CTkButton(btn_frame, text="🖨️ Printo", fg_color=SUCCESS_COLOR, hover_color=SUCCESS_HOVER, command=self.on_print)
        btn_print.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def on_print(self):
        try:
            import tempfile, os
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
                f.write(self.txt_box.get("1.0", "end"))
                filepath = f.name
            os.startfile(filepath, "print")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showinfo("Printo", "Fatura u dërgua te printeri i parazgjedhur në Windows.")


class AddItemDialog(ctk.CTkToplevel):
    """Dritare modale per shtimin e nje artikulli te ri nga Desktop GUI."""

    def __init__(self, parent, categories: List[Dict[str, Any]]):
        super().__init__(parent)
        self.title("Shto Artikull të Ri")
        self.geometry("400x420")
        self.resizable(False, False)
        self.result = None
        self.categories = categories

        self.transient(parent)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text="Artikull i Ri në Meny", font=FONT_TITLE)
        lbl_title.pack(pady=(16, 12))

        lbl_name = ctk.CTkLabel(self, text="Emri i Artikullit:", font=FONT_BODY_BOLD)
        lbl_name.pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_name = ctk.CTkEntry(self, placeholder_text="p.sh. Pica Rustica", width=340)
        self.entry_name.pack(padx=30, pady=(0, 8))

        lbl_cat = ctk.CTkLabel(self, text="Kategoria:", font=FONT_BODY_BOLD)
        lbl_cat.pack(anchor="w", padx=30, pady=(4, 2))
        cat_names = [c["name"] for c in categories]
        self.cmb_cat = ctk.CTkComboBox(self, values=cat_names, width=340)
        self.cmb_cat.pack(padx=30, pady=(0, 8))

        lbl_price = ctk.CTkLabel(self, text="Çmimi (€):", font=FONT_BODY_BOLD)
        lbl_price.pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_price = ctk.CTkEntry(self, placeholder_text="p.sh. 3.50", width=340)
        self.entry_price.pack(padx=30, pady=(0, 8))

        lbl_stock = ctk.CTkLabel(self, text="Sasia në Stok:", font=FONT_BODY_BOLD)
        lbl_stock.pack(anchor="w", padx=30, pady=(4, 2))
        self.entry_stock = ctk.CTkEntry(self, placeholder_text="100", width=340)
        self.entry_stock.insert(0, "100")
        self.entry_stock.pack(padx=30, pady=(0, 16))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(6, 16))

        btn_cancel = ctk.CTkButton(btn_frame, text="Anulo", fg_color=DANGER_COLOR, hover_color=DANGER_HOVER, width=150, command=self.destroy)
        btn_cancel.pack(side="left", padx=(0, 10))

        btn_save = ctk.CTkButton(btn_frame, text="Ruaj", fg_color=SUCCESS_COLOR, hover_color=SUCCESS_HOVER, width=150, command=self.on_save)
        btn_save.pack(side="right")

        self.wait_window()

    def on_save(self):
        name = self.entry_name.get().strip()
        cat_name = self.cmb_cat.get()
        price_str = self.entry_price.get().strip()
        stock_str = self.entry_stock.get().strip()

        if not name:
            return

        try:
            price = float(price_str)
            stock = int(stock_str) if stock_str else 100
        except ValueError:
            return

        # Gjejmë id e kategorise
        cat_id = 1
        for c in self.categories:
            if c["name"] == cat_name:
                cat_id = c["id"]
                break

        self.result = {
            "name": name,
            "category_id": cat_id,
            "price": price,
            "stock_quantity": stock,
            "description": ""
        }
        self.destroy()


class PaymentWithChangeDialog(ctk.CTkToplevel):
    """Dritare modale per arketim me llogarites te integruar te kusurit."""

    def __init__(self, parent, total_amount: float, order_id: int):
        super().__init__(parent)
        self.title(f"Arkëtimi i Porosisë #{order_id}")
        self.geometry("440x490")
        self.resizable(False, False)
        self.total = total_amount
        self.order_id = order_id
        self.result = None

        self.transient(parent)
        self.grab_set()

        lbl_title = ctk.CTkLabel(self, text=f"Arkëtimi - Porosia #{order_id}", font=FONT_TITLE)
        lbl_title.pack(pady=(16, 10))

        # Paneli i Totalit
        frame_tot = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=10)
        frame_tot.pack(fill="x", padx=30, pady=(0, 12))

        lbl_sub = ctk.CTkLabel(frame_tot, text="TOTALI PËR PAGESË", font=("Segoe UI", 11, "bold"), text_color="gray")
        lbl_sub.pack(pady=(10, 2))

        self.lbl_big_total = ctk.CTkLabel(frame_tot, text=f"{self.total:.2f} €", font=FONT_TOTAL, text_color="#0f172a")
        self.lbl_big_total.pack(pady=(0, 10))

        # Butonat e shpejte te keshit
        lbl_quick = ctk.CTkLabel(self, text="Para të Gatshme (Kesh):", font=FONT_BODY_BOLD)
        lbl_quick.pack(anchor="w", padx=30, pady=(4, 2))

        frame_quick = ctk.CTkFrame(self, fg_color="transparent")
        frame_quick.pack(fill="x", padx=30, pady=(0, 10))

        for val in ["E Saktë", "5 €", "10 €", "20 €", "50 €"]:
            btn = ctk.CTkButton(
                frame_quick,
                text=val,
                width=68,
                height=32,
                fg_color="#3b82f6",
                hover_color="#2563eb",
                command=lambda v=val: self.set_quick_cash(v)
            )
            btn.pack(side="left", padx=3)

        # Fusha per shumen e dhene
        lbl_given = ctk.CTkLabel(self, text="Shuma e Dhënë nga Klienti (€):", font=FONT_BODY_BOLD)
        lbl_given.pack(anchor="w", padx=30, pady=(4, 2))

        self.entry_given = ctk.CTkEntry(self, font=("Segoe UI", 16, "bold"), height=40, width=380, justify="center")
        self.entry_given.pack(padx=30, pady=(0, 10))
        self.entry_given.bind("<KeyRelease>", lambda e: self.calculate_change())

        # Paneli i Kusurit
        frame_change = ctk.CTkFrame(self, fg_color="#ecfdf5", border_width=1, border_color="#a7f3d0", corner_radius=8)
        frame_change.pack(fill="x", padx=30, pady=(0, 16))

        self.lbl_change = ctk.CTkLabel(frame_change, text="Kusuri për t'u kthyer: 0.00 €", font=FONT_SUBTITLE, text_color="#059669")
        self.lbl_change.pack(pady=10)

        # Butonat e Pageses
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 12))

        btn_card = ctk.CTkButton(
            btn_frame,
            text="💳 Me Kartelë",
            fg_color="#475569",
            hover_color="#334155",
            width=180,
            height=42,
            command=lambda: self.finish_pay("Kartelë")
        )
        btn_card.pack(side="left", padx=(0, 10))

        btn_cash = ctk.CTkButton(
            btn_frame,
            text="💵 Arkëto me Kesh",
            fg_color=SUCCESS_COLOR,
            hover_color=SUCCESS_HOVER,
            width=180,
            height=42,
            command=lambda: self.finish_pay("Kesh")
        )
        btn_cash.pack(side="right")

        self.entry_given.focus_set()
        self.wait_window()

    def set_quick_cash(self, val_str: str):
        if val_str == "E Saktë":
            self.entry_given.delete(0, "end")
            self.entry_given.insert(0, f"{self.total:.2f}")
        else:
            num = val_str.replace("€", "").strip()
            self.entry_given.delete(0, "end")
            self.entry_given.insert(0, num)
        self.calculate_change()

    def calculate_change(self):
        txt = self.entry_given.get().strip().replace(",", ".")
        try:
            given = float(txt) if txt else 0.0
            change = given - self.total
            if change < 0:
                self.lbl_change.configure(text=f"Mungojnë: {abs(change):.2f} €", text_color="#dc2626")
            else:
                self.lbl_change.configure(text=f"Kusuri për t'u kthyer: {change:.2f} €", text_color="#059669")
        except ValueError:
            self.lbl_change.configure(text="Shkruani një numër të vlefshëm!", text_color="#dc2626")

    def finish_pay(self, method: str):
        self.result = {"method": method}
        self.destroy()
