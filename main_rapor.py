import os
import json
import customtkinter as ctk
from tkinter import messagebox
from fpdf import FPDF
from tkinter import filedialog

# KONFIGURASI GLOBAL
COLOR_LULUS = "#22c55e"
COLOR_TIDAK_LULUS = "#ef4444"

# Konfigurasi dasar
DATA_FILE = "data_siswa.json"
SUBJECTS = ["Matematika", "Bahasa Indonesia", "Bahasa Inggris", "IPA", "IPS"]

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def hitung_rata_status(nilai_dict):
    total = sum(nilai_dict.values()) if nilai_dict else 0
    rata = total / len(nilai_dict) if nilai_dict else 0
    status = "LULUS" if rata >= 75 else "TIDAK LULUS"
    return rata, status

def get_predikat(nilai):
    if nilai >= 90:
        return "A"
    elif nilai >= 80:
        return "B"
    elif nilai >= 70:
        return "C"
    elif nilai >= 60:
        return "D"
    else:
        return "E"

def export_pdf_for_student(nisn, nama, kelas, nilai_dict):
    rata, status = hitung_rata_status(nilai_dict)
    predikat_rata = get_predikat(rata)

    # ===== FILE SAVE DIALOG =====
    safe_name = nama.replace(" ", "_")
    default_filename = f"Rapor_{nisn}_{safe_name}.pdf"

    filepath = filedialog.asksaveasfilename(
        title="Simpan Rapor PDF",
        initialfile=default_filename,
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if not filepath:
        return None

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ===== HEADER =====
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "LAPORAN HASIL BELAJAR SISWA", ln=True, align="C")
        pdf.cell(0, 10, "(RAPOR)", ln=True, align="C")
        pdf.ln(8)

        # ===== IDENTITAS =====
        pdf.set_font("Arial", size=12)

        def info_row(label, value, label_w=40):
            pdf.cell(label_w, 8, label)
            pdf.cell(2, 8, ":")
            pdf.cell(0, 8, str(value), ln=True)

        info_row("Nama Peserta Didik", nama)
        info_row("NISN", nisn)
        info_row("Kelas", kelas)

        pdf.ln(8)

        # ===== TABEL NILAI =====
        COL_NO = 12
        COL_MAPEL = 90
        COL_NILAI = 28
        COL_PRED = 28

        table_width = COL_NO + COL_MAPEL + COL_NILAI + COL_PRED
        start_x = (pdf.w - table_width) / 2

        pdf.set_font("Arial", "B", 12)
        pdf.set_x(start_x)
        pdf.cell(COL_NO, 8, "No", border=1, align="C")
        pdf.cell(COL_MAPEL, 8, "Mata Pelajaran", border=1, align="C")
        pdf.cell(COL_NILAI, 8, "Nilai", border=1, align="C")
        pdf.cell(COL_PRED, 8, "Predikat", border=1, align="C", ln=True)

        pdf.set_font("Arial", size=12)
        for i, (mapel, nilai) in enumerate(nilai_dict.items(), start=1):
            pdf.set_x(start_x)
            pdf.cell(COL_NO, 8, str(i), border=1, align="C")
            pdf.cell(COL_MAPEL, 8, mapel, border=1)
            pdf.cell(COL_NILAI, 8, str(nilai), border=1, align="C")
            pdf.cell(COL_PRED, 8, get_predikat(nilai), border=1, align="C", ln=True)

        pdf.ln(8)

        # ===== RINGKASAN =====
        info_row("Nilai Rata-rata", f"{rata:.2f}")
        info_row("Predikat Rata-rata", predikat_rata)
        info_row("Status Kelulusan", status)

        pdf.output(filepath)
        return filepath

    except Exception as e:
        messagebox.showerror("Error", f"Gagal membuat PDF:\n{e}")
        return None

