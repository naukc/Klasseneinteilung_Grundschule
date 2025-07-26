import tkinter as tk
from tkinter import ttk # ttk sorgt für modernere Widgets

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Fenstereinstellungen
        self.title("Klasseneinteilung Grundschule")
        self.geometry("800x600") 
        self.minsize(600, 400) # Mindestgröße des Fensters

        # Haupt-Container erstellen
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame für die Steuerung (oben) ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Knopf: Datei auswählen
        self.file_button = ttk.Button(control_frame, text="1. Excel-Datei auswählen")
        self.file_button.pack(side=tk.LEFT, padx=5)

        # Label und Eingabefeld für Klassenanzahl
        self.class_label = ttk.Label(control_frame, text="2. Anzahl Klassen:")
        self.class_label.pack(side=tk.LEFT, padx=(20, 5))
        
        self.class_count_var = tk.StringVar(value="3") # Variable für die Eingabe, Standardwert ist "3"
        self.class_entry = ttk.Entry(control_frame, width=5, textvariable=self.class_count_var)
        self.class_entry.pack(side=tk.LEFT)

        # Knopf: Einteilung starten
        self.start_button = ttk.Button(control_frame, text="3. Einteilung starten")
        self.start_button.pack(side=tk.LEFT, padx=20)

        # --- Frame für die Ergebnisse (unten) ---
        result_frame = ttk.Frame(main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Label für Ergebnis-Textfeld
        result_label = ttk.Label(result_frame, text="Ergebnisse:")
        result_label.pack(anchor="w") # "w" für west/linksbündig

        # Textfeld für die Ergebnisse mit Scrollbar
        self.result_text = tk.Text(result_frame, wrap="word", height=10, width=80)
        self.scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.result_text.pack(fill=tk.BOTH, expand=True)


# Hauptteil der Anwendung
if __name__ == "__main__":
    app = App()
    app.mainloop()