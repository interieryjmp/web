import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import os
import shutil
import re
from datetime import datetime
import subprocess
from pathlib import Path

# --- 1. NASTAVENÍ A KONSTANTY ---
def t(text):
    return "<" + "!-- " + text + " --" + ">"

SLOZKA_HLAVNI_IMG = "assets/img"
SLOZKA_EXPORT = "export"

# GLOBÁLNÍ PROMĚNNÁ PRO UKLÁDÁNÍ CEST K NOVÝM SOUBORŮM V RÁMCI JEDNOHO SPUŠTĚNÍ
SESSION_NEW_FILES = []
SESSION_CHANGED_FILES = set()  # Sledujeme které HTML se změnily
CURRENT_EXPORT_DIR = None  # Aktuální export složka

FILE_GALERIE = {
    "data": "data_fotogalerie.html",
    "sablona": "sablona_fotogalerie.html",
    "vystup": "fotogalerie.html"
}

FILE_VIDEO = {
    "data": "data_realizace.html",
    "sablona": "sablona_realizace.html",
    "vystup": "realizace.html"
}

KATEGORIE = {
    "Kuchyně":            (t("START KUCHYNE"), t("END KUCHYNE")),
    "Skříně":             (t("START SKRINE"),  t("END SKRINE")),
    "Dětské pokoje":      (t("START POKOJE"),  t("END POKOJE")),
    "Koupelny":           (t("START KOUPELNY"),t("END KOUPELNY")),
    "Studentské pokoje":  (t("START STUDENT"), t("END STUDENT"))
}

CONFIG_VIDEO = {
    "start": t("START REALIZACE"),
    "konec": t("END REALIZACE")
}

# --- 2. POMOCNÉ FUNKCE ---

def otevrit_pruzkumnik(cesta):
    """Otevře složku v průzkumníku Windows."""
    cesta = os.path.abspath(cesta)
    if os.path.exists(cesta):
        subprocess.Popen(f'explorer "{cesta}"')

def ziskej_youtube_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else url

def seznam_dostupnych_exportu():
    """Vrátí seznam všech dostupných exportů seřazených od nejnovějšího."""
    if not os.path.exists(SLOZKA_EXPORT):
        return []
    
    exporty = []
    for polozka in os.listdir(SLOZKA_EXPORT):
        if polozka.startswith("export_") and os.path.isdir(os.path.join(SLOZKA_EXPORT, polozka)):
            exporty.append(polozka)
    
    return sorted(exporty, reverse=True)

def najdi_soubor_v_exportech(nazev_souboru, od_exportu=None):
    """Hledá soubor v exportech od nejnovějšího, počínaje od_exportu."""
    exporty = seznam_dostupnych_exportu()
    
    if od_exportu:
        try:
            index = exporty.index(od_exportu)
            exporty = exporty[index+1:]  # Hledáme v starších
        except ValueError:
            pass
    
    for export in exporty:
        cesta = os.path.join(SLOZKA_EXPORT, export, nazev_souboru)
        if os.path.exists(cesta):
            return cesta
    
    return None

def zpracuj_fotky(cesty):
    """
    1. Přejmenuje a zkopíruje fotky do HLAVNÍ složky webu (assets/img).
    2. Vrátí seznam (cesta_html, absolutni_cesta_k_novemu_souboru).
    """
    if not os.path.exists(SLOZKA_HLAVNI_IMG): os.makedirs(SLOZKA_HLAVNI_IMG)
    
    vystup = []
    
    for c in cesty:
        nazev = os.path.basename(c)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        novy_nazev = f"{ts}_{nazev}"
        
        cilova_cesta_hlavni = os.path.join(SLOZKA_HLAVNI_IMG, novy_nazev)
        
        # Kopírování do hlavní složky webu (trvalé úložiště)
        shutil.copy2(c, cilova_cesta_hlavni)
        
        # Uložíme si info
        cesta_web = f"assets/img/{novy_nazev}"
        vystup.append((cesta_web, cilova_cesta_hlavni))
        
    return vystup

# --- 3. GENERUJ POUZE HLAVNÍ WEB (BEZ EXPORTU) ---

