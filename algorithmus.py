import pandas as pd
import numpy as np
import random
import config  # Importiert unsere Konfigurationsdatei

def erstelle_zufaellige_einteilung(schueler_ids):
    """Mischt alle Schüler und teilt sie zufällig auf die Klassen auf."""
    zufaellig_gemischt = list(schueler_ids)
    random.shuffle(zufaellig_gemischt)
    return [list(klasse) for klasse in np.array_split(zufaellig_gemischt, config.ANZAHL_KLASSEN)]

def bewerte_einteilung(einteilung, df, gesamt_stats):
    """Bewertet eine gesamte Klasseneinteilung und gibt eine Gesamtpunktzahl zurück."""
    gesamt_score = 0
    
    # 1. Beziehungen zwischen Schülern bewerten
    alle_paare = []
    for klasse in einteilung:
        paare_in_klasse = [(a, b) for i, a in enumerate(klasse) for b in klasse[i + 1:]]
        alle_paare.extend(paare_in_klasse)

    for id1, id2 in alle_paare:
        schueler1 = df.loc[id1]
        schueler2 = df.loc[id2]

        wunsch_spalten = ['Wunsch_1', 'Wunsch_2', 'Wunsch_3', 'Wunsch_4']
        if id2 in schueler1[wunsch_spalten].values or id1 in schueler2[wunsch_spalten].values:
            gesamt_score += config.PUNKTE_WUNSCH_ERFUELLT
            
        if schueler1['Sprengel'] == schueler2['Sprengel']:
            gesamt_score += config.PUNKTE_SPRENGEL_GLEICH

        if schueler1['Trennen_Von'] == id2 or schueler2['Trennen_Von'] == id1:
            gesamt_score += config.STRAFE_TRENNUNG_MISSACHTET

    # 2. Balance der einzelnen Klassen bewerten
    for klasse_ids in einteilung:
        klassen_df = df.loc[klasse_ids]
        
        maedchen_anteil = klassen_df[klassen_df['Geschlecht'] == 'w'].shape[0] / len(klassen_df)
        abweichung_geschlecht = abs(maedchen_anteil - 0.5) * len(klassen_df)
        gesamt_score += abweichung_geschlecht * config.STRAFE_ABWEICHUNG_GESCHLECHT

        migration_anteil_klasse = klassen_df[klassen_df['Migrationshintergrund / 2. Staatsangehörigkeit'] == 'Ja'].shape[0] / len(klassen_df)
        abweichung_migration = abs(migration_anteil_klasse - gesamt_stats['avg_migration']) * 100
        gesamt_score += abweichung_migration * config.STRAFE_ABWEICHUNG_MIGRATION
        
        auffaelligkeit_summe_klasse = klassen_df['Auffaelligkeit_Score'].sum()
        abweichung_auffaelligkeit = abs(auffaelligkeit_summe_klasse - gesamt_stats['avg_auffaelligkeit_summe'])
        gesamt_score += abweichung_auffaelligkeit * config.STRAFE_ABWEICHUNG_AUFFAELLIGKEIT

    return gesamt_score