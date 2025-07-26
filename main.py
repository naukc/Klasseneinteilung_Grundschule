# Importiert die Funktionen aus unseren neuen Dateien
from datenlader import lade_schuelerdaten
from algorithmus import erstelle_zufaellige_einteilung, bewerte_einteilung
import config # Importiert die Konfigurationsvariablen

def main():
    """Die Hauptfunktion, die den gesamten Prozess steuert."""
    schueler_df = lade_schuelerdaten("schuelerliste.xlsx")

    if schueler_df is None:
        return # Bricht ab, wenn die Datei nicht geladen werden konnte

    # Berechne einmalig die Gesamtstatistiken für die Stufe
    gesamtstatistiken = {
        'avg_migration': schueler_df[schueler_df['Migrationshintergrund / 2. Staatsangehörigkeit'] == 'Ja'].shape[0] / len(schueler_df),
        'avg_auffaelligkeit_summe': schueler_df['Auffaelligkeit_Score'].sum() / config.ANZAHL_KLASSEN
    }
    print("\nGesamtstatistiken für die Stufe berechnet:")
    print(f" - Durchschnittlicher Migrationsanteil: {gesamtstatistiken['avg_migration']:.2%}")
    print(f" - Ideale 'Belastungssumme' pro Klasse: {gesamtstatistiken['avg_auffaelligkeit_summe']:.2f}")

    # Erstelle eine erste, zufällige Einteilung
    print(f"\nErstelle eine zufällige Einteilung für {config.ANZAHL_KLASSEN} Klassen...")
    start_einteilung = erstelle_zufaellige_einteilung(schueler_df.index)

    for i, klasse in enumerate(start_einteilung):
        print(f"Klasse {i+1}: {klasse}")

    # Bewerte diese zufällige Einteilung
    start_score = bewerte_einteilung(start_einteilung, schueler_df, gesamtstatistiken)
    print(f"\nBewertung der zufälligen Einteilung: {start_score:.2f} Punkte")

# Dieser Standard-Block stellt sicher, dass main() nur ausgeführt wird,
# wenn das Skript direkt gestartet wird.
if __name__ == "__main__":
    main()