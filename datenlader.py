import pandas as pd

def lade_schuelerdaten(dateipfad):
    """Lädt die Schülerdaten aus einer Excel-Datei (.xlsx)."""
    try:
        daten = pd.read_excel(dateipfad, index_col='Schüler-ID')
        
        # NEUE ZEILE: Entfernt alle Zeilen, bei denen die Spalte 'Name' leer ist.
        daten.dropna(subset=['Name'], inplace=True)

        print("✅ Excel-Datei erfolgreich geladen.")
        print(f"Insgesamt {len(daten)} Schülerinnen und Schüler eingelesen.")
        return daten
    except FileNotFoundError:
        print(f"❌ Fehler: Die Datei unter '{dateipfad}' wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"❌ Ein Fehler ist aufgetreten: {e}")
        return None