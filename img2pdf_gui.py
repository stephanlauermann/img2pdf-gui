import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from io import BytesIO

from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


QUALITY_PRESETS = {
    "Entwurf":   {"max_long_edge_px": 2000, "jpeg_quality": 70},
    "Standard":  {"max_long_edge_px": 3500, "jpeg_quality": 85},
    "Hoch":      {"max_long_edge_px": 6000, "jpeg_quality": 95},
}

QUALITY_TEXT = {
    "Entwurf":  "Entwurf: kleine Datei, Bildschirm/Vorschau (2000px, JPG 70)",
    "Standard": "Standard: beste Balance, Büro/Archiv (3500px, JPG 85)",
    "Hoch":     "Hoch: maximale Qualität, größere Datei (6000px, JPG 95)",
}

SCALE_MODES = [
    "A4 einpassen (hochskalieren)",
    "A4 einpassen (nicht hochskalieren)",
    "Originalgröße (DPI)",
]


def mm_to_pt(mm: float) -> float:
    return float(mm) * 72.0 / 25.4


def get_image_dpi(im: Image.Image, fallback_dpi: float) -> float:
    dpi = im.info.get("dpi")
    if isinstance(dpi, tuple) and len(dpi) >= 1 and dpi[0]:
        try:
            d = float(dpi[0])
            if 30 <= d <= 1200:
                return d
        except Exception:
            pass
    return float(fallback_dpi)


def prepare_image_bytes(path: str, preset: dict) -> tuple[BytesIO, int, int]:
    with Image.open(path) as im:
        im.load()
        try:
            im = ImageOps.exif_transpose(im)
        except Exception:
            pass

        max_edge = int(preset["max_long_edge_px"])
        w, h = im.size
        long_edge = max(w, h)
        if long_edge > max_edge:
            scale = max_edge / float(long_edge)
            im = im.resize((int(round(w * scale)), int(round(h * scale))), Image.LANCZOS)

        w, h = im.size
        has_alpha = (im.mode in ("RGBA", "LA")) or ("transparency" in im.info)
        bio = BytesIO()

        if has_alpha:
            if im.mode not in ("RGBA", "LA"):
                im = im.convert("RGBA")
            im.save(bio, format="PNG", optimize=True)
        else:
            if im.mode != "RGB":
                im = im.convert("RGB")
            im.save(
                bio,
                format="JPEG",
                quality=int(preset["jpeg_quality"]),
                optimize=True,
                progressive=True
            )

        bio.seek(0)
        return bio, w, h


