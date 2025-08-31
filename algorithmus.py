import pandas as pd
import numpy as np
import random
import copy
import math
import config

def erstelle_zufaellige_einteilung(schueler_ids, anzahl_klassen):
    """Erstellt eine zufällige Startaufteilung in Klassen."""
    zufaellig_gemischt = list(schueler_ids)
    random.shuffle(zufaellig_gemischt)
    return [list(klasse) for klasse in np.array_split(zufaellig_gemischt, anzahl_klassen)]


def bewerte_einteilung(einteilung, df, gesamt_stats):
    """Berechnet den Score einer Einteilung basierend auf den Regeln in config.py."""
    score = 0

    # 1. Geschlechterbalance
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        maennlich = (klassen_df["Geschlecht"] == "m").sum()
        weiblich = (klassen_df["Geschlecht"] == "w").sum()
        abweichung = abs(maennlich - weiblich)
        score += config.STRAFE_ABWEICHUNG_GESCHLECHT * abweichung

    # 2. Migrationshintergrund
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        migrationsanteil = (klassen_df["Migrationshintergrund / 2. Staatsangehörigkeit"] == "Ja").sum() / len(klassen_df)
        abweichung = abs(migrationsanteil - gesamt_stats["avg_migration"]) * 100
        score += config.STRAFE_ABWEICHUNG_MIGRATION * abweichung

    # 3. Auffälligkeit
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        summe = klassen_df["Auffaelligkeit_Score"].sum()
        abweichung = abs(summe - gesamt_stats["avg_auffaelligkeit_summe"])
        score += config.STRAFE_ABWEICHUNG_AUFFAELLIGKEIT * abweichung

    # 4. Freundschaftswünsche
    wunsch_spalten = [sp for sp in df.columns if sp.startswith("Wunsch_")]
    if wunsch_spalten:
        for klasse in einteilung:
            klassen_df = df.loc[klasse]
            for _, row in klassen_df.iterrows():
                for wunsch_spalte in wunsch_spalten:
                    gewuenscht = row[wunsch_spalte]
                    if pd.isna(gewuenscht):
                        continue
                    if gewuenscht in klassen_df["Name"].values:
                        score += config.PUNKTE_WUNSCH_ERFUELLT

    # 5. Trennung
    if "Trennen_Von" in df.columns:
        for klasse in einteilung:
            klassen_df = df.loc[klasse]
            for _, row in klassen_df.iterrows():
                trennung = row.get("Trennen_Von")
                if pd.isna(trennung):
                    continue
                if trennung in klassen_df["Name"].values:
                    score += config.STRAFE_TRENNUNG_MISSACHTET

    return score


def optimiere_einteilung(
    einteilung, df, gesamt_stats, anzahl_klassen,
    iterationen=config.OPT_ITERATIONEN,
    start_temp=config.OPT_START_TEMPERATUR,
    cooling_rate=config.OPT_COOLING_RATE
):
    """
    Optimiert die Einteilung mit Simulated Annealing.
    """
    aktuelle_einteilung = copy.deepcopy(einteilung)
    bester_score = bewerte_einteilung(aktuelle_einteilung, df, gesamt_stats)
    bester_einteilung = copy.deepcopy(aktuelle_einteilung)

    aktuelle_score = bester_score
    temperatur = start_temp

    print(f"\n🚀 Starte Optimierung (Simulated Annealing)... Start-Score: {bester_score:.2f}")

    for i in range(iterationen):
        klasse1_idx, klasse2_idx = random.sample(range(anzahl_klassen), 2)
        if not aktuelle_einteilung[klasse1_idx] or not aktuelle_einteilung[klasse2_idx]:
            continue

        # zwei Schüler auswählen
        schueler1_pos = random.randrange(len(aktuelle_einteilung[klasse1_idx]))
        schueler2_pos = random.randrange(len(aktuelle_einteilung[klasse2_idx]))

        schueler1 = aktuelle_einteilung[klasse1_idx][schueler1_pos]
        schueler2 = aktuelle_einteilung[klasse2_idx][schueler2_pos]

        # Tauschen
        aktuelle_einteilung[klasse1_idx][schueler1_pos] = schueler2
        aktuelle_einteilung[klasse2_idx][schueler2_pos] = schueler1

        neuer_score = bewerte_einteilung(aktuelle_einteilung, df, gesamt_stats)
        delta = neuer_score - aktuelle_score

        # Akzeptanzkriterium (Simulated Annealing)
        if delta > 0 or random.random() < math.exp(delta / temperatur):
            aktuelle_score = neuer_score
            if neuer_score > bester_score:
                bester_score = neuer_score
                bester_einteilung = copy.deepcopy(aktuelle_einteilung)
        else:
            # zurücktauschen
            aktuelle_einteilung[klasse1_idx][schueler1_pos] = schueler1
            aktuelle_einteilung[klasse2_idx][schueler2_pos] = schueler2

        temperatur *= cooling_rate

        if i % 1000 == 0:
            print(f"Iteration {i}/{iterationen}, aktueller Score: {aktuelle_score:.2f}, bester Score: {bester_score:.2f}")

    print(f"🏁 Optimierung beendet. Bester gefundener Score: {bester_score:.2f}")
    return bester_einteilung, bester_score
