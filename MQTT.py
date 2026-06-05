import paho.mqtt.client as mqtt
import json
import csv
import os

broker = "158.180.44.197"
port = 1883
topic = "aut/SoSe26/learning_factory_simulation/#"

csv_filename = "bottles_data.csv"
# Alle von der Aufgabe geforderten Spalten für Termin 3 und 4:
csv_columns = [
    "bottle", "recipe", 
    "fill_red", "vibration_red", 
    "fill_blue", "vibration_blue", 
    "fill_green", "vibration_green", 
    "temp", "final_weight", "is_cracked", "drop_oscillation"
]

# Erstelle die CSV-Datei mit den Kopfzeilen, falls sie noch nicht existiert
if not os.path.exists(csv_filename):
    with open(csv_filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()

bottle_data = {}

def transform(topic, payload_bytes):
    try:
        # 1. Payload in Text umwandeln und als JSON laden
        decoded_payload = payload_bytes.decode()
        data = json.loads(decoded_payload)
        
        # 2. Die Flaschen-ID auslesen
        bottle_id = data.get("bottle")
        
        if bottle_id:
            if bottle_id not in bottle_data:
                bottle_data[bottle_id] = {
                    "bottle": bottle_id,
                    "recipe": None,
                    "fill_red": None,
                    "vibration_red": None,
                    "fill_blue": None,
                    "vibration_blue": None,
                    "fill_green": None,
                    "vibration_green": None,
                    "temp": None,
                    "final_weight": None,
                    "is_cracked": None,
                    "drop_oscillation": None
                }
            topic_end = topic.split("/")[-1]
            
            if "dispenser" in topic_end:
                color = data.get("dispenser")
                fill_level = data.get("fill_level_grams")
                vibration = data.get("vibration-index")
                
                # Wir merken uns das recipe einmalig
                if not bottle_data[bottle_id]["recipe"] and "recipe" in data:
                    bottle_data[bottle_id]["recipe"] = data.get("recipe")
                
                if color == "red":
                    bottle_data[bottle_id]["fill_red"] = fill_level
                    bottle_data[bottle_id]["vibration_red"] = vibration
                elif color == "blue":
                    bottle_data[bottle_id]["fill_blue"] = fill_level
                    bottle_data[bottle_id]["vibration_blue"] = vibration
                elif color == "green":
                    bottle_data[bottle_id]["fill_green"] = fill_level
                    bottle_data[bottle_id]["vibration_green"] = vibration
                    
            elif topic_end == "temperature":
                # Anmerkung: Normal gibt es 3 Temperaturen. Wenn nur "temp" gefordert ist, überschreiben wir.
                bottle_data[bottle_id]["temp"] = data.get("temperature_C")
                
            elif "final_weight" in topic:
                bottle_data[bottle_id]["final_weight"] = data.get("final_weight")
                
            elif topic_end == "drop_oscillation":
                # Als Array empfangen, aber als STRING speichern (laut Anleitung wichtig für CSV)
                bottle_data[bottle_id]["drop_oscillation"] = json.dumps(data.get("drop_oscillation"))
                
            elif topic_end == "ground_truth":
                if "is_cracked" in data:
                    val = str(data["is_cracked"]).strip().lower()
                    bottle_data[bottle_id]["is_cracked"] = int(val in ("true", "1"))
            return bottle_id, bottle_data[bottle_id], topic_end
            
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
        
    return None, None, None

def on_message(client, userdata, message):
    bottle_id, updated_data, topic_end = transform(message.topic, message.payload)
    
    if bottle_id and updated_data:
        print(f"Aktualisierte Daten für Flasche {bottle_id}:")
        print(json.dumps(updated_data, indent=4))
        print("-" * 40)
        
        # Wenn der Datensatz fertig ist (Ground Truth ist meist das Letzte in der Kette)
        # dann speichern wir ihn ab und löschen ihn aus dem Speicher
        if topic_end == "ground_truth":
            print(f"Flasche {bottle_id} abgeschlossen. Speichere in CSV...")
            with open(csv_filename, mode='a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_columns)
                writer.writerow(updated_data)
            
            # Speicher freigeben
            del bottle_data[bottle_id]
            
    else:
        print("Ignoriere Nachricht (Kein gültiges JSON oder keine bottle-ID)")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set("bobm", "letmein")
mqttc.on_message = on_message
mqttc.connect(broker, port)
mqttc.subscribe(topic, qos=0)

print(f"Warte auf Nachrichten unter: {topic}")
while True:
    mqttc.loop(0.5)