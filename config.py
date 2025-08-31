# Anzahl Klassen (Standardwert, kann in der GUI überschrieben werden)
ANZAHL_KLASSEN = 3 

# Positive Punkte
PUNKTE_WUNSCH_ERFUELLT = 30
PUNKTE_SPRENGEL_GLEICH = 3

# Negative Punkte (Strafen)
STRAFE_TRENNUNG_MISSACHTET = -1000
STRAFE_ABWEICHUNG_GESCHLECHT = -30      # pro Schüler Abweichung vom 50/50-Ideal
STRAFE_ABWEICHUNG_MIGRATION = -3       # pro Prozentpunkt Abweichung vom Stufenschnitt
STRAFE_ABWEICHUNG_AUFFAELLIGKEIT = -3  # pro Punkt Abweichung von der idealen "Belastungssumme"
STRAFE_ABWEICHUNG_JUNGEN = -500      # pro Jungen mehr als Mädchen (um zu viele Jungs in einer Klasse zu vermeiden)


# ------------------------------------
# Optimierungsparameter (Simulated Annealing)
# ------------------------------------
OPT_ITERATIONEN = 10000        # Anzahl Iterationen (10.000 = meist ausreichend gut)
OPT_START_TEMPERATUR = 150.0   # Start-Temperatur (höher = mehr Exploration am Anfang)
OPT_COOLING_RATE = 0.998       # Abkühlrate (langsames Abkühlen bringt bessere Lösungen)