# GUI App
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class RaporApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Rapor Sederhana")
        self.iconbitmap("logo.ico")
        self.geometry("980x640")
        self.minsize(860, 540)

        self.data = load_data()

        # Layout: sidebar + content frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nswe", padx=(0, 10), pady=10)
        # FIX: agar semua page bisa full resize
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Sidebar buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=0, column=0, padx=12, pady=8, sticky="we")

        self.btn_siswa = ctk.CTkButton(self.sidebar, text="Tambah Siswa", command=self.show_siswa)
        self.btn_siswa.grid(row=1, column=0, padx=12, pady=8, sticky="we")

        self.btn_nilai = ctk.CTkButton(self.sidebar, text="Input Nilai", command=self.show_nilai)
        self.btn_nilai.grid(row=2, column=0, padx=12, pady=8, sticky="we")

        self.btn_search = ctk.CTkButton(self.sidebar, text="Search Siswa", command=self.show_search)
        self.btn_search.grid(row=3, column=0, padx=12, pady=8, sticky="we")

        self.btn_mapel = ctk.CTkButton(self.sidebar, text="Search Mapel", command=self.show_mapel)
        self.btn_mapel.grid(row=4, column=0, padx=12, pady=8, sticky="we")

        self.sidebar_buttons = [
            self.btn_dashboard,
            self.btn_siswa,
            self.btn_nilai,
            self.btn_search,
            self.btn_mapel
        ]
        
        self.COLOR_NORMAL = self.btn_dashboard.cget("fg_color") 
        self.COLOR_ACTIVE = self.btn_dashboard.cget("hover_color")

        # Create pages
        self.pages = {}
        for Page in (DashboardPage, SiswaPage, NilaiPage, SearchPage, MapelPage):
            page = Page(self.content, self)
            self.pages[Page.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_dashboard()
    
    def set_active_sidebar(self, active_btn):
        for btn in self.sidebar_buttons:
            btn.configure(fg_color=self.COLOR_NORMAL)

        active_btn.configure(fg_color=self.COLOR_ACTIVE)

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if page:
            try:
                page.update_contents()
            except Exception:
                pass
            page.tkraise()

    def show_dashboard(self):
        self.show_page("DashboardPage")
        self.set_active_sidebar(self.btn_dashboard)

    def show_siswa(self):
        self.show_page("SiswaPage")
        self.set_active_sidebar(self.btn_siswa)

    def show_nilai(self):
        self.show_page("NilaiPage")
        self.set_active_sidebar(self.btn_nilai)

    def show_search(self):
        self.show_page("SearchPage")
        self.set_active_sidebar(self.btn_search)

    def show_mapel(self):
        self.show_page("MapelPage")
        self.set_active_sidebar(self.btn_mapel)
    # def show_dashboard(self):
    #     self.show_page("DashboardPage")

    # def show_siswa(self):
    #     self.show_page("SiswaPage")

    # def show_nilai(self):
    #     self.show_page("NilaiPage")

    # def show_search(self):
    #     self.show_page("SearchPage")

    # def show_mapel(self):
    #     self.show_page("MapelPage")
        
    def refresh_all(self):
        for page in self.pages.values():
            try:
                page.update_contents()
            except Exception:
                pass


# Page: Dashboard
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # TITLE
        self.label_title = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_title.pack(pady=(10, 4))

        self.label_sub = ctk.CTkLabel(
            self,
            text="Ringkasan data akademik siswa",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.label_sub.pack(pady=(0, 10))

        # CARD BACKGROUND
        self.card_bg = ctk.CTkFrame(
            self,
            fg_color=("gray92", "gray14"),
            corner_radius=16
        )
        self.card_bg.pack(padx=14, pady=8, fill="x")

        # CARD CONTAINER
        self.card_frame = ctk.CTkFrame(self.card_bg, fg_color="transparent")
        self.card_frame.pack(padx=10, pady=10, fill="x")
        self.card_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Total Siswa
        self.card_total = self._create_card(
            self.card_frame, "Total Siswa", "0"
        )
        self.card_total.grid(row=0, column=0, padx=(0, 8), sticky="we")

        # Card 2: Persentase Lulus (INI YANG DIGANTI)
        self.card_avg = self._create_card(
            self.card_frame, "Persentase Lulus", "0%"
        )
        self.card_avg.grid(row=0, column=1, padx=8, sticky="we")

        # Card 3: Jumlah Lulus
        self.card_lulus = self._create_card(
            self.card_frame, "Jumlah Lulus", "0"
        )
        self.card_lulus.grid(row=0, column=2, padx=(8, 0), sticky="we")

        # DETAIL BOX
        self.info_box = ctk.CTkTextbox(self, state="disabled")
        self.info_box.pack(padx=10, pady=10, fill="both", expand=True)

        self.info_box.tag_config("lulus", foreground=COLOR_LULUS)
        self.info_box.tag_config("tidak_lulus", foreground=COLOR_TIDAK_LULUS)

    # CARD BUILDER
    def _create_card(self, parent, title, value):
        frame = ctk.CTkFrame(
            parent,
            height=90,
            fg_color=("white", "gray10"),
            border_width=1,
            border_color=("gray70", "gray30"),
            corner_radius=12
        )
        frame.pack_propagate(False)

        lbl_title = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=13)
        )
        lbl_title.pack(pady=(10, 0))

        lbl_value = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        lbl_value.pack(pady=(2, 6))

        frame.value_label = lbl_value
        return frame

    # UPDATE CONTENT
    def update_contents(self):
        data = self.app.data
        total = len(data)

        count_nilai = 0
        lulus = 0

        for info in data.values():
            nilai = info.get("nilai", {})
            if nilai:
                count_nilai += 1
                _, status = hitung_rata_status(nilai)
                if status == "LULUS":
                    lulus += 1

        persen_lulus = (lulus / count_nilai * 100) if count_nilai else 0

        # UPDATE CARD
        self.card_total.value_label.configure(text=str(total))
        self.card_avg.value_label.configure(text=f"{persen_lulus:.0f}%")
        self.card_lulus.value_label.configure(text=str(lulus))

        # UPDATE DETAIL BOX
        self.info_box.configure(state="normal")
        self.info_box.delete("1.0", "end")

        if not data:
            self.info_box.insert("end", "Belum ada data siswa.\n")
        else:
            for idx, (nisn, info) in enumerate(sorted(data.items()), start=1):
                nama = info.get("nama", "-")
                kelas = info.get("kelas", "-")
                nilai = info.get("nilai")

                self.info_box.insert(
                    "end", f"{idx}. {nisn} — {nama} — {kelas}\n"
                )

                if not nilai:
                    self.info_box.insert(
                        "end", "     Nilai belum diinput\n\n"
                    )
                else:
                    rata, status = hitung_rata_status(nilai)
                    self.info_box.insert(
                        "end", f"     Rata-rata : {rata:.2f} | Status: "
                    )

                    if status == "LULUS":
                        self.info_box.insert(
                            "end", "LULUS\n\n", "lulus"
                        )
                    else:
                        self.info_box.insert(
                            "end", "TIDAK LULUS\n\n", "tidak_lulus"
                        )

        self.info_box.configure(state="disabled")