def images_to_pdf(
    paths: list[str],
    output_pdf: str,
    preset_name: str,
    margin_mm: float = 0.0,
    scale_mode: str = SCALE_MODES[0],
    assumed_dpi: float = 300.0
):
    preset = QUALITY_PRESETS.get(preset_name, QUALITY_PRESETS["Standard"])

    page_w, page_h = A4
    margin = mm_to_pt(margin_mm)
    box_w = page_w - 2 * margin
    box_h = page_h - 2 * margin

    c = canvas.Canvas(output_pdf, pagesize=A4)

    for p in paths:
        dpi_for_original = assumed_dpi
        if scale_mode == "Originalgröße (DPI)":
            with Image.open(p) as im0:
                im0.load()
                try:
                    im0 = ImageOps.exif_transpose(im0)
                except Exception:
                    pass
                dpi_for_original = get_image_dpi(im0, assumed_dpi)

        img_bytes, px_w, px_h = prepare_image_bytes(p, preset)
        img = ImageReader(img_bytes)

        if scale_mode == "Originalgröße (DPI)":
            draw_w = (px_w / float(dpi_for_original)) * 72.0
            draw_h = (px_h / float(dpi_for_original)) * 72.0
            scale = min(box_w / draw_w, box_h / draw_h, 1.0)
            draw_w *= scale
            draw_h *= scale
        else:
            aspect = px_w / float(px_h)
            box_aspect = box_w / float(box_h)

            if aspect >= box_aspect:
                target_w = box_w
                target_h = box_w / aspect
            else:
                target_h = box_h
                target_w = box_h * aspect

            if scale_mode == "A4 einpassen (nicht hochskalieren)":
                draw_w_native = (px_w / float(assumed_dpi)) * 72.0
                draw_h_native = (px_h / float(assumed_dpi)) * 72.0

                draw_w = min(target_w, draw_w_native)
                draw_h = min(target_h, draw_h_native)

                native_aspect = draw_w_native / float(draw_h_native)
                if draw_w / float(draw_h) > native_aspect:
                    draw_w = draw_h * native_aspect
                else:
                    draw_h = draw_w / native_aspect
            else:
                draw_w, draw_h = target_w, target_h

        x = margin + (box_w - draw_w) / 2.0
        y = margin + (box_h - draw_h) / 2.0

        c.drawImage(img, x, y, width=draw_w, height=draw_h, mask="auto")
        c.showPage()

    c.save()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bilder → PDF (A4, ohne Abschneiden)")
        self.geometry("900x540")
        self.minsize(780, 440)
        self.paths: list[str] = []
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(main)
        right.pack(side="right", fill="y", padx=(12, 0))

        ttk.Label(left, text="Geladene Bilder (Reihenfolge = PDF-Seiten):").pack(anchor="w")
        self.listbox = tk.Listbox(left, selectmode=tk.EXTENDED)
        self.listbox.pack(fill="both", expand=True, pady=(6, 0))

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_row, text="Hinzufügen…", command=self.add_files).pack(side="left")
        ttk.Button(btn_row, text="Entfernen", command=self.remove_selected).pack(side="left", padx=(8, 0))
        ttk.Button(btn_row, text="Nach oben", command=lambda: self.move_selected(-1)).pack(side="left", padx=(8, 0))
        ttk.Button(btn_row, text="Nach unten", command=lambda: self.move_selected(1)).pack(side="left", padx=(8, 0))

        ttk.Separator(right).pack(fill="x", pady=(0, 10))

        ttk.Label(right, text="Qualität:").pack(anchor="w")
        self.quality_var = tk.StringVar(value="Standard")
        self.quality_cb = ttk.Combobox(
            right, textvariable=self.quality_var,
            values=list(QUALITY_PRESETS.keys()),
            state="readonly", width=28
        )
        self.quality_cb.pack(anchor="w", pady=(4, 4))

        # Kurzbeschreibung direkt darunter
        self.quality_desc = ttk.Label(right, text=QUALITY_TEXT["Standard"], wraplength=260, justify="left")
        self.quality_desc.pack(anchor="w", pady=(0, 12))

        self.quality_cb.bind("<<ComboboxSelected>>", self._on_quality_changed)

        ttk.Label(right, text="Rand (mm) – 0 = volle A4-Fläche:").pack(anchor="w")
        self.margin_var = tk.StringVar(value="0")
        ttk.Entry(right, textvariable=self.margin_var, width=10).pack(anchor="w", pady=(4, 12))

        ttk.Label(right, text="Skalierung:").pack(anchor="w")
        self.scale_mode_var = tk.StringVar(value=SCALE_MODES[0])
        ttk.Combobox(
            right, textvariable=self.scale_mode_var,
            values=SCALE_MODES, state="readonly", width=28
        ).pack(anchor="w", pady=(4, 12))

        ttk.Label(right, text="Angenommene DPI (für Originalgröße / nicht hochskalieren):").pack(anchor="w")
        self.dpi_var = tk.StringVar(value="300")
        ttk.Entry(right, textvariable=self.dpi_var, width=10).pack(anchor="w", pady=(4, 12))

        ttk.Separator(right).pack(fill="x", pady=10)
        ttk.Button(right, text="PDF erzeugen…", command=self.export_pdf).pack(fill="x")
        ttk.Button(right, text="Beenden", command=self.destroy).pack(fill="x", pady=(8, 0))

    def _on_quality_changed(self, _event=None):
        q = self.quality_var.get()
        self.quality_desc.config(text=QUALITY_TEXT.get(q, ""))

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Bilder auswählen",
            filetypes=[
                ("Bilder", "*.jpg *.jpeg *.png"),
                ("JPG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Alle Dateien", "*.*")
            ],
        )
        if not files:
            return
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                self.paths.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.listbox.delete(idx)
            del self.paths[idx]

    def move_selected(self, direction: int):
        sel = list(self.listbox.curselection())
        if not sel:
            return
        sel_sorted = sel if direction < 0 else list(reversed(sel))
        for idx in sel_sorted:
            new_idx = idx + direction
            if not (0 <= new_idx < len(self.paths)):
                continue
            self.paths[idx], self.paths[new_idx] = self.paths[new_idx], self.paths[idx]

            text_idx = self.listbox.get(idx)
            text_new = self.listbox.get(new_idx)
            self.listbox.delete(new_idx)
            self.listbox.insert(new_idx, text_idx)
            self.listbox.delete(idx)
            self.listbox.insert(idx, text_new)

        self.listbox.selection_clear(0, tk.END)
        for idx in sel:
            new_idx = idx + direction
            if 0 <= new_idx < len(self.paths):
                self.listbox.selection_set(new_idx)

    def export_pdf(self):
        if not self.paths:
            messagebox.showwarning("Keine Bilder", "Bitte zuerst JPG/PNG hinzufügen.")
            return

        out = filedialog.asksaveasfilename(
            title="PDF speichern",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not out:
            return

        try:
            margin_mm = float(self.margin_var.get().strip().replace(",", "."))
            dpi = float(self.dpi_var.get().strip().replace(",", "."))
            if margin_mm < 0:
                margin_mm = 0.0
            if dpi <= 0:
                dpi = 300.0

            images_to_pdf(
                self.paths,
                out,
                preset_name=self.quality_var.get(),
                margin_mm=margin_mm,
                scale_mode=self.scale_mode_var.get(),
                assumed_dpi=dpi
            )
        except Exception as e:
            messagebox.showerror("Fehler", f"PDF konnte nicht erzeugt werden:\n{e}")
            return

        messagebox.showinfo("Fertig", f"PDF wurde erstellt:\n{out}")


if __name__ == "__main__":
    App().mainloop()
