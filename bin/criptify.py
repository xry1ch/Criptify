from __future__ import annotations
import random
from pathlib import Path
from typing import Iterable, List
import tkinter as tk
from tkinter import filedialog, messagebox
from cryptography.fernet import Fernet

try:
    import ttkbootstrap as tb
except ModuleNotFoundError:
    tb = None

DARK_BG = "#000000"
SURFACE = "#202020"
FG = "#eaeaea"
BTN = "#3d3d3d"
BTN_HOVER = "#505050"
GREEN = "#00ff00"

LOGO = (
    " \n"
    " ▄████████    ▄████████  ▄█     ▄███████▄     ███      ▄█     ▄████████ ▄██   ▄   \n"
    "███    ███   ███    ███ ███    ███    ███ ▀█████████▄ ███    ███    ███ ███   ██▄ \n"
    "███    █▀    ███    ███ ███▌   ███    ███    ▀███▀▀██ ███▌   ███    █▀  ███▄▄▄███ \n"
    "███         ▄███▄▄▄▄██▀ ███▌   ███    ███     ███   ▀ ███▌  ▄███▄▄▄     ▀▀▀▀▀▀███ \n"
    "███        ▀▀███▀▀▀▀▀   ███▌ ▀█████████▀      ███     ███▌ ▀▀███▀▀▀     ▄██   ███ \n"
    "███    █▄  ▀███████████ ███    ███            ███     ███    ███        ███   ███ \n"
    "███    ███   ███    ███ ███    ███            ███     ███    ███        ███   ███ \n"
    "████████▀    ███    ███ █▀    ▄████▀         ▄████▀   █▀     ███         ▀█████▀  \n"
    "             ███    ███                                                    \n"
)

# ─── UTILITIES ──────────────────────────────────────────────────────────────────


def make_button(parent: tk.Widget, text: str, cmd):
    """consistent dark-themed button"""
    btn = tk.Button(
        parent, text=text, command=cmd,
        bg=BTN, fg="white", activebackground=BTN_HOVER, activeforeground="white",
        relief="flat", padx=18, pady=8, bd=0, highlightthickness=0,
        font=("Helvetica", 12, "bold"),
    )
    # simple hover effect
    btn.bind("<Enter>", lambda _e: btn.configure(bg=BTN_HOVER))
    btn.bind("<Leave>", lambda _e: btn.configure(bg=BTN))
    return btn

# ─── MATRIX RAIN ────────────────────────────────────────────────────────────────


class MatrixRain:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.font = ("Courier", 16, "bold")
        self.reset_geometry()
        # Katakana unicode block gives a nice cyberpunk vibe
        self.chars = [chr(i) for i in range(0x30A0, 0x30FF)]
        self.loop()

    def reset_geometry(self):
        self.width = self.canvas.winfo_width() or 840
        self.height = self.canvas.winfo_height() or 580
        self.cell = 16
        self.columns = self.width // self.cell + 1
        # random starting positions so columns begin at different heights
        self.drops = [random.randint(0, self.height // self.cell)
                      for _ in range(self.columns)]

    def loop(self):
        self.canvas.delete("rain")
        for i in range(self.columns):
            x = i * self.cell
            y = self.drops[i] * self.cell
            self.canvas.create_text(
                x, y,
                text=random.choice(self.chars),
                fill=GREEN, font=self.font,
                tags="rain"
            )
            if y > self.height and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1
        self.canvas.after(50, self.loop)

# ─── FERNET HELPERS ────────────────────────────────────────────────────────────


def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_file(key: bytes, p: Path) -> Path:
    out = p.with_suffix(p.suffix + ".enc")
    out.write_bytes(Fernet(key).encrypt(p.read_bytes()))
    p.unlink(missing_ok=True)
    return out


def decrypt_file(key: bytes, p: Path) -> Path | None:
    try:
        data = Fernet(key).decrypt(p.read_bytes())
    except Exception:
        return None
    out = p.with_suffix("")
    out.write_bytes(data)
    p.unlink(missing_ok=True)
    return out

# ─── KEY DIALOG ────────────────────────────────────────────────────────────────


class KeyDialog(tk.Toplevel):
    def __init__(self, parent: "App", mode: str, files: Iterable[Path]):
        super().__init__(parent)
        self.parent, self.mode, self.files = parent, mode, list(files)
        self.configure(bg=SURFACE)
        self.title("Fernet Key")
        self.resizable(False, False)
        self.transient(parent)

        tk.Label(
            self, text="Fernet key:", bg=SURFACE, fg=FG
        ).pack(anchor="w", padx=14, pady=(14, 4))

        self.key_var = tk.StringVar(self)
        entry = tk.Entry(
            self,
            textvariable=self.key_var,
            width=60,
            bg="#141414",
            fg=FG,
            insertbackground=FG,
            relief="flat",
        )
        entry.pack(fill="x", padx=14)
        entry.focus()

        row = tk.Frame(self, bg=SURFACE)
        row.pack(fill="x", padx=14, pady=16)

        # ▸ Show “Generate” **only** when encrypting
        if mode == "encrypt":
            make_button(row, "Generate", self._gen).pack(
                side="left", padx=(0, 8))

        action_label = "Encrypt" if mode == "encrypt" else "Decrypt"
        make_button(row, action_label, self._run).pack(side="right")

        self._center()

    # ---------------- internal helpers --------------------

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - w)//2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _gen(self):
        self.key_var.set(generate_key().decode())

    def _run(self):
        try:
            key = self.key_var.get().strip().encode()
            Fernet(key)
        except Exception:
            messagebox.showerror(
                "Invalid Key", "Please enter a valid Fernet key.")
            return
        fn = self.parent.encrypt_files if self.mode == "encrypt" else self.parent.decrypt_files
        fn(self.files, key)
        self.destroy()