# Page: Input Siswa
class SiswaPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Input Data Siswa", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))
        
        card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color=("gray92", "gray14")
        )
        card.pack(padx=40, pady=20)
        
        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(padx=30, pady=20)
        form_frame.grid_columnconfigure(1, minsize=280)


        lbl_nisn = ctk.CTkLabel(form_frame, text="NISN", anchor="w")
        lbl_nisn.grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.entry_nisn = ctk.CTkEntry(form_frame, placeholder_text="1234567890")
        self.entry_nisn.grid(row=0, column=1, padx=6, pady=6)

        lbl_name = ctk.CTkLabel(form_frame, text="Nama lengkap", anchor="w")
        lbl_name.grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Nama lengkap")
        self.entry_name.grid(row=1, column=1, padx=6, pady=6)

        lbl_kelas = ctk.CTkLabel(form_frame, text="Kelas", anchor="w")
        lbl_kelas.grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.entry_kelas = ctk.CTkEntry(form_frame, placeholder_text="Kelas")
        self.entry_kelas.grid(row=2, column=1, padx=6, pady=6)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        btn_add = ctk.CTkButton(
            btn_frame,
            text="Tambah",
            width=120,
            command=self.add_siswa
        )
        btn_add.pack(side="left", padx=8)

        btn_clear = ctk.CTkButton(
            btn_frame,
            text="Clear",
            width=120,
            fg_color="gray",
            command=self.clear_form
        )
        btn_clear.pack(side="left", padx=8)

    def update_contents(self):
        pass

    def clear_form(self):
        self.entry_nisn.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_kelas.delete(0, "end")

    def add_siswa(self):
        nisn = self.entry_nisn.get().strip()
        nama = self.entry_name.get().strip()
        kelas = self.entry_kelas.get().strip()
        
        # =VALIDASI INPUT=
        # NISN wajib, angka, dan 10 digit
        if not nisn:
            messagebox.showerror("Error", "NISN wajib diisi.")
            return
        if not nisn.isdigit():
            messagebox.showerror("Error", "NISN harus berupa angka.")
            return
        if len(nisn) != 10:
            messagebox.showerror("Error", "NISN harus terdiri dari 10 digit.")
            return

        # Nama wajib dan tidak boleh angka
        if not nama:
            messagebox.showerror("Error", "Nama siswa wajib diisi.")
            return
        if any(char.isdigit() for char in nama):
            messagebox.showerror("Error", "Nama tidak boleh mengandung angka.")
            return
        nama = nama.title()

        # Kelas wajib diisi
        if not kelas:
            messagebox.showerror("Error", "Kelas wajib diisi.")
            return
        kelas = kelas.upper()

        # CEK DUPLIKAT NISN
        if nisn in self.app.data:
            messagebox.showerror("Error", f"NISN '{nisn}' sudah terdaftar (Nama: {self.app.data[nisn].get('nama')}).")
            return

        # =====================
        # SIMPAN DATA
        # =====================
        self.app.data[nisn] = {"nama": nama,"kelas": kelas}
        save_data(self.app.data)

        # Update halaman lain
        self.app.refresh_all()

        messagebox.showinfo(
            "Sukses",
            f"Data siswa '{nama}' (NISN: {nisn}) berhasil disimpan."
        )
        self.clear_form()

