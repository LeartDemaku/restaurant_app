from .db import init_database, get_db_connection

CATEGORIES_DATA = [
    {"name": "Pije", "color": "#2980b9", "icon": "bi-cup-straw", "display_order": 1},
    {"name": "Kafe", "color": "#8d6e63", "icon": "bi-cup-hot", "display_order": 2},
    {"name": "Ushqim", "color": "#e74c3c", "icon": "bi-egg-fried", "display_order": 3},
    {"name": "Embëlsirë", "color": "#e67e22", "icon": "bi-cake2", "display_order": 4},
]

ITEMS_DATA = [
    # --- PIJE ---
    ("Coca Cola 0.33l", 1.50, "Pije", 100, "Pije freskuese e gazuar"),
    ("Coca Cola Zero 0.33l", 1.50, "Pije", 100, "Pa sheqer"),
    ("Fanta Orange 0.33l", 1.50, "Pije", 100, "Shije portokalli"),
    ("Fanta Exotic 0.33l", 1.50, "Pije", 100, "Shije fruta ekzotike"),
    ("Sprite 0.33l", 1.50, "Pije", 100, "Limon-lajm"),
    ("Schweppes Bitter Lemon", 1.70, "Pije", 80, "Pije tonike limon"),
    ("Schweppes Tonic Water", 1.70, "Pije", 80, "Ujë tonik"),
    ("Cockta 0.275l", 1.50, "Pije", 90, "Pije tradicionale bimore"),
    ("Ujë Natyral 0.25l", 1.00, "Pije", 200, "Ujë natyral"),
    ("Ujë Natyral 0.75l", 2.00, "Pije", 100, "Ujë natyral shishe"),
    ("Ujë me Gaz 0.25l", 1.00, "Pije", 200, "Ujë mineral me gaz"),
    ("Ujë me Gaz 0.75l", 2.00, "Pije", 100, "Ujë mineral me gaz"),
    ("Red Bull 0.25l", 2.50, "Pije", 60, "Pije energjike"),
    ("Golden Eagle 0.25l", 1.50, "Pije", 100, "Pije energjike"),
    ("Lëng Portokalli Natyral", 2.00, "Pije", 50, "I shtrydhur i freskët"),
    ("Lëng Mollë 0.2l", 1.50, "Pije", 80, "Lëng peme natyral"),
    ("Lëng Dredhëze 0.2l", 1.50, "Pije", 80, "Lëng luleshtrydhe"),
    ("Lëng Boronice 0.2l", 1.50, "Pije", 80, "Lëng boronice"),
    ("Lëng Pjeshke 0.2l", 1.50, "Pije", 80, "Lëng pjeshke"),
    ("Ice Tea Shqepë", 1.50, "Pije", 90, "Çaj i ftohtë pjeshkë"),
    ("Ice Tea Limon", 1.50, "Pije", 90, "Çaj i ftohtë limon"),
    ("Limonadë Shtëpie", 1.50, "Pije", 70, "Limonadë e përgatitur vetë"),
    ("Limonadë me Boronicë", 2.00, "Pije", 60, "Limonadë me shurup boronice"),
    ("Birrë Peja 0.33l", 1.50, "Pije", 120, "Birrë vendore"),
    ("Birrë Peja Crudo", 2.00, "Pije", 80, "Birrë e pafiltruar"),
    ("Birrë Korçë 0.33l", 1.80, "Pije", 80, "Birrë bjonde/zezë"),
    ("Heineken 0.33l", 2.50, "Pije", 70, "Birrë premium"),
    ("Tuborg 0.33l", 2.20, "Pije", 70, "Birrë importi"),
    ("Somersby Mollë", 2.00, "Pije", 60, "Cidër molle"),
    ("Somersby Boronicë", 2.00, "Pije", 60, "Cidër boronice"),
    ("Verë e Kuqe (Gota)", 3.00, "Pije", 50, "Verë cilësore e kuqe"),
    ("Verë e Bardhë (Gota)", 3.00, "Pije", 50, "Verë cilësore e bardhë"),
    ("Raki Rrushi", 1.50, "Pije", 60, "Raki shtëpie"),
    ("Raki Dardhe", 2.00, "Pije", 40, "Raki tradicionale dardhe"),

    # --- KAFE ---
    ("Espresso Single", 1.00, "Kafe", 200, "Espresso klasike italiane"),
    ("Espresso Double", 1.50, "Kafe", 150, "Dopjo espresso"),
    ("Espresso Macchiato", 1.00, "Kafe", 200, "Me pak qumësht"),
    ("Macchiato e Madhe", 1.20, "Kafe", 200, "Macchiato në gotë të madhe"),
    ("Macchiato e Vogël", 1.00, "Kafe", 200, "Macchiato tradicionale"),
    ("Cappuccino", 1.30, "Kafe", 150, "Me shkumë qumështi"),
    ("Caffe Latte", 1.50, "Kafe", 150, "Qumësht me pak kafe"),
    ("Latte Macchiato", 1.50, "Kafe", 120, "Latte me shtresa"),
    ("Americano", 1.20, "Kafe", 100, "Espresso e zgjatur"),
    ("Nescafé Classic", 1.20, "Kafe", 100, "Nescafé e nxehtë"),
    ("Nescafé 3in1", 1.20, "Kafe", 100, "Nescafé e ëmbël"),
    ("Freddo Espresso", 1.80, "Kafe", 80, "Espresso e ftohtë me akull"),
    ("Freddo Cappuccino", 2.00, "Kafe", 80, "Cappuccino e ftohtë me shkumë"),
    ("Ice Coffee me Akullore", 2.50, "Kafe", 60, "Kafe e ftohtë me top akullore"),
    ("Kafe Turke", 1.00, "Kafe", 150, "Kafe tradicionale në xhezve"),
    ("Mocha me Çokollatë", 2.00, "Kafe", 70, "Kafe me çokollatë"),
    ("Kafe me Caramel", 1.80, "Kafe", 70, "Me shurup karameli"),
    ("Kafe me Vanilje", 1.80, "Kafe", 70, "Me shurup vanilje"),
    ("Çaj me Bimë Të Ndryshme", 1.00, "Kafe", 150, "Kamomil, mente, boronicë"),
    ("Çaj me Limon e Mjaltë", 1.20, "Kafe", 150, "Çaj shërues"),
    ("Çaj i Zi", 1.00, "Kafe", 150, "Çaj rusi klasik"),
    ("Çokollatë e Ngrohtë e Bardhë", 1.80, "Kafe", 80, "Cremoso bardhë"),
    ("Çokollatë e Ngrohtë e Zezë", 1.80, "Kafe", 80, "Cremoso zezë"),

    # --- USHQIM ---
    ("Sufllaqe me Pule", 3.00, "Ushqim", 80, "File pule, patate, salcë, sallatë"),
    ("Sufllaqe me Mish Vjeçi", 3.50, "Ushqim", 70, "Mish vjeçi cilësor"),
    ("Sufllaqe Mix", 4.00, "Ushqim", 60, "Pulë dhe viç miks"),
    ("Doner në Kifle", 3.00, "Ushqim", 90, "Doner me kifle të freskët"),
    ("Doner Pjatë me Patate", 4.50, "Ushqim", 70, "Pjatë e pasur me doner"),
    ("Pleskavicë Sharri", 4.50, "Ushqim", 50, "E mbushur me kaçkavall"),
    ("Pleskavicë e Mbushur", 5.00, "Ushqim", 50, "Kaçkavall dhe proshutë"),
    ("Qebapa (10 copë)", 4.00, "Ushqim", 100, "Qebapa tradicionalë me samun"),
    ("Qebapa (5 copë)", 2.50, "Ushqim", 100, "Gjysmë porcie"),
    ("File Pule në Skarë", 4.50, "Ushqim", 60, "Servuar me perime dhe patate"),
    ("File Pule me Salcë Kërpudhash", 5.50, "Ushqim", 40, "Në krem kërpudhash"),
    ("Biftek Vjeçi", 12.00, "Ushqim", 20, "Biftek premium në skarë"),
    ("Ramstek Vjeçi", 9.50, "Ushqim", 25, "Ramstek me erëza"),
    ("Pica Margarita", 3.50, "Ushqim", 60, "Salcë domate, mocarela"),
    ("Pica Vesuvio", 4.00, "Ushqim", 60, "Mocarela, proshutë"),
    ("Pica Capricciosa", 4.50, "Ushqim", 60, "Proshutë, kërpudha"),
    ("Pica Pepperoni", 5.00, "Ushqim", 50, "Suxhuk djegës pepperoni"),
    ("Pica Shtëpisë", 5.50, "Ushqim", 50, "Përbërës specialë të shtëpisë"),
    ("Pica Quattro Formaggi", 5.00, "Ushqim", 40, "4 lloje djathërash"),
    ("Hamburger Klasik", 2.50, "Ushqim", 80, "Mish viçi, sallatë, salca"),
    ("Cheeseburger", 3.00, "Ushqim", 80, "Me djathë çedar"),
    ("Double Burger", 4.00, "Ushqim", 60, "Dy qofte viçi"),
    ("Chicken Burger", 3.00, "Ushqim", 70, "Pule krokante"),
    ("Sanduiç me Proshutë", 2.00, "Ushqim", 90, "Bukë e freskët, proshutë, kaçkavall"),
    ("Sanduiç me Pulë", 2.50, "Ushqim", 90, "File pule, salcë majoneze"),
    ("Sanduiç Ton", 2.50, "Ushqim", 60, "Peshk ton, misër, ullinj"),
    ("Toast me Djathë e Proshutë", 1.50, "Ushqim", 100, "Toast klasik"),
    ("Pasta Bolognese", 4.00, "Ushqim", 50, "Salcë me mish të grirë"),
    ("Pasta Carbonara", 4.50, "Ushqim", 50, "Panketë, vezë, parmezan"),
    ("Pasta Penne Arrabbiata", 4.00, "Ushqim", 40, "Salcë domate pikante"),
    ("Risotto me Kërpudha", 4.50, "Ushqim", 30, "Oriz italian me kërpudha"),
    ("Risotto me Pulë", 4.50, "Ushqim", 30, "Oriz me copëza pule"),
    ("Sallatë Cezar", 3.50, "Ushqim", 50, "Pulë, marule, krutonë, dresing"),
    ("Sallatë Greke", 3.00, "Ushqim", 50, "Domate, tranguj, djathë fete"),
    ("Sallatë me Ton", 3.50, "Ushqim", 40, "Peshk ton, sallatë e gjelbër"),
    ("Sallatë Shopska", 2.50, "Ushqim", 60, "Domate, kastravec, djathë bardhë"),
    ("Patate të Fritura", 1.50, "Ushqim", 150, "Patate të skuqura krokante"),
    ("Patate me Djathë Kaçkavall", 2.00, "Ushqim", 100, "Patate me kaçkavall të shkrirë"),
    ("Skedë me Djathë të Bardhë", 2.00, "Ushqim", 80, "Me vaj ulliri dhe rigon"),
    ("Supë me Pulë", 2.00, "Ushqim", 60, "Supë e ngrohtë shtëpie"),
    ("Supë me Perime", 2.00, "Ushqim", 60, "Perime të freskëta"),
    ("Supë Peshku", 2.50, "Ushqim", 40, "Supë tradicionale deti"),

    # --- EMBËLSIRË ---
    ("Trileçe", 1.50, "Embëlsirë", 50, "Trileçe tradicionale me karamel"),
    ("Bakllavë Tradicionale", 2.00, "Embëlsirë", 40, "Bakllavë me arra"),
    ("Tiramisu", 2.50, "Embëlsirë", 35, "Tiramisu italiane"),
    ("Cheesecake me Fruta Mali", 2.50, "Embëlsirë", 30, "Cheesecake i freskët"),
    ("Cheesecake me Nutella", 2.50, "Embëlsirë", 30, "Cheesecake me çokollatë"),
    ("Tortë me Çokollatë", 2.50, "Embëlsirë", 40, "Peshk çokollate"),
    ("Soufflé me Çokollatë", 3.00, "Embëlsirë", 25, "Lava cake e ngrohtë"),
    ("Sufle me Akullore", 3.50, "Embëlsirë", 25, "Soufflé me vanilje akullore"),
    ("Pulla me Nutella", 2.50, "Embëlsirë", 40, "Petulla të ngrohta"),
    ("Pulla me Mjaltë e Arra", 2.50, "Embëlsirë", 40, "Pulla tradicionale"),
    ("Crepes me Nutella", 2.00, "Embëlsirë", 50, "Petulla franceze"),
    ("Crepes me Banana e Nutella", 2.50, "Embëlsirë", 50, "Kombinim klasik"),
    ("Panna Cotta", 2.00, "Embëlsirë", 30, "Me lëng frutash mali"),
    ("Krofne me Çokollatë", 1.20, "Embëlsirë", 60, "Krofne e butë"),
    ("Akullore (1 Top)", 0.80, "Embëlsirë", 100, "Shije të ndryshme"),
    ("Akullore Kupë miks", 2.50, "Embëlsirë", 40, "Kupë me 3 topa dhe shurup"),
    ("Oreo Milkshake", 2.50, "Embëlsirë", 40, "Me biskota Oreo"),
    ("Dredhëz Milkshake", 2.50, "Embëlsirë", 40, "Me luleshtrydhe"),
    ("Vanilla Milkshake", 2.50, "Embëlsirë", 40, "Shije klasike vanilje"),
    ("Çokollatë Milkshake", 2.50, "Embëlsirë", 40, "Shije e thellë çokollate"),
]

