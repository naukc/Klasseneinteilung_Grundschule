import pandas as pd
import numpy as np
import random
import copy
import config

# Funktion akzeptiert jetzt anzahl_klassen als Parameter
def erstelle_zufaellige_einteilung(schueler_ids, anzahl_klassen):
    zufaellig_gemischt = list(schueler_ids)
    random.shuffle(zufaellig_gemischt)
    return [list(klasse) for klasse in np.array_split(zufaellig_gemischt, anzahl_klassen)]

# Funktion akzeptiert jetzt anzahl_klassen als Parameter
def optimiere_einteilung(einteilung, df, gesamt_stats, anzahl_klassen):
    aktuelle_einteilung = copy.deepcopy(einteilung)
    bester_score = bewerte_einteilung(aktuelle_einteilung, df, gesamt_stats)
    
    print(f"\n🚀 Starte Optimierung... Anfangs-Score: {bester_score:.2f}")

    anzahl_iterationen = 500
    
    for i in range(anzahl_iterationen):
        if i % 50 == 0:
            print(f"   ...Iteration {i}/{anzahl_iterationen}, aktueller Score: {bester_score:.2f}")

        # anzahl_klassen wird jetzt als Parameter verwendet
        klasse1_idx, klasse2_idx = random.sample(range(anzahl_klassen), 2)
        
        if not aktuelle_einteilung[klasse1_idx] or not aktuelle_einteilung[klasse2_idx]:
            continue

        schueler1_pos = random.randrange(len(aktuelle_einteilung[klasse1_idx]))
        schueler2_pos = random.randrange(len(aktuelle_einteilung[klasse2_idx]))

        schueler1 = aktuelle_einteilung[klasse1_idx][schueler1_pos]
        schueler2 = aktuelle_einteilung[klasse2_idx][schueler2_pos]

        aktuelle_einteilung[klasse1_idx][schueler1_pos] = schueler2
        aktuelle_einteilung[klasse2_idx][schueler2_pos] = schueler1
        
        neuer_score = bewerte_einteilung(aktuelle_einteilung, df, gesamt_stats)

        if neuer_score > bester_score:
            bester_score = neuer_score
        else:
            aktuelle_einteilung[klasse1_idx][schueler1_pos] = schueler1
            aktuelle_einteilung[klasse2_idx][schueler2_pos] = schueler2
            
    print(f"🏁 Optimierung beendet. Finaler Score: {bester_score:.2f}")
    return aktuelle_einteilung, bester_score

# Die Funktion bewerte_einteilung bleibt unverändert
def bewerte_einteilung(einteilung, df, gesamt_stats):
    gesamt_score = 0
    spaltenname_migration = 'Migrationshintergrund / 2. Staatsangehörigkeit'
    spaltenname_auffaelligkeit = 'Auffaelligkeit_Score'
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
    for klasse_ids in einteilung:
        if not klasse_ids: continue
        klassen_df = df.loc[klasse_ids]
        maedchen_anteil = klassen_df[klassen_df['Geschlecht'] == 'w'].shape[0] / len(klassen_df)
        abweichung_geschlecht = abs(maedchen_anteil - 0.5) * len(klassen_df)
        gesamt_score += abweichung_geschlecht * config.STRAFE_ABWEICHUNG_GESCHLECHT
        migration_anteil_klasse = klassen_df[klassen_df[spaltenname_migration] == 'Ja'].shape[0] / len(klassen_df)
        abweichung_migration = abs(migration_anteil_klasse - gesamt_stats['avg_migration']) * 100
        gesamt_score += abweichung_migration * config.STRAFE_ABWEICHUNG_MIGRATION
        auffaelligkeit_summe_klasse = klassen_df[spaltenname_auffaelligkeit].sum()
        abweichung_auffaelligkeit = abs(auffaelligkeit_summe_klasse - gesamt_stats['avg_auffaelligkeit_summe'])
        gesamt_score += abweichung_auffaelligkeit * config.STRAFE_ABWEICHUNG_AUFFAELLIGKEIT
    return gesamt_score