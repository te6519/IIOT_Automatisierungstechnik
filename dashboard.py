import pandas as pd
import matplotlib.pyplot as plt
import time

# CSV-Dateiname, den auch dein MQTT-Skript verwendet
csv_filename = "bottles_data.csv"

# Interaktiven Modus von Matplotlib aktivieren
plt.ion()

# Erstelle ein Plot-Fenster
fig, ax = plt.subplots(figsize=(10, 6))

print("Starte Live-Visualisierung... Schließe das Fenster zum Beenden.")

try:
    while True:
        try:
            # Nutzt tail(), um nur die neuesten Flaschen anzuzeigen, falls die Datei riesig wird
            df = pd.read_csv(csv_filename).tail(50)
            
            ax.clear()
            
            # 3. Wenn noch keine Daten da sind
            if df.empty:
                ax.text(0.5, 0.5, 'Warte auf Daten...\n(MQTT Skript ausführen!)', 
                        horizontalalignment='center', verticalalignment='center')
            else:
                # Da die Flaschen-IDs text/nummern sind, nutzen wir sie als X-Achse
                x_labels = df['bottle'].astype(str)
                
                # Vibrations-Daten der drei Dispenser extrahieren
                # .fillna(0) setzt fehlende Werte auf 0, falls eine Flasche noch nicht fertig ist
                vib_red = df['vibration_red'].fillna(0)
                vib_blue = df['vibration_blue'].fillna(0)
                vib_green = df['vibration_green'].fillna(0)
                
                # Wir plotten alle 3 Dispenser in einem Diagramm mit entsprechenden Farben
                ax.plot(x_labels, vib_red, marker='o', linestyle='-', color='red', label='Rot')
                ax.plot(x_labels, vib_blue, marker='s', linestyle='-', color='blue', label='Blau')
                ax.plot(x_labels, vib_green, marker='^', linestyle='-', color='green', label='Grün')
                
                # Legende aktivieren, um die Linien zuordnen zu können
                ax.legend()
                
                ax.set_title("Live-Vibrationen der Dispenser pro Flasche")
                ax.set_xlabel("Flaschen ID (Letzte 50)")
                ax.set_ylabel("Vibration Index")
                
                # X-Achsen-Labels rotieren, falls sie zu lang sind
                plt.xticks(rotation=45)
                
                # Raster im Hintergrund
                ax.grid(True, linestyle='--', alpha=0.7)

            # Layout anpassen (sorgt dafür dass abgeschnittene Texte reinpassen)
            plt.tight_layout()
            
            # 5. Aktualisieren und kurz warten
            # plt.pause übernimmt das Zeichnen der Grafik für uns
            plt.pause(2.0)
            
        except FileNotFoundError:
            print("CSV-Datei noch nicht gefunden. Bitte zuerst das MQTT Skript starten!")
            time.sleep(2)
            
        except Exception as e:
            print(f"Fehler beim Zeichnen (Datei ggf. gerade beim Speichern): {e}")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nVisualisierung beendet.")
