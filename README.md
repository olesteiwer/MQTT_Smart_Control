# MQTT Smart Control V5

Ein IoT-System auf Basis von MQTT und Raspberry Pi zur Überwachung von Sensoren, Speicherung von Messwerten und automatischer Steuerung einer Klimaanlage.

---

# Funktionen

✅ MQTT Kommunikation

✅ Automatische Geräteerkennung

✅ Live Dashboard

✅ Temperaturüberwachung

✅ Temperaturdiagramme

✅ SQLite Datenbank

✅ Klimaautomatik

✅ Manuelle Klimasteuerung

✅ Online-/Offline Erkennung

✅ Weboberfläche

✅ MQTT Geräteverwaltung

✅ Plug & Play Geräteintegration

---

# Projektaufbau

```text
Pi1
│
├── Mosquitto MQTT Broker
├── Flask Webserver
├── SQLite Datenbank
├── MQTT Smart Control Dashboard
└── Klimaautomatik

Pi2
│
├── DHT11 Temperatursensor
└── MQTT Client

Pi3
│
├── Klima Controller
├── LED als Klimaanlage
└── MQTT Client
```

---

# Hardware

## Pi1 - Server

### Hardware

- Raspberry Pi
  
### Aufgaben

- MQTT Broker
- Flask Webserver
- SQLite Datenbank
- Dashboard
- Klimaautomatik

### Software

- Python
- Flask
- SQLite
- Mosquitto
- Chart.js
- Paho MQTT

---

## Pi2 - Temperatursensor

### Hardware

- Raspberry Pi
- DHT11

### Aufgaben

- Temperatur messen
- Luftfeuchtigkeit messen
- MQTT Werte senden

### Gesendete MQTT Topics

```text
device/pi2/temperature
device/pi2/humidity
device/pi2/status
device/pi2/info
```

---

## Pi3 - Klima Controller

### Hardware

- Raspberry Pi Zero / Raspberry Pi
- LED (Simulation der Klimaanlage)

### Aufgaben

- MQTT Befehle empfangen
- Klimaanlage schalten
- Status zurückmelden

### Verwendete MQTT Topics

```text
device/pi3/ac
device/pi3/acstatus
device/pi3/status
device/pi3/info
```

### Funktionsweise

```text
Pi2 misst Temperatur
        │
        ▼
Pi1 verarbeitet Daten
        │
        ▼
Klimaautomatik entscheidet
        │
        ▼
Pi3 schaltet Klimaanlage
```

---

# Installation

## MQTT Broker

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
```

Autostart aktivieren:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

---

## Python Pakete

### Pi1

```bash
pip install flask paho-mqtt
```

### Pi2

```bash
pip install paho-mqtt
```

Zusätzlich für DHT11:

```bash
pip install adafruit-circuitpython-dht
```

### Pi3

```bash
pip install paho-mqtt
```

---

# Starten

## Pi1

```bash
python app.py
```

## Pi2

```bash
python client.py
```

## Pi3

```bash
python client.py
```

---

# Klimaautomatik

Die Klimaautomatik arbeitet mit zwei Schwellwerten.

Beispiel:

```text
EIN ab: 28°C

AUS unter: 24°C
```

### Verhalten

```text
30°C → Klimaanlage EIN

28°C → Klimaanlage EIN

25°C → Klimaanlage bleibt EIN

24°C → Klimaanlage AUS

20°C → Klimaanlage AUS
```

Dadurch wird ständiges Ein- und Ausschalten verhindert (Hysterese).

---

# Dashboard

Das Dashboard zeigt:

- Geräteübersicht
- Gerätestatus
- Temperatur
- Klimaanlagenstatus
- Temperaturdiagramm
- Klimaeinstellungen

Die Geräteverwaltung befindet sich im Zahnrad-Menü.

```text
⚙️ Einstellungen

├── Geräte
├── Klimaautomatik
├── Schwellwerte
└── Manuelle Steuerung
```

---

# Datenbank

## Tabelle

```sql
sensor_data
```

## Inhalt

```text
ID
Gerät
Sensor
Wert
Zeitstempel
```

### Beispiel

```text
1
pi2
temperature
24.6
25.09.2026 09:45:10
```

---

# MQTT Struktur

## Pi2

```text
device/pi2/temperature
device/pi2/humidity
device/pi2/status
device/pi2/info
```

## Pi3

```text
device/pi3/ac
device/pi3/acstatus
device/pi3/status
device/pi3/info
```

---

# MQTT Smart Control

MQTT Smart Control dient als zentrale Steuerungseinheit.

### Funktionen

- Datenerfassung
- Datenspeicherung
- Visualisierung
- Automatisierung
- Geräteüberwachung
- Klimasteuerung

---

# Plug & Play Geräte

MQTT Smart Control erkennt neue MQTT Geräte automatisch.

Damit ein neues Gerät im Dashboard erscheint, muss es nur:

1. Mit dem MQTT Broker verbunden sein
2. Status senden
3. Eine Gerätebeschreibung senden
4. Sensorwerte senden

Danach erscheint das Gerät automatisch im Dashboard.

Es sind keine Änderungen an der Webseite notwendig.

---

# Voraussetzungen für neue Geräte

Mindestens installieren:

```bash
sudo apt update

