# Bericht zur Aufgabe 12.1.2

## Umsetzung
- `MQTT.py` liest Daten von `aut/SoSe26/learning_factory_simulation/#`.
- Bei `ground_truth` werden die Flaschendaten in `bottles_data.csv` und `bottles_data.json` gespeichert.
- Jede abgeschlossene Flasche bekommt einen `timestamp`.
- `dashboard.py` zeigt den bestehenden Flaschenverlauf und zusätzlich ein Zeitdiagramm.

## Ergebnisse
- Die Daten werden korrekt gespeichert und sind im Dashboard verfügbar.
- `vibration_red` ist deutlich höher als `vibration_blue` und `vibration_green`.
- Blau und Grün zeigen weniger Schwankung.

## Interpretation
- Der rote Kanal steht für einen anderen Prozesszustand oder stärkere Schwingung.
- Blau und Grün wirken stabiler, das spricht für konstante Bedingungen in diesen Bereichen.
- Ausreißer zeigen mögliche kurzzeitige Störungen im Prozess.
- Mit Timestamp sind die Daten gut für spätere Fehleranalyse und zeitliche Auswertung geeignet.
