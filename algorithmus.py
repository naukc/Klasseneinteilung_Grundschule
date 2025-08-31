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
    """Berechnet den Score einer Einteilung basierend auf den Regeln in config.py.
       Wünsche/Trennungen werden über SCHÜLER-IDs (Index) bewertet, nicht über Namen.
    """
    import pandas as pd
    score = 0

    # 1) Geschlechterbalance
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        maennlich = (klassen_df["Geschlecht"] == "m").sum()
        weiblich  = (klassen_df["Geschlecht"] == "w").sum()
        abweichung = abs(maennlich - weiblich)
        score += config.STRAFE_ABWEICHUNG_GESCHLECHT * abweichung

    # 2) Migrationshintergrund (Abweichung vom Stufenschnitt, in %-Punkten)
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        migrationsanteil = (klassen_df["Migrationshintergrund / 2. Staatsangehörigkeit"] == "Ja").sum() / len(klassen_df)
        abw_prozentpunkte = abs(migrationsanteil - gesamt_stats["avg_migration"]) * 100
        score += config.STRAFE_ABWEICHUNG_MIGRATION * abw_prozentpunkte

    # 3) Auffälligkeit (Abweichung von der idealen Klassensumme)
    for klasse in einteilung:
        klassen_df = df.loc[klasse]
        summe = pd.to_numeric(klassen_df["Auffaelligkeit_Score"], errors="coerce").fillna(0).sum()
        abweichung = abs(summe - gesamt_stats["avg_auffaelligkeit_summe"])
        score += config.STRAFE_ABWEICHUNG_AUFFAELLIGKEIT * abweichung

    # 4) Freundschaftswünsche (per ID)
    wunsch_spalten = [c for c in df.columns if str(c).startswith("Wunsch_")]
    if wunsch_spalten:
        for klasse in einteilung:
            klasse_set = set(map(int, klasse))  # schnelleres Membership-Checking
            klassen_df = df.loc[klasse]
            for schueler_id, row in klassen_df.iterrows():
                # alle gültigen Wunsch-IDs dieses Schülers sammeln (Duplikate vermeiden)
                wuensche_ids = []
                for wcol in wunsch_spalten:
                    wish_val = row.get(wcol)
                    wish_id = pd.to_numeric(wish_val, errors="coerce")
                    if pd.notna(wish_id):
                        wuensche_ids.append(int(wish_id))
                for wish_id in set(wuensche_ids):
                    if wish_id != int(schueler_id) and wish_id in klasse_set:
                        score += config.PUNKTE_WUNSCH_ERFUELLT

    # 5) Trennung (per ID)
    if "Trennen_Von" in df.columns:
        for klasse in einteilung:
            klasse_set = set(map(int, klasse))
            klassen_df = df.loc[klasse]
            for schueler_id, row in klassen_df.iterrows():
                sep_val = row.get("Trennen_Von")
                sep_id = pd.to_numeric(sep_val, errors="coerce")
                if pd.notna(sep_id):
                    sep_id = int(sep_id)
                    if sep_id in klasse_set:
                        score += config.STRAFE_TRENNUNG_MISSACHTET

    # 6. Gleichmäßige Verteilung der Jungen
    if config.STRAFE_ABWEICHUNG_JUNGEN != 0:
        # Ideal: alle Klassen haben ungefähr gleich viele Jungen
        gesamt_jungen = (df["Geschlecht"] == "m").sum()
        ideal_pro_klasse = gesamt_jungen / len(einteilung)

        for klasse in einteilung:
            klassen_df = df.loc[klasse]
            anzahl_jungen = (klassen_df["Geschlecht"] == "m").sum()
            abweichung = abs(anzahl_jungen - ideal_pro_klasse)
            score += config.STRAFE_ABWEICHUNG_JUNGEN * abweichung


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