# Page: Input Nilai
class NilaiPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Input Nilai Siswa",
                            font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        # Bagian Search
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Cari NISN / Nama...")
        self.search_entry.pack(padx=10, pady=(8, 4), fill="x")

        self.btn_search = ctk.CTkButton(self, text="Cari", command=self.search_siswa)
        self.btn_search.pack(padx=10, pady=4)

        self.search_result = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.search_result.pack(pady=4)

        # Frame Form Nilai (disembunyikan dulu)
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack_forget()

        self.subject_vars = {}

        # Buat form nilai di dalam self.form_frame
        for sub in SUBJECTS:
            row = ctk.CTkFrame(self.form_frame)
            row.pack(fill="x", padx=10, pady=4)

            lbl = ctk.CTkLabel(row, text=sub, width=140, anchor="w")
            lbl.pack(side="left")

            ent = ctk.CTkEntry(row, placeholder_text="0 - 100")
            ent.pack(side="left", fill="x", expand=True)

            self.subject_vars[sub] = ent

        # tombol submit + clear
        btn_row = ctk.CTkFrame(self.form_frame)
        btn_row.pack(pady=8)

        self.btn_submit = ctk.CTkButton(btn_row, text="Simpan Nilai", command=self.add_nilai)
        self.btn_submit.pack(side="left", padx=5)

        self.btn_clear = ctk.CTkButton(btn_row, text="Clear", command=self.clear_form)
        self.btn_clear.pack(side="left", padx=5)

        self.selected_nisn = None
        self.selected_name = None

    # Fungsi Search
    def search_siswa(self):
        key = self.search_entry.get().strip()

        if not key:
            messagebox.showwarning("Kosong", "Masukkan NISN atau Nama.")
            return

        found = None

        # Cari berdasarkan NISN atau nama
        for nisn, info in self.app.data.items():
            if key == nisn or key.lower() in info["nama"].lower():
                found = (nisn, info)
                break

        if not found:
            self.search_result.configure(text="Siswa tidak ditemukan.")
            self.form_frame.pack_forget()
            return

        # Data ditemukan
        self.selected_nisn = found[0]
        self.selected_name = found[1]["nama"]

        self.search_result.configure(
            text=f"✔ Ditemukan: {self.selected_name} (NISN {self.selected_nisn})"
        )

        # tampilkan form nilai
        self.form_frame.pack(padx=10, pady=10, fill="x")

    # Clear Form
    def clear_form(self):
        for ent in self.subject_vars.values():
            ent.delete(0, "end")

    # Simpan Nilai
    def add_nilai(self):
        if not self.selected_nisn:
            messagebox.showwarning("Pilih siswa", "Cari dan pilih siswa dahulu.")
            return

        nilai_dict = {}

        # validasi tiap mapel
        try:
            for sub, ent in self.subject_vars.items():
                v = ent.get().strip()
                if v == "":
                    raise ValueError(f"Nilai {sub} kosong.")
                n = int(v)
                if not (0 <= n <= 100):
                    raise ValueError(f"Nilai {sub} harus 0-100.")
                nilai_dict[sub] = n
        except ValueError as e:
            messagebox.showerror("Kesalahan nilai", str(e))
            return

        # Simpan nilai ke data siswa
        self.app.data[self.selected_nisn]["nilai"] = nilai_dict
        save_data(self.app.data)

        # Update halaman lain jika ada
        self.app.refresh_all()

        messagebox.showinfo(
            "Sukses",
            f"Nilai untuk {self.selected_name} (NISN {self.selected_nisn}) berhasil disimpan!"
        )

        self.clear_form()
        