pip install paho-mqtt
```

Zusätzlich die Bibliothek des jeweiligen Sensors.

### Beispiele

DHT11

```bash
pip install adafruit-circuitpython-dht
```

HC-SR04 Ultraschallsensor

```bash
pip install paho-mqtt
```

Bodenfeuchtigkeit

```bash
pip install paho-mqtt
```

Lichtsensor

```bash
pip install paho-mqtt
```

---

# Verbindung zum MQTT Broker

Jeder neue Raspberry Pi verbindet sich mit Pi1:

```python
client.connect(
    "IP_VON_PI1",
    1883
)
```

---

# Automatische Registrierung

Beim Start sendet jedes Gerät:

```python
client.publish(
    "device/pi4/info",
    json.dumps({
        "name": "Mein Sensor",
        "sensors": [
            "temperature"
        ]
    }),
    retain=True
)
```

Außerdem:

```python
client.publish(
    "device/pi4/status",
    "online",
    retain=True
)
```

---

# Beispiel: Ultraschallsensor

### MQTT Topics

```text
device/pi4/info
device/pi4/status
device/pi4/distance
```

### Wert senden

```python
client.publish(
    "device/pi4/distance",
    distance
)
```

### Dashboard

```text
Ultraschall Sensor

distance

53.4
```

Das Gerät erscheint automatisch im Dashboard.

---

# Beispiel: Bodenfeuchtigkeitssensor

### MQTT Topics

```text
device/pi5/info
device/pi5/status
device/pi5/soil
```

### Wert senden

```python
client.publish(
    "device/pi5/soil",
    soil_value
)
```

### Anzeige

```text
Bodenfeuchtigkeit

78
```

---

# Beispiel: Lichtsensor

### MQTT Topics

```text
device/pi6/info
device/pi6/status
device/pi6/light
```

### Wert senden

```python
client.publish(
    "device/pi6/light",
    light_value
)
```

### Anzeige

```text
Lichtsensor

421
```

---

# Aktueller Plug & Play Status

Derzeit erkennt MQTT Smart Control automatisch:

✅ Neue Geräte

✅ Neue MQTT Clients

✅ Online-/Offline Zustände

✅ Temperaturwerte

✅ Luftfeuchtigkeitswerte

✅ Klima Controller

✅ Beliebige MQTT Werte

✅ Automatische Dashboard Anzeige

✅ Automatische Geräteverwaltung

---

# Was automatisch funktioniert

Wenn ein Gerät sendet:

```text
device/pi4/info
```

mit:

```json
{
  "name": "Mein Sensor",
  "sensors": [
    "temperature"
  ]
}
```

Dann passiert automatisch:

✅ Gerät erscheint im Dashboard

✅ Gerät erscheint im Geräte-Menü

✅ Sensorwerte werden angezeigt

✅ Online-/Offline Überwachung aktiv

✅ MQTT Smart Control verwaltet das Gerät

Es ist keine Änderung an Datenbank oder Webseite erforderlich.

---

# Aktuelle Einschränkungen

Temperatursensoren besitzen bereits:

✅ Live Anzeige

✅ Datenbank Speicherung

✅ Temperaturdiagramm

Andere Sensoren wie:

```text
distance
soil
light
pressure
water
```

werden bereits automatisch erkannt und angezeigt.

Aktuell besitzen sie jedoch noch kein eigenes Diagramm.

---

# Geplante Erweiterungen

✅ Automatische Diagramme für beliebige Sensoren

✅ Dynamische Sensor-Karten

✅ Mehrere Klima Controller

✅ CSV Export

✅ Benutzerverwaltung

✅ Alarmfunktionen

✅ Sensorgruppen

✅ Mobile Ansicht

---

# Projektziel

Ziel des Projekts ist die Entwicklung einer modularen IoT-Plattform zur Überwachung und Steuerung von Geräten über MQTT.

Das System ist so aufgebaut, dass weitere Sensoren und Aktoren problemlos hinzugefügt werden können.

### Beispiele

```text
Pi4 → Bodenfeuchtigkeit

Pi5 → Wasserpumpe

Pi6 → Lichtsensor

Pi7 → Relais

Pi8 → Ultraschallsensor

Pi9 → OLED Display
```

Durch die automatische Geräteerkennung müssen neue Geräte nicht manuell in die Weboberfläche eingetragen werden.

---

# Aktueller Entwicklungsstand

✅ MQTT Broker

✅ Flask Dashboard

✅ SQLite Datenbank

✅ Temperaturdiagramme

✅ Klimaautomatik

✅ Geräteverwaltung

✅ Automatische Geräteerkennung

✅ Manuelle Klimasteuerung

✅ Online-/Offline Überwachung

✅ Raspberry Pi MQTT Clients

🔄 Automatische Diagramme für alle Sensortypen

🔄 Mehrere Temperatursensoren

🔄 Mehrere Klima Controller

🔄 CSV Export

🔄 Benutzerverwaltung

---

# Fazit

MQTT Smart Control V5 ist bereits zu etwa 90 % Plug & Play.

Neue Raspberry Pis können mit wenigen Zeilen Code und einer MQTT Verbindung automatisch in das Dashboard integriert werden.

Aktuell müssen neue Sensoren lediglich ihre Daten per MQTT veröffentlichen und eine Gerätebeschreibung senden. Danach erscheinen sie automatisch im Dashboard und werden überwacht.

---