STAFF_DATA = [
    ("Menaxheri", "menaxher", "0000"),
    ("Ardit (Kamarier)", "kamarier", "1111"),
    ("Besa (Kamariere)", "kamarier", "2222"),
    ("Ekrani Kuzhinës", "kuzhine", "3333"),
]


def seed_database(force: bool = False):
    """Populon bazën e të dhënave me artikujt dhe konfigurimet fillestare."""
    init_database()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Kontrollojmë a ka tashmë artikuj
    count = cursor.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count > 0 and not force:
        conn.close()
        return

    print("Po popullohen të dhënat fillestare...")

    # 1. Kategoritë
    cat_id_map = {}
    for cat in CATEGORIES_DATA:
        cursor.execute(
            """INSERT OR REPLACE INTO categories (name, color, icon, display_order)
               VALUES (?, ?, ?, ?)""",
            (cat["name"], cat["color"], cat["icon"], cat["display_order"])
        )
        # Gjejmë ID-në
        c_id = cursor.execute("SELECT id FROM categories WHERE name = ?", (cat["name"],)).fetchone()[0]
        cat_id_map[cat["name"]] = c_id

    # 2. Artikujt e menysë
    for item in ITEMS_DATA:
        name, price, cat_name, stock, desc = item
        cat_id = cat_id_map.get(cat_name, 1)
        cursor.execute(
            """INSERT INTO menu_items (name, category_id, price, stock_quantity, description, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (name, cat_id, price, stock, desc)
        )

    # 3. Tavolinat (1 deri 16)
    for i in range(1, 17):
        capacity = 2 if i in (1, 2) else (6 if i in (15, 16) else 4)
        section = "Verandë" if i > 12 else "Salla Kryesore"
        cursor.execute(
            """INSERT OR IGNORE INTO restaurant_tables (table_number, capacity, section, status)
               VALUES (?, ?, ?, 'e_lire')""",
            (i, capacity, section)
        )

    # 4. Stafi
    for name, role, pin in STAFF_DATA:
        cursor.execute(
            """INSERT OR IGNORE INTO staff (name, role, pin_code, is_active)
               VALUES (?, ?, ?, 1)""",
            (name, role, pin)
        )

    conn.commit()
    conn.close()
    print(f"U importuan me sukses {len(ITEMS_DATA)} artikuj, 16 tavolina dhe stafi!")


if __name__ == "__main__":
    seed_database(force=True)