def aktualizovat_hlavni_soubory(config_files):
    """
    Pouze přegeneruje HTML soubor v hlavní složce (např. fotogalerie.html).
    Nesahá na export.
    """
    sablona = config_files["sablona"]
    data = config_files["data"]
    vystup = config_files["vystup"]
    
    if not os.path.exists(sablona):
        messagebox.showerror("Chyba", f"Chybí šablona: {sablona}")
        return False
    if not os.path.exists(data):
        with open(data, "w", encoding="utf-8") as f: f.write("")

    try:
        with open(sablona, "r", encoding="utf-8") as f: sablona_obsah = f.read()
        with open(data, "r", encoding="utf-8") as f: data_obsah = f.read()
        
        if "#####" in sablona_obsah:
            final = sablona_obsah.replace("#####", data_obsah)
        else:
            final = sablona_obsah
        
        # Uložení finálního HTML do hlavní složky
        with open(vystup, "w", encoding="utf-8") as f: f.write(final)
        return True
    except Exception as e:
        messagebox.showerror("Chyba", str(e))
        return False

def vlozit_do_html(files_config, novy_kod, st, en, nove_soubory=None):
    """
    Vloží kód do datového souboru a aktualizuje hlavní HTML.
    Nové soubory (fotky) přidá do globálního seznamu pro pozdější export.
    """
    soubor_dat = files_config["data"]
    if not os.path.exists(soubor_dat):
        with open(soubor_dat, "w", encoding="utf-8") as f: f.write("")

    try:
        with open(soubor_dat, "r", encoding="utf-8") as f: obsah = f.read()
        
        if st in obsah and en in obsah:
            parts_outer = obsah.split(st)
            pre = parts_outer[0]
            rest = parts_outer[1]
            parts_inner = rest.split(en)
            uvnitr = parts_inner[0]
            post = parts_inner[1]

            # Rozlišujeme mezi novými sekcemi a přidáváním do existujících
            if '<div class="galerie-skupina">' in novy_kod and '<div class="galerie-grid">' in novy_kod:
                # Nová galerie-skupina s vlastním gridem
                novy_vnitrek = uvnitr.rstrip() + "\n" + novy_kod
            elif '<img' in novy_kod and '<div' not in novy_kod:
                # Pouze img tagy - vkládáme do poslední galerie-grid
                # Hledáme poslední </div></div> (konec galerie-skupiny)
                posledni_close = uvnitr.rfind('</div></div>')
                if posledni_close != -1:
                    # Vkládáme před uzavírací tagy
                    novy_vnitrek = uvnitr[:posledni_close] + novy_kod + uvnitr[posledni_close:]
                else:
                    # Pokud není galerie, přidáme na konec
                    novy_vnitrek = uvnitr.rstrip() + "\n" + novy_kod
            else:
                # Videa a ostatní - přidáme na konec
                novy_vnitrek = uvnitr.rstrip() + "\n" + novy_kod

            # Uložení dat
            with open(soubor_dat, "w", encoding="utf-8") as f:
                f.write(pre + st + novy_vnitrek + en + post)
            
            # Aktualizace hlavního souboru
            aktualizovat_hlavni_soubory(files_config)
            
            # Záznam změny
            SESSION_CHANGED_FILES.add(files_config["vystup"])
            
            # PŘIDÁNÍ DO SESSION (pro pozdější export)
            if nove_soubory:
                SESSION_NEW_FILES.extend(nove_soubory)
                
            messagebox.showinfo("Uloženo", "Položka přidána. Můžete přidat další, nebo klikněte na 'Exportovat'.")

        else:
            messagebox.showerror("Chyba", f"Chybí sekce {st}")
    except Exception as e:
        messagebox.showerror("Chyba", str(e))

# --- 4. FINÁLNÍ EXPORT (TLAČÍTKO) ---

