import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd

from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, optimiere_einteilung
import config

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klasseneinteilung Grundschule")
        self.geometry("900x600")
        self.minsize(700, 400)

        self.filepath = None
        self.schueler_df = None
        self.finale_einteilung = None

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Steuerbereich ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        self.file_button = ttk.Button(control_frame, text="1. Excel-Datei auswählen", command=self.select_file)
        self.file_button.pack(side=tk.LEFT, padx=5)

        self.class_label = ttk.Label(control_frame, text="2. Anzahl Klassen:")
        self.class_label.pack(side=tk.LEFT, padx=(20, 5))
        self.class_count_var = tk.StringVar(value=str(config.ANZAHL_KLASSEN))
        self.class_entry = ttk.Entry(control_frame, width=5, textvariable=self.class_count_var)
        self.class_entry.pack(side=tk.LEFT)

        self.start_button = ttk.Button(control_frame, text="3. Einteilung starten", command=self.start_allocation)
        self.start_button.pack(side=tk.LEFT, padx=20)

        self.save_button = ttk.Button(control_frame, text="Als Excel speichern", command=self.save_excel, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # --- Ergebnisanzeige ---
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        result_label = ttk.Label(result_frame, text="Ergebnisse:")
        result_label.pack(anchor="w")

        self.result_text = tk.Text(result_frame, wrap="word", height=20, width=100)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.result_text.config(yscrollcommand=self.scrollbar.set)

    def select_file(self):
        filepath = filedialog.askopenfilename(title="Excel-Datei auswählen", filetypes=[("Excel-Dateien", "*.xlsx")])
        if filepath:
            self.filepath = filepath
            self.schueler_df = lade_schuelerdaten(filepath)

    def start_allocation(self):
        if self.schueler_df is None:
            messagebox.showerror("Fehler", "Bitte zuerst eine Excel-Datei auswählen.")
            return

        try:
            anzahl_klassen = int(self.class_count_var.get())
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Klassenzahl eingeben.")
            return

        spaltenname_migration = 'Migrationshintergrund / 2. Staatsangehörigkeit'
        spaltenname_auffaelligkeit = 'Auffaelligkeit_Score'
        gesamtstatistiken = {
            'avg_migration': self.schueler_df[self.schueler_df[spaltenname_migration] == 'Ja'].shape[0] / len(self.schueler_df),
            'avg_auffaelligkeit_summe': self.schueler_df[spaltenname_auffaelligkeit].sum() / anzahl_klassen
        }

        start_einteilung = erstelle_zufaellige_einteilung(self.schueler_df.index, anzahl_klassen)
        self.finale_einteilung, finaler_score = optimiere_einteilung(
            start_einteilung, self.schueler_df, gesamtstatistiken, anzahl_klassen
        )

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, f"Finaler Score: {finaler_score:.2f}\n")
        self.result_text.insert(tk.END, "="*50 + "\n")
        for i, klasse_ids in enumerate(self.finale_einteilung):
            self.result_text.insert(tk.END, f"\n--- Klasse {i+1} ---\n")
            klassen_df = self.schueler_df.loc[klasse_ids]
            self.result_text.insert(tk.END, str(klassen_df[['Vorname', 'Name', 'Geschlecht', 'Sprengel', 'Auffaelligkeit_Score']]))
            self.result_text.insert(tk.END, "\n")

        self.save_button.config(state=tk.NORMAL)

    def save_excel(self):
        if self.finale_einteilung is None:
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel-Dateien", "*.xlsx")])
        if not filepath:
            return

        writer = pd.ExcelWriter(filepath, engine="openpyxl")
        alle = []
        for i, klasse_ids in enumerate(self.finale_einteilung):
            tmp = self.schueler_df.loc[klasse_ids].copy()
            tmp["Klasse"] = i + 1
            alle.append(tmp)
        gesamt_df = pd.concat(alle)
        gesamt_df.to_excel(writer, sheet_name="Einteilung")
        for i, klasse_ids in enumerate(self.finale_einteilung):
            self.schueler_df.loc[klasse_ids].to_excel(writer, sheet_name=f"Klasse_{i+1}")
        writer.close()

        messagebox.showinfo("Erfolg", f"Einteilung gespeichert unter:\n{filepath}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
