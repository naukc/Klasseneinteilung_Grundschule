from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, optimiere_einteilung
import config
import pandas as pd

def speichere_einteilung_excel(einteilung, df, pfad="Klasseneinteilung.xlsx"):
    """Speichert die finale Einteilung in eine Excel-Datei mit Übersicht und Klassentabs."""
    writer = pd.ExcelWriter(pfad, engine="openpyxl")

    # Übersichtstabelle
    alle = []
    for i, klasse_ids in enumerate(einteilung):
        tmp = df.loc[klasse_ids].copy()
        tmp["Klasse"] = i + 1
        alle.append(tmp)
    gesamt_df = pd.concat(alle)
    gesamt_df.to_excel(writer, sheet_name="Einteilung")

    # Einzelne Klassen
    for i, klasse_ids in enumerate(einteilung):
        klassen_df = df.loc[klasse_ids]
        klassen_df.to_excel(writer, sheet_name=f"Klasse_{i+1}")

    writer.close()
    print(f"✅ Einteilung in '{pfad}' gespeichert.")

def main():
    schueler_df = lade_schuelerdaten("schuelerliste.xlsx")
    if schueler_df is None:
        return

    spaltenname_migration = 'Migrationshintergrund / 2. Staatsangehörigkeit'
    spaltenname_auffaelligkeit = 'Auffaelligkeit_Score'

    gesamtstatistiken = {
        'avg_migration': schueler_df[schueler_df[spaltenname_migration] == 'Ja'].shape[0] / len(schueler_df),
        'avg_auffaelligkeit_summe': schueler_df[spaltenname_auffaelligkeit].sum() / config.ANZAHL_KLASSEN
    }

    start_einteilung = erstelle_zufaellige_einteilung(schueler_df.index, config.ANZAHL_KLASSEN)
    finale_einteilung, finaler_score = optimiere_einteilung(
        start_einteilung, schueler_df, gesamtstatistiken, config.ANZAHL_KLASSEN
    )

    print("\nBeste gefundene Klasseneinteilung:\n" + "="*35)
    for i, klasse_ids in enumerate(finale_einteilung):
        print(f"\n--- Klasse {i+1} ---")
        klassen_df = schueler_df.loc[klasse_ids]
        print(klassen_df[['Vorname', 'Name', 'Geschlecht', 'Sprengel', 'Auffaelligkeit_Score']])

    speichere_einteilung_excel(finale_einteilung, schueler_df)

if __name__ == "__main__":
    main()