def provest_finalni_export():
    """
    Vytvoří novou podsložku export_RRRRMMDD_HHMM a zkopíruje tam všechny změny.
    """
    if not SESSION_CHANGED_FILES and not SESSION_NEW_FILES:
        messagebox.showwarning("Upozornění", "Žádné změny k exportu.")
        return
    
    # 1. Vytvořit export folder
    if not os.path.exists(SLOZKA_EXPORT):
        os.makedirs(SLOZKA_EXPORT, exist_ok=True)
    
    # 2. Vytvořit novou podsložku s datumem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = os.path.join(SLOZKA_EXPORT, f"export_{ts}")
    os.makedirs(export_dir, exist_ok=True)
    
    global CURRENT_EXPORT_DIR
    CURRENT_EXPORT_DIR = export_dir
    
    # 3. Zkopírovat změněné HTML soubory (bez data a sablona souborů - nejsou potřeba pro hosting)
    for html_soubor in SESSION_CHANGED_FILES:
        if os.path.exists(html_soubor):
            shutil.copy2(html_soubor, os.path.join(export_dir, os.path.basename(html_soubor)))
    
    # 4. Zkopírovat NASBÍRANÉ fotky (pokud nějaké jsou)
    if SESSION_NEW_FILES:
        export_img_dir = os.path.join(export_dir, "assets", "img")
        os.makedirs(export_img_dir, exist_ok=True)
        pocet = 0
        for _, cesta_zdroj in SESSION_NEW_FILES:
            if os.path.exists(cesta_zdroj):
                shutil.copy2(cesta_zdroj, os.path.join(export_img_dir, os.path.basename(cesta_zdroj)))
                pocet += 1
    
    messagebox.showinfo("Export dokončen", f"Soubory exportovány do:\n{export_dir}")
    otevrit_pruzkumnik(export_dir)
    
    # Vyčistíme seznamy pro další kolo
    SESSION_NEW_FILES.clear()
    SESSION_CHANGED_FILES.clear()

def provest_revert(export_jmeno):
    """
    Vrátí staré soubory z daného exportu. Hledá je postupně v starších,
    pokud nejsou v aktuálním.
    """
    if not os.path.exists(SLOZKA_EXPORT):
        messagebox.showerror("Chyba", "Žádné exporty k dispozici.")
        return
    
    # 1. Vytvořit revert folder
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    revert_dir = os.path.join(SLOZKA_EXPORT, f"revert_{ts}")
    os.makedirs(revert_dir, exist_ok=True)
    
    # 2. Hledat soubory v exportech (postupně od nejnovějšího)
    html_soubory = ["fotogalerie.html", "realizace.html"]
    
    for html in html_soubory:
        cesta_v_exportu = najdi_soubor_v_exportech(html, od_exportu=export_jmeno)
        if cesta_v_exportu:
            shutil.copy2(cesta_v_exportu, os.path.join(revert_dir, html))
            # Také zkopíruj do kmenové složky
            shutil.copy2(cesta_v_exportu, html)
            
            # Najdi a aktualizuj odpovídající data_*.html a sablona_*.html
            if html == "fotogalerie.html":
                # Najdi data a sablonu z exportu
                data_path = najdi_soubor_v_exportech("data_fotogalerie.html", od_exportu=export_jmeno)
                sablona_path = najdi_soubor_v_exportech("sablona_fotogalerie.html", od_exportu=export_jmeno)
                if data_path:
                    shutil.copy2(data_path, "data_fotogalerie.html")
                if sablona_path:
                    shutil.copy2(sablona_path, "sablona_fotogalerie.html")
            
            elif html == "realizace.html":
                data_path = najdi_soubor_v_exportech("data_realizace.html", od_exportu=export_jmeno)
                sablona_path = najdi_soubor_v_exportech("sablona_realizace.html", od_exportu=export_jmeno)
                if data_path:
                    shutil.copy2(data_path, "data_realizace.html")
                if sablona_path:
                    shutil.copy2(sablona_path, "sablona_realizace.html")
    
    messagebox.showinfo("Revert dokončen", f"Soubory obnoveny do:\n{revert_dir}")
    otevrit_pruzkumnik(revert_dir)
    
    # Vyčistíme session
    SESSION_NEW_FILES.clear()
    SESSION_CHANGED_FILES.clear() 

