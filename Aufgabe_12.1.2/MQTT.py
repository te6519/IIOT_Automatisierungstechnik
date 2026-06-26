import paho.mqtt.client as mqtt
import json
import csv
import os
import time
from tinydb import TinyDB

# Lade Konfiguration
try:
    with open('config.json', 'r') as conf_file:
        config = json.load(conf_file)
except FileNotFoundError:
    print('config.json nicht gefunden, fallback auf hardcoded Werte.')
    config = {
        'mqtt_broker': '158.180.44.197',
        'mqtt_port': 1883,
        'mqtt_user': 'bobm',
        'mqtt_password': 'letmein',
        'mqtt_topic': 'aut/SoSe26/learning_factory_simulation/#'
    }

csv_filename = 'bottles_data.csv'
db = TinyDB('bottles_data.json')

csv_columns = [
    'bottle', 'recipe', 
    'fill_red', 'vibration_red', 
    'fill_blue', 'vibration_blue', 
    'fill_green', 'vibration_green', 
    'temp', 'final_weight', 'is_cracked', 'drop_oscillation'
]

if not os.path.exists(csv_filename):
    with open(csv_filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()

bottle_data = {}

def transform(topic, payload_bytes):
    try:
        decoded_payload = payload_bytes.decode()
        data = json.loads(decoded_payload)
        bottle_id = data.get('bottle')
        
        if bottle_id:
            if bottle_id not in bottle_data:
                bottle_data[bottle_id] = {col: None for col in csv_columns}
                bottle_data[bottle_id]['bottle'] = bottle_id
                
            topic_end = topic.split('/')[-1]
            
            if 'dispenser' in topic_end:
                color = data.get('dispenser')
                fill_level = data.get('fill_level_grams')
                vibration = data.get('vibration-index')
                
                if not bottle_data[bottle_id]['recipe'] and 'recipe' in data:
                    bottle_data[bottle_id]['recipe'] = data.get('recipe')
                
                if color in ['red', 'blue', 'green']:
                    bottle_data[bottle_id][f'fill_{color}'] = fill_level
                    bottle_data[bottle_id][f'vibration_{color}'] = vibration
                    
            elif topic_end == 'temperature':
                bottle_data[bottle_id]['temp'] = data.get('temperature_C')
            elif 'final_weight' in topic:
                bottle_data[bottle_id]['final_weight'] = data.get('final_weight')
            elif topic_end == 'drop_oscillation':
                bottle_data[bottle_id]['drop_oscillation'] = str(data.get('drop_oscillation'))
            elif topic_end == 'ground_truth':
                if 'is_cracked' in data:
                    val = str(data['is_cracked']).strip().lower()
                    bottle_data[bottle_id]['is_cracked'] = int(val in ('true', '1'))
            return bottle_id, bottle_data[bottle_id], topic_end
    except (json.JSONDecodeError, UnicodeDecodeError):
        pass
    return None, None, None

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f'Verbunden mit MQTT Broker {config["mqtt_broker"]}')
        client.subscribe(config['mqtt_topic'], qos=0)
    else:
        print(f'Verbindung fehlgeschlagen, Grund: {reason_code}')

def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    print(f'Verbindung unterbrochen, versuche Neuaufbau... (Grund: {reason_code})')

def on_message(client, userdata, message):
    bottle_id, updated_data, topic_end = transform(message.topic, message.payload)
    if bottle_id and updated_data:
        if topic_end == 'ground_truth':
            print(f'Flasche {bottle_id} abgeschlossen. Speichere in CSV & TinyDB...')
            # CSV schreiben
            with open(csv_filename, mode='a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=csv_columns)
                writer.writerow(updated_data)
            # TinyDB schreiben
            db.insert(updated_data)
            del bottle_data[bottle_id]

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.username_pw_set(config['mqtt_user'], config['mqtt_password'])
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_message = on_message

while True:
    try:
        mqttc.connect(config['mqtt_broker'], config['mqtt_port'])
        mqttc.loop_forever()
    except Exception as e:
        print(f'MQTT Fehler: {e}. Versuche Neustart in 5 Sekunden...')
        time.sleep(5)