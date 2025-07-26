from datenlader import lade_schuelerdaten
# Wichtig: Die neue Funktion hier importieren
from algorithmus import erstelle_zufaellige_einteilung, bewerte_einteilung, optimiere_einteilung
import config

def main():
    """Die Hauptfunktion, die den gesamten Prozess steuert."""
    schueler_df = lade_schuelerdaten("schuelerliste.xlsx")

    if schueler_df is None:
        return

    spaltenname_migration = 'Migrationshintergrund / 2. Staatsangehörigkeit'
    spaltenname_auffaelligkeit = 'Auffaelligkeit_Score'
    
    gesamtstatistiken = {
        'avg_migration': schueler_df[schueler_df[spaltenname_migration] == 'Ja'].shape[0] / len(schueler_df),
        'avg_auffaelligkeit_summe': schueler_df[spaltenname_auffaelligkeit].sum() / config.ANZAHL_KLASSEN
    }
    
    # Starte mit einer zufälligen Einteilung
    start_einteilung = erstelle_zufaellige_einteilung(schueler_df.index)
    
    # OPTIMIERE die Einteilung
    finale_einteilung, finaler_score = optimiere_einteilung(start_einteilung, schueler_df, gesamtstatistiken)
    
    # Gib das Endergebnis aus
    print("\nBeste gefundene Klasseneinteilung:\n" + "="*35)
    for i, klasse_ids in enumerate(finale_einteilung):
        print(f"\n--- Klasse {i+1} (Score-Beitrag wird noch nicht berechnet) ---")
        # Hole die Namen der Schüler für eine schönere Ausgabe
        klassen_df = schueler_df.loc[klasse_ids]
        print(klassen_df[['Vorname', 'Name', 'Geschlecht', 'Sprengel', 'Auffälligkeit_Score']])

if __name__ == "__main__":
    main()