# --- 5. GUI ---

def okno_galerie(parent_window):
    """Okno pro přidávání fotek - vrátí se zpět do menu."""
    win = tk.Toplevel()  # Změněno z parent_window
    win.title("Přidat galerii")
    win.geometry("600x500")
    win.resizable(False, False)
    
    # Styl
    win.configure(bg="#f0f0f0")
    
    ttk.Label(win, text="Vyberte kategorii:", font=("Arial", 10, "bold")).pack(pady=10)
    combo = ttk.Combobox(win, values=list(KATEGORIE.keys()), state="readonly", width=30)
    combo.current(0)
    combo.pack(pady=5)
    
    ttk.Label(win, text="Nadpis pro sekci (volitelné):", font=("Arial", 9)).pack(pady=(15,5))
    e_nadpis = tk.Entry(win, width=40)
    e_nadpis.pack(pady=5)
    
    # Frame pro fotky
    frame_fotky = ttk.Frame(win)
    frame_fotky.pack(pady=15, padx=20, fill="x")
    
    lbl_info = tk.Label(frame_fotky, text="Vybrano: 0 fotek", font=("Arial", 9), fg="#666666")
    lbl_info.pack()
    
    fotky = []
    def btn_vyber():
        nonlocal fotky
        fotky = filedialog.askopenfilenames(
            title="Vyberte fotky",
            filetypes=[("Obrázky", "*.jpg *.jpeg *.png *.gif"), ("Všechny", "*.*")]
        )
        lbl_info.config(text=f"Vybrano: {len(fotky)} fotek")
    
    tk.Button(frame_fotky, text="📁 Nahrát fotky...", command=btn_vyber, 
              bg="#4CAF50", fg="white", font=("Arial", 10), padx=10, pady=5).pack()
    
    def btn_nahrat():
        if not fotky:
            messagebox.showwarning("Upozornění", "Vyberte alespoň jednu fotku.")
            return
        
        kat = combo.get()
        st, en = KATEGORIE[kat]
        
        # Zpracuje fotky, uloží do main a vrátí seznam
        zpracovana_data = zpracuj_fotky(fotky)
        
        imgs = "".join([f'<img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" data-src="{data[0]}" alt="{kat}">\n' for data in zpracovana_data])
        
        # Pokud je zadán nadpis, vytvoříme novu sekci, jinak jen přidáme fotky
        if e_nadpis.get():
            h4 = f"<h4>{e_nadpis.get()}</h4>"
            html = f'<div class="galerie-skupina">{h4}<div class="galerie-grid">{imgs}</div></div>'
        else:
            # Přidáme fotky přímo do existující galerie-grid (bez nového obalu)
            html = imgs
        
        vlozit_do_html(FILE_GALERIE, html, st, en, zpracovana_data)
        win.destroy()

    tk.Button(win, text="✓ Přidat do webu", command=btn_nahrat, 
              bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8).pack(pady=10)
    
    tk.Button(win, text="✕ Zavřít", command=win.destroy, 
              bg="#666666", fg="white", font=("Arial", 10), padx=15, pady=8).pack(pady=5)

def okno_video(parent_window):
    """Okno pro přidávání videa - vrátí se zpět do menu."""
    win = tk.Toplevel()  # Změněno z parent_window
    win.title("Přidat video")
    win.geometry("600x300")
    win.resizable(False, False)
    
    win.configure(bg="#f0f0f0")
    
    ttk.Label(win, text="Zadejte YouTube odkaz:", font=("Arial", 10, "bold")).pack(pady=15)
    e_url = tk.Entry(win, width=50, font=("Arial", 10))
    e_url.pack(pady=10, padx=20)
    
    def potvrdit():
        url = e_url.get().strip()
        if not url:
            messagebox.showwarning("Upozornění", "Zadejte YouTube odkaz.")
            return
        
        vid = ziskej_youtube_id(url)
        html = f"""<div class="video-container">
                <div class="youtube-player" data-id="{vid}"></div>
            </div>"""
        vlozit_do_html(FILE_VIDEO, html, CONFIG_VIDEO["start"], CONFIG_VIDEO["konec"])
        win.destroy()
        
    tk.Button(win, text="✓ Přidat video", command=potvrdit, 
              bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8).pack(pady=10)
    
    tk.Button(win, text="✕ Zavřít", command=win.destroy, 
              bg="#666666", fg="white", font=("Arial", 10), padx=15, pady=8).pack(pady=5)

