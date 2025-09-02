from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, optimiere_einteilung
from export_excel import speichere_einteilung_excel
import config
import pandas as pd

def main():
    df = lade_schuelerdaten("schuelerliste.xlsx")
    if df is None or df.empty:
        print("Keine Schülerdaten gefunden.")
        return

    sp_mig = 'Migrationshintergrund / 2. Staatsangehörigkeit'
    sp_auff = 'Auffaelligkeit_Score'

    df[sp_auff] = pd.to_numeric(df[sp_auff], errors="coerce").fillna(0)

    gesamtstats = {
        "avg_migration": (df[sp_mig] == "Ja").sum() / len(df),
        "avg_auffaelligkeit_summe": df[sp_auff].sum() / config.ANZAHL_KLASSEN,
    }

    start = erstelle_zufaellige_einteilung(df.index, config.ANZAHL_KLASSEN)
    einteilung, score = optimiere_einteilung(start, df, gesamtstats, config.ANZAHL_KLASSEN)

    # Konsolen-Plausis
    print("\nBeste gefundene Klasseneinteilung:\n" + "="*35)
    for i, klasse_ids in enumerate(einteilung, start=1):
        kdf = df.loc[klasse_ids]
        j = (kdf["Geschlecht"] == "m").sum()
        m = (kdf["Geschlecht"] == "w").sum()
        s = kdf[sp_auff].sum()
        print(f"\n--- Klasse {i} ---")
        print(kdf[["Vorname", "Name", "Geschlecht", "Sprengel", sp_auff]])
        print(f"  Jungen: {j}, Mädchen: {m}, Auffälligkeitssumme: {s}")

    # Excel-Export (mit Plausis und Rotfärbung)
    speichere_einteilung_excel(einteilung, df)

if __name__ == "__main__":
    main()
