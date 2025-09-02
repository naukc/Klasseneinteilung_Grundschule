import pandas as pd

def speichere_einteilung_excel(einteilung, df, pfad="Klasseneinteilung.xlsx"):
    """
    Exportiert:
      - Blatt 'Einteilung' mit allen Schülern
      - Pro Klasse ein eigenes Blatt:
          * Tabelle mit Wünschen 1–4
          * Alle nicht erfüllten Wünsche rot markiert
          * Zusammenfassung: Jungen / Mädchen / Auffälligkeitssumme
    Benötigt: xlsxwriter
    """
    df = df.copy()
    df["Auffaelligkeit_Score"] = pd.to_numeric(df["Auffaelligkeit_Score"], errors="coerce").fillna(0)

    with pd.ExcelWriter(pfad, engine="xlsxwriter") as writer:
        wb  = writer.book
        red = wb.add_format({"bg_color": "#FF9999"})
        bold = wb.add_format({"bold": True})

        alle_klassen_df = []

        for k_idx, klasse_ids in enumerate(einteilung, start=1):
            klassen_df = df.loc[klasse_ids].copy()
            klassen_df["Klasse"] = k_idx

            sheet = f"Klasse_{k_idx}"
            klassen_df.to_excel(writer, sheet_name=sheet, index=True)
            ws = writer.sheets[sheet]

            # Wunsch-Spalten einfärben, wenn Wunsch nicht in Klasse
            cols = [str(c) for c in klassen_df.columns]
            wunsch_cols = [c for c in cols if c.lower().startswith("wunsch")]
            for wcol in wunsch_cols:
                if wcol not in cols:
                    continue
                col_idx = cols.index(wcol) + 1  # +1 wegen Indexspalte
                klasse_set = set(map(int, klasse_ids))
                for row_idx, (_, row) in enumerate(klassen_df.iterrows(), start=1):
                    val = pd.to_numeric(row.get(wcol), errors="coerce")
                    if pd.notna(val) and int(val) not in klasse_set:
                        ws.write(row_idx+1, col_idx, int(val), red)  
                        # row_idx+1: header=0, Index=0. DataFrame startet bei Zeile 1 im Excel

            # Zusammenfassung unten
            base_row = len(klassen_df) + 3
            j = (klassen_df["Geschlecht"] == "m").sum()
            m = (klassen_df["Geschlecht"] == "w").sum()
            s = float(klassen_df["Auffaelligkeit_Score"].sum())

            ws.write(base_row, 0, "Zusammenfassung:", bold)
            ws.write(base_row+1, 0, f"Jungen: {j}")
            ws.write(base_row+2, 0, f"Mädchen: {m}")
            ws.write(base_row+3, 0, f"Auffälligkeitssumme: {int(s) if s.is_integer() else s}")

            alle_klassen_df.append(klassen_df)

        # Übersicht
        gesamt_df = pd.concat(alle_klassen_df)
        gesamt_df.to_excel(writer, sheet_name="Einteilung", index=True)
        ws_all = writer.sheets["Einteilung"]

        cols = [str(c) for c in gesamt_df.columns]
        wunsch_cols = [c for c in cols if c.lower().startswith("wunsch")]
        for wcol in wunsch_cols:
            col_idx = cols.index(wcol) + 1
            for row_idx, (_, row) in enumerate(gesamt_df.iterrows(), start=1):
                val = pd.to_numeric(row.get(wcol), errors="coerce")
                klasse_id = row["Klasse"]
                klasse_set = set(map(int, einteilung[int(klasse_id)-1]))
                if pd.notna(val) and int(val) not in klasse_set:
                    ws_all.write(row_idx+1, col_idx, int(val), red)

    print(f"✅ Einteilung mit Wunsch-Markierungen gespeichert: {pfad}")
