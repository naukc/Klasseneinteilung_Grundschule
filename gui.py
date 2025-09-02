import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, optimiere_einteilung
from export_excel import speichere_einteilung_excel
import config

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klasseneinteilung Grundschule")
        self.geometry("900x600")

        self.filepath = None
        self.df = None
        self.einteilung = None

        top = ttk.Frame(self, padding=10); top.pack(fill=tk.BOTH, expand=True)
        ctl = ttk.Frame(top); ctl.pack(fill=tk.X)

        ttk.Button(ctl, text="1. Excel-Datei auswählen", command=self.pick).pack(side=tk.LEFT, padx=5)
        ttk.Label(ctl, text="2. Anzahl Klassen:").pack(side=tk.LEFT, padx=(20,5))
        self.n_var = tk.StringVar(value=str(config.ANZAHL_KLASSEN))
        ttk.Entry(ctl, width=5, textvariable=self.n_var).pack(side=tk.LEFT)
        ttk.Button(ctl, text="3. Einteilung starten", command=self.run).pack(side=tk.LEFT, padx=20)
        self.save_btn = ttk.Button(ctl, text="Als Excel speichern", command=self.save, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.out = tk.Text(top, wrap="word", height=25)
        self.out.pack(fill=tk.BOTH, expand=True, pady=10)

    def pick(self):
        p = filedialog.askopenfilename(title="Excel-Datei auswählen", filetypes=[("Excel", "*.xlsx")])
        if not p: return
        self.filepath = p
        self.df = lade_schuelerdaten(p)
        if self.df is None or self.df.empty:
            messagebox.showerror("Fehler", "Datei konnte nicht geladen werden.")
            return
        self.out.insert(tk.END, f"Geladen: {p}\n")

    def run(self):
        if self.df is None:
            messagebox.showerror("Fehler", "Bitte zuerst eine Excel-Datei auswählen."); return
        try:
            n = int(self.n_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Klassenzahl."); return

        sp_mig = 'Migrationshintergrund / 2. Staatsangehörigkeit'
        sp_auff = 'Auffaelligkeit_Score'
        self.df[sp_auff] = pd.to_numeric(self.df[sp_auff], errors="coerce").fillna(0)

        stats = {
            "avg_migration": (self.df[sp_mig] == "Ja").sum() / len(self.df),
            "avg_auffaelligkeit_summe": self.df[sp_auff].sum() / n,
        }

        start = erstelle_zufaellige_einteilung(self.df.index, n)
        self.einteilung, score = optimiere_einteilung(start, self.df, stats, n)

        # Textausgabe inkl. Plausis
        self.out.delete("1.0", tk.END)
        self.out.insert(tk.END, f"Finaler Score: {score:.2f}\n" + "="*50 + "\n")
        for i, klasse_ids in enumerate(self.einteilung, start=1):
            kdf = self.df.loc[klasse_ids]
            j = (kdf["Geschlecht"] == "m").sum()
            m = (kdf["Geschlecht"] == "w").sum()
            s = kdf[sp_auff].sum()
            self.out.insert(tk.END, f"\n--- Klasse {i} ---\n")
            self.out.insert(tk.END, str(kdf[["Vorname", "Name", "Geschlecht", "Sprengel", sp_auff]]) + "\n")
            self.out.insert(tk.END, f"Jungen: {j}, Mädchen: {m}, Auffälligkeitssumme: {s}\n")

        self.save_btn.config(state=tk.NORMAL)

    def save(self):
        if not self.einteilung or self.df is None:
            messagebox.showerror("Fehler", "Keine Einteilung vorhanden."); return
        p = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title="Einteilung speichern")
        if not p: return
        speichere_einteilung_excel(self.einteilung, self.df, p)
        messagebox.showinfo("Erfolg", f"Gespeichert unter:\n{p}")

if __name__ == "__main__":
    App().mainloop()
