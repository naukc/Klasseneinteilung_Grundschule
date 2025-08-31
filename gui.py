import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Import unserer eigenen Module
from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, bewerte_einteilung, optimiere_einteilung

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Klasseneinteilung Grundschule")
        self.geometry("800x600")
        self.minsize(600, 400)
        self.filepath = None

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.file_button = ttk.Button(control_frame, text="1. Excel-Datei auswählen", command=self.select_file)
        self.file_button.pack(side=tk.LEFT, padx=5)

        self.class_label = ttk.Label(control_frame, text="2. Anzahl Klassen:")
        self.class_label.pack(side=tk.LEFT, padx=(20, 5))
        self.class_count_var = tk.StringVar(value="3")
        self.class_entry = ttk.Entry(control_frame, width=5, textvariable=self.class_count_var)
        self.class_entry.pack(side=tk.LEFT)

        self.start_button = ttk.Button(control_frame, text="3. Einteilung starten", command=self.start_allocation)
        self.start_button.pack(side=tk.LEFT, padx=20)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        self.selected_file_label = ttk.Label(status_frame, text="Keine Datei ausgewählt.")
        self.selected_file_label.pack(side=tk.LEFT, padx=5)

        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        result_label = ttk.Label(result_frame, text="Ergebnisse:")
        result_label.pack(anchor="w")
        self.result_text = tk.Text(result_frame, wrap="word", height=10, width=80)
        self.scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def select_file(self):
        filetypes = [("Excel-Dateien", "*.xlsx"), ("Alle Dateien", "*.*")]
        filepath = filedialog.askopenfilename(title="Excel-Liste auswählen", filetypes=filetypes)
        if filepath:
            self.filepath = filepath
            filename = filepath.split("/")[-1]
            self.selected_file_label.config(text=f"Ausgewählt: {filename}")

    def start_allocation(self):
        if not self.filepath:
            messagebox.showerror("Fehler", "Bitte zuerst eine Excel-Datei auswählen.")
            return
        
        try:
            anzahl_klassen = int(self.class_count_var.get())
            if anzahl_klassen < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Anzahl an Klassen eingeben (mindestens 2).")
            return

        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, "Berechne Einteilung... Bitte warten.\n")
        self.start_button.config(state="disabled")
        self.file_button.config(state="disabled")
        self.update_idletasks()

        try:
            schueler_df = lade_schuelerdaten(self.filepath)
            if schueler_df is None: return

            spaltenname_migration = 'Migrationshintergrund / 2. Staatsangehörigkeit'
            spaltenname_auffaelligkeit = 'Auffaelligkeit_Score'
    
            gesamtstatistiken = {
                'avg_migration': schueler_df[schueler_df[spaltenname_migration] == 'Ja'].shape[0] / len(schueler_df),
                'avg_auffaelligkeit_summe': schueler_df[spaltenname_auffaelligkeit].sum() / anzahl_klassen
            }
    
            start_einteilung = erstelle_zufaellige_einteilung(schueler_df.index, anzahl_klassen)
            finale_einteilung, finaler_score = optimiere_einteilung(start_einteilung, schueler_df, gesamtstatistiken, anzahl_klassen)

            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Optimierung beendet! Finaler Score: {finaler_score:.2f}\n\n")
            
            for i, klasse_ids in enumerate(finale_einteilung):
                self.result_text.insert(tk.END, f"--- Klasse {i+1} ---\n")
                klassen_df = schueler_df.loc[klasse_ids]
                # HIER IST DIE KORREKTUR:
                self.result_text.insert(tk.END, klassen_df.to_string(columns=['Vorname', 'Name', 'Geschlecht', 'Sprengel']) + "\n\n")
        
        except Exception as e:
            messagebox.showerror("Laufzeitfehler", f"Ein unerwarteter Fehler ist aufgetreten:\n{e}")
        
        finally:
            self.start_button.config(state="normal")
            self.file_button.config(state="normal")

if __name__ == "__main__":
    app = App()
    app.mainloop()