# ─── MAIN APP ──────────────────────────────────────────────────────────────────


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        W, H = 700, 400
        self.title("Criptify")
        self.geometry(f"{W}x{H}")
        self.resizable(False, False)
        self._center_on_screen(W, H)

    def _center_on_screen(self, w: int, h: int) -> None:
        """Place the window in the exact centre of the primary monitor."""
        self.update_idletasks()            # make sure winfo data is up-to-date
        scr_w = self.winfo_screenwidth()
        scr_h = self.winfo_screenheight()
        x = (scr_w - w) // 2
        y = (scr_h - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        if tb is not None:
            tb.Style("darkly", master=self)

        self.canvas = tk.Canvas(self, bg=DARK_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.rain = MatrixRain(self.canvas)
        self.canvas.bind("<Configure>", lambda _e: self.rain.reset_geometry())

        self._build_front()

    def _build_front(self):
        fg = tk.Frame(self.canvas, bg=DARK_BG)
        fg.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            fg, text=LOGO, bg=DARK_BG, fg=GREEN,
            font=("Courier New", 9), justify="center"
        ).pack()
        make_button(fg, "Select File(s)…", self._select_files).pack(pady=40)

    # --------------- file selection --------------
    def _select_files(self):
        paths = [Path(p)
                 for p in filedialog.askopenfilenames(title="Choose file(s)")]
        if not paths:
            return
        mode = "decrypt" if any(
            p.suffix == ".enc" for p in paths) else "encrypt"
        KeyDialog(self, mode, paths)

    def encrypt_files(self, files: Iterable[Path], key: bytes):
        msgs = [f"🔒 {p.name} → {encrypt_file(key, p).name}" for p in files]
        self._show_results(msgs, header="🔒 Encryption complete!")

    def decrypt_files(self, files: Iterable[Path], key: bytes):
        msgs, success = [], True

        for p in files:
            out = decrypt_file(key, p)
            if out is None:
                msgs.append(f"⛔ Failed to decrypt {p.name}")
                success = False
            else:
                msgs.append(f"🔓 {p.name} → {out.name}")

        header = "🔓 Decryption complete!" if success else "⛔ Decryption failed"
        self._show_results(msgs, header=header)

    # --------------- results overlay ----------------------

    def _show_results(self, lines: List[str], header: str):
        overlay = tk.Frame(self.canvas, bg=DARK_BG)
        overlay.place(relwidth=1, relheight=1)

        tk.Label(overlay, text=header, fg=GREEN, bg=DARK_BG,
                 font=("Helvetica", 20, "bold")).pack(pady=(40, 20))

        box = tk.Text(overlay, height=12, width=60, bg="#141414", fg=FG,
                      relief="flat", padx=12, pady=12, state="disabled")
        box.pack()
        box.configure(state="normal")
        for ln in lines:
            box.insert("end", ln + "\n")
        box.configure(state="disabled")

        make_button(overlay, "OK", overlay.destroy).pack(pady=30)


if __name__ == "__main__":
    App().mainloop()