# --- START ---
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Admin Webu - Správa Obsahu")
    app.geometry("400x480")
    app.resizable(False, False)
    app.configure(bg="#f5f5f5")

    # Hlavní frame
    main_frame = ttk.Frame(app)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Nadpis
    title = tk.Label(main_frame, text="Admin Webu", font=("Arial", 16, "bold"), bg="#f5f5f5")
    title.pack(pady=(0, 20))

    # Sekce 1: Přidat obsah
    sec1 = tk.Label(main_frame, text="1. Přidat obsah", font=("Arial", 11, "bold"), bg="#f5f5f5", fg="#333")
    sec1.pack(anchor="w", pady=(10, 5))

    tk.Button(main_frame, text="▶ Přidat Video", command=lambda: okno_video(app), 
              width=30, bg="#FF6B6B", fg="white", font=("Arial", 10), pady=8).pack(pady=4)

    tk.Button(main_frame, text="▶ Přidat Galerii", command=lambda: okno_galerie(app), 
              width=30, bg="#4ECDC4", fg="white", font=("Arial", 10), pady=8).pack(pady=4)

    ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

    # Sekce 2: Export a Správa
    sec2 = tk.Label(main_frame, text="2. Správa a Export", font=("Arial", 11, "bold"), bg="#f5f5f5", fg="#333")
    sec2.pack(anchor="w", pady=(10, 5))

    btn_export = tk.Button(main_frame, text="✓ EXPORTOVAT ZMĚNY", command=provest_finalni_export, 
                            bg="#2ECC71", fg="white", font=("Arial", 10, "bold"), 
                            height=2, padx=15, pady=10)
    btn_export.pack(pady=5, fill="x")

    def okno_revert():
        """Okno pro výběr exportu k návratu."""
        exporty = seznam_dostupnych_exportu()
        
        if not exporty:
            messagebox.showwarning("Upozornění", "Žádné exporty k dispozici.")
            return
        
        win = tk.Toplevel(app)
        win.title("Vrátit se k exportu")
        win.geometry("400x250")
        win.resizable(False, False)
        win.configure(bg="#f0f0f0")
        
        ttk.Label(win, text="Vyberte export k návratu:", font=("Arial", 10, "bold")).pack(pady=15)
        
        frame_list = ttk.Frame(win)
        frame_list.pack(padx=15, pady=10, fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(frame_list)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame_list, yscrollcommand=scrollbar.set, font=("Arial", 9))
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        for export in exporty:
            listbox.insert("end", export)
        
        def provest():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Upozornění", "Vyberte export.")
                return
            
            vybrany_export = exporty[selection[0]]
            if messagebox.askyesno("Potvrzení", f"Vrátit se k exportu {vybrany_export}?"):
                provest_revert(vybrany_export)
                win.destroy()
        
        tk.Button(win, text="✓ Vrátit se", command=provest, 
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=15, pady=8).pack(pady=15)

    tk.Button(main_frame, text="↶ Vrátit se k exportu", command=okno_revert, 
              width=30, bg="#9B59B6", fg="white", font=("Arial", 10), pady=8).pack(pady=5)

    ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=15)

    # Sekce 3: Info
    sec3 = tk.Label(main_frame, text="ℹ Info", font=("Arial", 9, "italic"), bg="#f5f5f5", fg="#666")
    sec3.pack(anchor="w", pady=(5, 0))

    info_text = tk.Label(main_frame, text="Všechny změny se zaznamenávají.\nKlikněte 'Exportovat' pro uložení na web.", 
                         font=("Arial", 8), bg="#f5f5f5", fg="#999", wraplength=300, justify="left")
    info_text.pack(anchor="w", pady=5)

    app.mainloop()