# Page: Search Siswa
class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # TITLE
        title = ctk.CTkLabel(self, text="Search Siswa (NISN atau nama)", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        # SEARCH BAR
        top = ctk.CTkFrame(self)
        top.pack(padx=10, pady=6, fill="x")

        self.search_var = ctk.StringVar()
        self.entry_search = ctk.CTkEntry(
            top, placeholder_text="Ketik NISN atau bagian nama siswa ...",
            textvariable=self.search_var
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_search = ctk.CTkButton(top, text="Cari", width=80, command=self.perform_search)
        btn_search.pack(side="left")

        # BODY (2 kolom)
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        # LEFT COLUMN — List Siswa
        self.listbox = ctk.CTkScrollableFrame(body, width=320)
        self.listbox.pack(side="left", fill="both", expand=True)

        # RIGHT COLUMN — Detail Siswa
        detail_frame = ctk.CTkFrame(body)
        detail_frame.pack(side="right", fill="y", padx=(8, 0))
        detail_frame.grid_rowconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(0, weight=1)

        self.detail_box = ctk.CTkTextbox(detail_frame, width=380, height=380)
        self.detail_box.pack(fill="both", expand=True)

        # TAMBAH sub-frame khusus grid
        btn_frame = ctk.CTkFrame(detail_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        # tombol pakai grid di dalam btn_frame
        self.export_btn = ctk.CTkButton(btn_frame, text="Export PDF",text_color="white", width=90)
        self.export_btn.grid(row=0, column=0, padx=5)

        self.edit_btn = ctk.CTkButton(btn_frame, text="Edit Data", width=90)
        self.edit_btn.grid(row=0, column=1, padx=5)

        self.delete_btn = ctk.CTkButton(btn_frame, text="Hapus Siswa", fg_color="red", width=90)
        self.delete_btn.grid(row=0, column=2, padx=5)

    # dipanggil saat page dibuka
    def update_contents(self):
        self.perform_search()

    # SEARCH FUNCTION
    def perform_search(self):
        key = self.search_var.get().strip().lower()

        for widget in self.listbox.winfo_children():
            widget.destroy()

        found_any = False

        for nisn, info in sorted(self.app.data.items()):
            nama = info.get("nama", "")
            kelas = info.get("kelas", "")
            if key == "" or key in nisn.lower() or key in nama.lower():
                label = f"{nisn} — {nama} — {kelas}"
                btn = ctk.CTkButton(
                    self.listbox, text=label, anchor="w",
                    command=lambda n=nisn: self.show_detail(n)
                )
                btn.pack(fill="x", padx=6, pady=3)
                found_any = True

        if not found_any:
            lbl = ctk.CTkLabel(self.listbox, text="Tidak ada hasil.", fg_color="transparent")
            lbl.pack(padx=6, pady=6)

        self.clear_detail()

    # CLEAR DETAIL
    def clear_detail(self):
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.configure(state="disabled")

        self.export_btn.configure(state="disabled", command=None)
        self.edit_btn.configure(state="disabled", command=None)
        self.delete_btn.configure(state="disabled", command=None)
        
    # MENAMPILKAN DETAIL SISWA
    def show_detail(self, nisn):
        info = self.app.data.get(nisn, {})
        nama = info.get("nama", "-")
        kelas = info.get("kelas", "-")
        nilai = info.get("nilai", {})

        # Hitung rata dan status
        rata, status = hitung_rata_status(nilai)

        # Siapkan textbox
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.configure(font=("Consolas", 13))

        # Fungsi baris sejajar
        def row(label, value, label_w=18):
            return f"{label:<{label_w}} : {value}\n"

        # =====================
        # IDENTITAS SISWA
        # =====================
        self.detail_box.insert("end", row("Nama Peserta Didik", nama))
        self.detail_box.insert("end", row("NISN", nisn))
        self.detail_box.insert("end", row("Kelas", kelas))
        self.detail_box.insert("end", "\n")

        # =====================
        # TABEL NILAI
        # =====================
        col1 = 17   # Mata Pelajaran
        col2 = 7    # Nilai
        col3 = 9    # Predikat

        self.detail_box.insert(
            "end",
            f"{'Mata Pelajaran':<{col1}} {'Nilai':^{col2}} {'Predikat':^{col3}}\n"
        )
        self.detail_box.insert("end", "-" * (col1 + col2 + col3 + 2) + "\n")

        for m, v in nilai.items():
            pred = get_predikat(v)
            self.detail_box.insert(
            "end",
            f"{m:<{col1}} {str(v):^{col2}} {pred:^{col3}}\n"
        )

        # =====================
        # RINGKASAN NILAI
        # =====================
        self.detail_box.tag_config("lulus", foreground=COLOR_LULUS)
        self.detail_box.tag_config("tidak_lulus", foreground=COLOR_TIDAK_LULUS)

        self.detail_box.insert("end", "\n")
        self.detail_box.insert("end", row("Nilai Rata-rata", f"{rata:.2f}"))
        self.detail_box.insert("end", row("Predikat Rata-rata", get_predikat(rata)))
        self.detail_box.insert("end", f"{'Status Kelulusan':<18} : ")

        if status == "LULUS":
            self.detail_box.insert("end", "LULUS\n", "lulus")
        else:
            self.detail_box.insert("end", "TIDAK LULUS\n", "tidak_lulus")

        self.detail_box.configure(state="disabled")

        # Aktifkan tombol export
        self.export_btn.configure(
            state="normal",
            command=lambda: self.export_pdf(nisn, nama, kelas, nilai)
        )

        # aktifkan tombol edit
        self.edit_btn.configure(
            state="normal",
            command=lambda: self.open_edit_popup(nisn)
        )

        # aktifkan tombol delete
        self.delete_btn.configure(
            state="normal",
            command=lambda: self.delete_student(nisn)
        )

    #konfirmasi dan hapus siswa
    def delete_student(self, nisn):
        confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus siswa NISN '{nisn}'?")
        if not confirm:
            return

        # hapus dari data
        if nisn in self.app.data:
            del self.app.data[nisn]
            save_data(self.app.data)

        messagebox.showinfo("Sukses", f"Siswa dengan NISN '{nisn}' berhasil dihapus.")

        # refresh halaman & other pages
        self.app.refresh_all()


    def open_edit_popup(self, nisn):
        info = self.app.data.get(nisn, {})
        if not info:
            messagebox.showerror("Error", "Data siswa tidak ditemukan.")
            return

        current_name = info.get("nama", "")
        current_kelas = info.get("kelas", "")
        current_nilai = info.get("nilai", {})

        # Buat popup
        win = ctk.CTkToplevel(self)
        win.title(f"Edit Data - {current_name}")
        win.geometry("380x520")
        win.transient(self)
        win.grab_set()

        # Judul
        ctk.CTkLabel(win, text=f"Edit Data Siswa", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # NISN (bisa diubah)
        frame_nisn = ctk.CTkFrame(win)
        frame_nisn.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(frame_nisn, text="NISN", width=120, anchor="w").pack(side="left")
        ent_nisn = ctk.CTkEntry(frame_nisn)
        ent_nisn.pack(side="left", fill="x", expand=True)
        ent_nisn.insert(0, nisn)

        # Nama (bisa diubah)
        frame_name = ctk.CTkFrame(win)
        frame_name.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(frame_name, text="Nama", width=120, anchor="w").pack(side="left")
        ent_name = ctk.CTkEntry(frame_name)
        ent_name.pack(side="left", fill="x", expand=True)
        ent_name.insert(0, current_name)

        # Kelas (bisa diubah)
        frame_kelas = ctk.CTkFrame(win)
        frame_kelas.pack(fill="x", padx=12, pady=6)
        ctk.CTkLabel(frame_kelas, text="Kelas", width=120, anchor="w").pack(side="left")
        ent_kelas = ctk.CTkEntry(frame_kelas)
        ent_kelas.pack(side="left", fill="x", expand=True)
        ent_kelas.insert(0, current_kelas)

        # Subject entries
        entries = {}
        for sub in SUBJECTS:
            frame = ctk.CTkFrame(win)
            frame.pack(fill="x", padx=12, pady=4)

            ctk.CTkLabel(frame, text=sub, width=120, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(frame)
            ent.pack(side="left", fill="x", expand=True)
            ent.insert(0, str(current_nilai.get(sub, 0)))
            entries[sub] = ent

        # Tombol simpan
        def save_edit():
            new_nisn = ent_nisn.get().strip()
            new_name = ent_name.get().strip().title()
            new_kelas = ent_kelas.get().strip()

            if not new_nisn:
                messagebox.showerror("Error", "NISN tidak boleh kosong.")
                return
            if not new_name:
                messagebox.showerror("Error", "Nama tidak boleh kosong.")
                return
            if not new_kelas:
                messagebox.showerror("Error", "Kelas tidak boleh kosong.")
                return

            try:
                updated = {}
                for sub, ent in entries.items():
                    vv = ent.get().strip()
                    if vv == "":
                        raise ValueError(f"Nilai {sub} tidak boleh kosong.")
                    v = int(vv)
                    if not (0 <= v <= 100):
                        raise ValueError(f"Nilai {sub} harus antara 0 - 100.")
                    updated[sub] = v

                # Handle rename NISN: kalau ganti nisn, pindahkan key di dict
                saved_nisn = nisn
                if new_nisn != nisn:
                    if new_nisn in self.app.data:
                        ok = messagebox.askyesno("Konfirmasi", f"NISN '{new_nisn}' sudah ada (Nama: {self.app.data[new_nisn].get('nama')}). Timpa data?")
                        if not ok:
                            return
                    # tulis data baru dan hapus yang lama
                    self.app.data[new_nisn] = {"nama": new_name, "kelas": new_kelas, "nilai": updated}
                    if nisn in self.app.data:
                        del self.app.data[nisn]
                    saved_nisn = new_nisn
                else:
                    # update nilai dan nama pada nisn lama
                    self.app.data[nisn] = {"nama": new_name,"kelas": new_kelas,  "nilai": updated}
                    saved_nisn = nisn

                save_data(self.app.data)

                messagebox.showinfo("Sukses", f"Data '{new_name}' (NISN: {saved_nisn}) berhasil diperbarui.")
                win.destroy()

                self.app.refresh_all()
                self.show_detail(saved_nisn)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(win, text="Simpan Perubahan", command=save_edit).pack(pady=12)

    #EXPORT PDF
    def export_pdf(self, nisn, nama, kelas, nilai_dict):
        path = export_pdf_for_student(nisn, nama, kelas, nilai_dict)
        if path:
            messagebox.showinfo("Berhasil", f"PDF berhasil disimpan:\n{path}")
        else:
            messagebox.showinfo("Dibatalkan", "Export PDF dibatalkan.")

# Page: Search Mapel
class MapelPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Search Mapel", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        top = ctk.CTkFrame(self)
        top.pack(padx=10, pady=6, fill="x")

        self.mapel_var = ctk.StringVar(value=SUBJECTS[0])
        self.mapel_menu = ctk.CTkOptionMenu(
            top,
            values=SUBJECTS,
            variable=self.mapel_var,
            command=lambda _: self.show_mapel_list()  # refresh otomatis
        )
        self.mapel_menu.pack(side="left", padx=(0, 8))

        self.result_box = ctk.CTkTextbox(self, state="disabled")
        self.result_box.pack(fill="both", expand=True, padx=10, pady=8)

    def update_contents(self):
        self.show_mapel_list()

    def show_mapel_list(self):
        mapel = self.mapel_var.get()
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        found = False
        for nisn, info in sorted(self.app.data.items()):
            nilai = info.get("nilai", {})
            if mapel in nilai:
                nama = info.get("nama", "-")
                kelas = info.get("kelas", "-")
                nilai_mapel = nilai[mapel]

                self.result_box.insert("end", f"{nisn} — {nama} — {kelas}\n")
                self.result_box.insert("end", f"Nilai {mapel}: {nilai_mapel}\n\n")
                found = True
        if not found:
            self.result_box.insert("end", "Belum ada data untuk mapel ini.")
        self.result_box.configure(state="disabled")

# main program
if __name__ == "__main__":
    app = RaporApp()
    app.mainloop()
