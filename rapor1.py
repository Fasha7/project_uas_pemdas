import os
import json
import customtkinter as ctk
from tkinter import messagebox
from fpdf import FPDF

# -------------------------
# Konfigurasi dasar
# -------------------------
DATA_FILE = "data_siswa.json"
SUBJECTS = ["Matematika", "Bahasa Indonesia", "Bahasa Inggris", "Produktif"]


# -------------------------
# Utility: load / save data
# -------------------------
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
    total = sum(nilai_dict.values())
    rata = total / len(nilai_dict) if nilai_dict else 0
    status = "LULUS" if rata >= 75 else "TIDAK LULUS"
    return rata, status


def export_pdf_for_student(nama, nilai_dict, folder="."):
    """Buat file PDF rapor untuk satu siswa, return path or raise."""
    rata, status = hitung_rata_status(nilai_dict)
    filename = f"Rapor_{nama.replace(' ', '_')}.pdf"
    path = os.path.join(folder, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "RAPOR SISWA", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Nama: {nama}", ln=True)
    pdf.ln(3)

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(120, 8, "Mata Pelajaran", border=1)
    pdf.cell(40, 8, "Nilai", border=1, ln=True)

    # Table rows
    pdf.set_font("Arial", size=12)
    for mapel, n in nilai_dict.items():
        pdf.cell(120, 8, str(mapel), border=1)
        pdf.cell(40, 8, str(n), border=1, ln=True)

    pdf.ln(6)
    pdf.cell(0, 8, f"Rata-rata: {rata:.2f}", ln=True)
    pdf.cell(0, 8, f"Status: {status}", ln=True)

    pdf.output(path)
    return path

# -------------------------
# GUI App
# -------------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RaporApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplikasi Rapor - UAS")
        self.geometry("900x600")
        self.minsize(820, 520)

        # Data
        self.data = load_data()

        # Layout: sidebar + content frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(6, weight=1)

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nswe", padx=(0,10), pady=10)

        # Sidebar buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_input = ctk.CTkButton(self.sidebar, text="Input Siswa", command=self.show_input)
        self.btn_search = ctk.CTkButton(self.sidebar, text="Search Siswa", command=self.show_search)
        self.btn_mapel = ctk.CTkButton(self.sidebar, text="Search Mapel", command=self.show_mapel)
        self.btn_export = ctk.CTkButton(self.sidebar, text="Export PDF", command=self.show_export)
        self.btn_refresh = ctk.CTkButton(self.sidebar, text="Refresh Data", command=self.reload_data)

        self.btn_dashboard.grid(row=0, column=0, padx=10, pady=8, sticky="we")
        self.btn_input.grid(row=1, column=0, padx=10, pady=8, sticky="we")
        self.btn_search.grid(row=2, column=0, padx=10, pady=8, sticky="we")
        self.btn_mapel.grid(row=3, column=0, padx=10, pady=8, sticky="we")
        self.btn_export.grid(row=4, column=0, padx=10, pady=8, sticky="we")
        self.btn_refresh.grid(row=5, column=0, padx=10, pady=8, sticky="we")

        # Create pages
        self.pages = {}
        for Page in (DashboardPage, InputPage, SearchPage, MapelPage, ExportPage):
            page = Page(self.content, self)
            self.pages[Page.__name__] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_dashboard()

    def show_page(self, page_name):
        page = self.pages.get(page_name)
        if page:
            page.update_contents()
            page.tkraise()

    def show_dashboard(self):
        self.show_page("DashboardPage")

    def show_input(self):
        self.show_page("InputPage")

    def show_search(self):
        self.show_page("SearchPage")

    def show_mapel(self):
        self.show_page("MapelPage")

    def show_export(self):
        self.show_page("ExportPage")

    def reload_data(self):
        self.data = load_data()
        messagebox.showinfo("Refresh", "Data berhasil direfresh.")

# -------------------------
# Page: Dashboard
# -------------------------
class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.label_title = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.pack(pady=(10, 5))

        self.info_box = ctk.CTkTextbox(self, width=640, height=420, state="disabled")
        self.info_box.pack(padx=10, pady=10)

    def update_contents(self):
        self.info_box.configure(state="normal")
        self.info_box.delete("1.0", "end")

        data = self.app.data
        self.info_box.insert("end", f"Total siswa: {len(data)}\n\n")
        if not data:
            self.info_box.insert("end", "Belum ada data siswa. Silakan tambah di menu Input Siswa.\n")
        else:
            for idx, (nama, nilai) in enumerate(sorted(data.items()), start=1):
                rata, status = hitung_rata_status(nilai)
                self.info_box.insert("end", f"{idx}. {nama} — Rata-rata: {rata:.2f} — {status}\n")
        self.info_box.configure(state="disabled")

# -------------------------
# Page: Input Siswa
# -------------------------
class InputPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Input Data Siswa", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        form_frame = ctk.CTkFrame(self)
        form_frame.pack(padx=10, pady=6, fill="x")

        # Nama
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Nama lengkap")
        self.entry_name.grid(row=0, column=0, columnspan=2, padx=6, pady=6, sticky="we")

        # Subject entries
        self.subject_vars = {}
        for i, sub in enumerate(SUBJECTS, start=1):
            lbl = ctk.CTkLabel(form_frame, text=sub)
            ent = ctk.CTkEntry(form_frame, placeholder_text="0-100")
            lbl.grid(row=i, column=0, padx=6, pady=4, sticky="w")
            ent.grid(row=i, column=1, padx=6, pady=4, sticky="we")
            self.subject_vars[sub] = ent

        form_frame.grid_columnconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(padx=10, pady=8, fill="x")
        btn_add = ctk.CTkButton(btn_frame, text="Tambah / Simpan Siswa", command=self.add_siswa)
        btn_add.pack(side="left", padx=6)
        btn_clear = ctk.CTkButton(btn_frame, text="Clear", command=self.clear_form)
        btn_clear.pack(side="left", padx=6)

    def update_contents(self):
        # nothing dynamic needed here
        pass

    def clear_form(self):
        self.entry_name.delete(0, "end")
        for ent in self.subject_vars.values():
            ent.delete(0, "end")

    def add_siswa(self):
        nama = self.entry_name.get().strip().title()
        if not nama:
            messagebox.showwarning("Input kosong", "Nama siswa wajib diisi.")
            return

        nilai_dict = {}
        try:
            for sub, ent in self.subject_vars.items():
                v = ent.get().strip()
                if v == "":
                    raise ValueError(f"Nilai {sub} kosong.")
                n = int(v)
                if not (0 <= n <= 100):
                    raise ValueError(f"Nilai {sub} harus antara 0-100.")
                nilai_dict[sub] = n
        except ValueError as e:
            messagebox.showerror("Kesalahan nilai", str(e))
            return

        # simpan ke data
        self.app.data[nama] = nilai_dict
        save_data(self.app.data)
        messagebox.showinfo("Sukses", f"Data siswa '{nama}' berhasil disimpan.")
        self.clear_form()

# -------------------------
# Page: Search Siswa
# -------------------------
class SearchPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # ============ TITLE ============
        title = ctk.CTkLabel(self, text="Search Siswa", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        # ============ SEARCH BAR ============
        top = ctk.CTkFrame(self)
        top.pack(padx=10, pady=6, fill="x")

        self.search_var = ctk.StringVar()
        self.entry_search = ctk.CTkEntry(
            top, placeholder_text="Ketik bagian nama siswa ...",
            textvariable=self.search_var
        )
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 6))

        btn_search = ctk.CTkButton(top, text="Cari", width=80, command=self.perform_search)
        btn_search.pack(side="left")

        # ============ BODY (2 kolom) ============
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=8)

        # LEFT COLUMN — List Siswa
        self.listbox = ctk.CTkScrollableFrame(body, width=250)
        self.listbox.pack(side="left", fill="both", expand=True)

        # RIGHT COLUMN — Detail Siswa
        detail_frame = ctk.CTkFrame(body)
        detail_frame.pack(side="right", fill="y", padx=(8, 0))

        self.detail_box = ctk.CTkTextbox(detail_frame, width=300, height=350)
        self.detail_box.pack(fill="both", expand=True)

        # Export button (disabled by default)
        self.export_btn = ctk.CTkButton(detail_frame, text="Export PDF", state="disabled")
        self.export_btn.pack(pady=(8, 5))

        # Tombol Edit & Delete
        self.edit_btn = ctk.CTkButton(detail_frame, text="Edit Data", state="disabled")
        self.edit_btn.pack(pady=(5, 5))

        self.delete_btn = ctk.CTkButton(detail_frame, text="Hapus Siswa", fg_color="red", state="disabled")
        self.delete_btn.pack(pady=(5, 5))

    # dipanggil saat page dibuka
    def update_contents(self):
        self.perform_search()

    # ============ SEARCH FUNCTION ============
    def perform_search(self):
        key = self.search_var.get().strip().lower()

        # Clear listbox
        for widget in self.listbox.winfo_children():
            widget.destroy()

        found_any = False

        # Loop siswa
        for nama in sorted(self.app.data.keys()):
            if key == "" or key in nama.lower():
                btn = ctk.CTkButton(
                    self.listbox, text=nama, anchor="w",
                    command=lambda n=nama: self.show_detail(n)
                )
                btn.pack(fill="x", padx=6, pady=3)
                found_any = True

        if not found_any:
            lbl = ctk.CTkLabel(self.listbox, text="Tidak ada hasil.", fg_color="transparent")
            lbl.pack(padx=6, pady=6)

        # Reset detail panel tiap search
        self.clear_detail()

    # ============ CLEAR DETAIL ============
    def clear_detail(self):
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.configure(state="disabled")

        self.export_btn.configure(state="disabled", command=None)
        self.edit_btn.configure(state="disabled", command=None)
        self.delete_btn.configure(state="disabled", command=None)

    # ============ MENAMPILKAN DETAIL SISWA ============
    def show_detail(self, nama):
        nilai = self.app.data.get(nama, {})

        # Hitung rata dan status
        rata, status = hitung_rata_status(nilai)

        # Tampilkan detail
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")

        self.detail_box.insert("end", f"Nama: {nama}\n\n")
        for m, v in nilai.items():
            self.detail_box.insert("end", f"{m}: {v}\n")

        self.detail_box.insert("end", f"\nRata-rata: {rata:.2f}")
        self.detail_box.insert("end", f"\nStatus: {status}\n")

        self.detail_box.configure(state="disabled")

        # Aktifkan tombol export
        self.export_btn.configure(
            state="normal",
            command=lambda: self.export_pdf(nama, nilai)
        )

        # aktifkan tombol edit
        self.edit_btn.configure(
            state="normal",
            command=lambda: self.open_edit_popup(nama)
        )

        # aktifkan tombol delete
        self.delete_btn.configure(
            state="normal",
            command=lambda: self.delete_student(nama)
        )

    def delete_student(self, nama):
        confirm = messagebox.askyesno("Konfirmasi", f"Yakin ingin menghapus siswa '{nama}'?")
        if not confirm:
            return

        # hapus dari data
        del self.app.data[nama]
        save_data(self.app.data)

        messagebox.showinfo("Sukses", f"Siswa '{nama}' berhasil dihapus.")

        # refresh halaman
        self.perform_search()

    def open_edit_popup(self, nama):
        nilai = self.app.data[nama]

        # Buat popup
        win = ctk.CTkToplevel(self)
        win.title(f"Edit Data - {nama}")
        win.geometry("350x400")

        # Judul
        ctk.CTkLabel(win, text=f"Edit Nilai {nama}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        # Entry mapel
        entries = {}
        for sub in SUBJECTS:
            frame = ctk.CTkFrame(win)
            frame.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(frame, text=sub, width=120, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(frame)
            ent.pack(side="left", fill="x", expand=True)
            ent.insert(0, nilai.get(sub, 0))
            entries[sub] = ent

        # Tombol simpan
        def save_edit():
            try:
                updated = {}
                for sub, ent in entries.items():
                    v = int(ent.get())
                    if not (0 <= v <= 100):
                        raise ValueError(f"Nilai {sub} harus antara 0 - 100.")
                    updated[sub] = v

                self.app.data[nama] = updated
                save_data(self.app.data)

                messagebox.showinfo("Sukses", f"Data '{nama}' berhasil diperbarui.")
                win.destroy()
                self.show_detail(nama)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(win, text="Simpan Perubahan", command=save_edit).pack(pady=15)

    # ============ EXPORT PDF ============
    def export_pdf(self, nama, nilai):
        try:
            path = export_pdf_for_student(nama, nilai)
            messagebox.showinfo("Export Sukses", f"PDF berhasil dibuat:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Gagal", str(e))

# -------------------------
# Page: Search Mapel
# -------------------------
class MapelPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Search Mapel", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        top = ctk.CTkFrame(self)
        top.pack(padx=10, pady=6, fill="x")

        self.mapel_var = ctk.StringVar(value=SUBJECTS[0])
        self.mapel_menu = ctk.CTkOptionMenu(top, values=SUBJECTS, variable=self.mapel_var)
        self.mapel_menu.pack(side="left", padx=(0,8))

        btn = ctk.CTkButton(top, text="Tampilkan", command=self.show_mapel_list)
        btn.pack(side="left")

        self.result_box = ctk.CTkTextbox(self, state="disabled")
        self.result_box.pack(fill="both", expand=True, padx=10, pady=8)

    def update_contents(self):
        self.show_mapel_list()

    def show_mapel_list(self):
        mapel = self.mapel_var.get()
        self.result_box.configure(state="normal")
        self.result_box.delete("1.0", "end")
        found = False
        for nama, nilai in sorted(self.app.data.items()):
            if mapel in nilai:
                self.result_box.insert("end", f"{nama}: {nilai[mapel]}\n")
                found = True
        if not found:
            self.result_box.insert("end", "Belum ada data untuk mapel ini.")
        self.result_box.configure(state="disabled")

# -------------------------
# Page: Export PDF
# -------------------------
class ExportPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self, text="Export PDF Rapor", font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=(10, 8))

        frame = ctk.CTkFrame(self)
        frame.pack(padx=10, pady=8, fill="x")

        self.student_var = ctk.StringVar(value="")
        self.option = ctk.CTkOptionMenu(frame, values=list(sorted(self.app.data.keys())), variable=self.student_var)
        self.option.pack(side="left", padx=(0,8), fill="x", expand=True)

        btn = ctk.CTkButton(frame, text="Export Selected", command=self.do_export_selected)
        btn.pack(side="left", padx=(8,0))

        self.path_label = ctk.CTkLabel(self, text="")
        self.path_label.pack(padx=10, pady=6)

    def update_contents(self):
        # refresh option menu values
        vals = list(sorted(self.app.data.keys()))
        if not vals:
            vals = ["-- kosong --"]
        self.option.configure(values=vals)
        # if current value not in vals, set first
        if self.student_var.get() not in vals:
            self.student_var.set(vals[0])

    def do_export_selected(self):
        nama = self.student_var.get()
        if not nama or nama.startswith("--"):
            messagebox.showwarning("Peringatan", "Pilih siswa untuk diexport.")
            return
        nilai = self.app.data.get(nama)
        if not nilai:
            messagebox.showerror("Error", "Data siswa tidak ditemukan.")
            return
        try:
            path = export_pdf_for_student(nama, nilai)
            self.path_label.configure(text=f"PDF dibuat: {path}")
            messagebox.showinfo("Sukses", f"PDF berhasil dibuat:\n{path}")
        except Exception as e:
            messagebox.showerror("Gagal export", str(e))

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app = RaporApp()
    app.mainloop()