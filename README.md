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

Aufgaben:

- MQTT Broker
- Flask Webserver
- SQLite Datenbank
- Dashboard
- Klimaautomatik

Software:

- Python
- Flask
- SQLite
- Mosquitto
- Chart.js
- Paho MQTT

---

## Pi2 - Temperatursensor

Hardware:

- Raspberry Pi
- DHT11

Aufgaben:

- Temperatur messen
- Luftfeuchtigkeit messen
- MQTT Werte senden

Gesendete MQTT Topics:

```text
device/pi2/temperature
device/pi2/humidity
device/pi2/status
device/pi2/info
```

---

## Pi3 - Klima Controller

Hardware:

- Raspberry Pi Zero / Raspberry Pi
- LED (Simulation Klimaanlage)

Aufgaben:

- MQTT Befehle empfangen
- Klimaanlage schalten
- Status zurückmelden

Verwendete MQTT Topics:

```text
device/pi3/ac
device/pi3/acstatus
device/pi3/status
device/pi3/info
```

Funktionsweise:

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

Server:

```bash
pip install flask paho-mqtt
```

Pi2:

```bash
pip install paho-mqtt
```

Pi3:

```bash
pip install paho-mqtt
```

---

# Starten

## Pi1

```bash
python app.py
```

---

## Pi2

```bash
python client.py
```

---

## Pi3

```bash
python client.py
```

---

# Klimaautomatik

Die Klimaautomatik arbeitet mit zwei Grenzwerten.

Beispiel:

```text
Einschalten ab: 28°C
Ausschalten unter: 24°C
```

Verhalten:

```text
30°C → Klimaanlage EIN

28°C → Klimaanlage EIN

25°C → Klimaanlage bleibt EIN

24°C → Klimaanlage AUS

20°C → Klimaanlage AUS
```

Dadurch wird ständiges Ein- und Ausschalten verhindert.

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

Tabelle:

```sql
sensor_data
```

Inhalt:

```text
ID
Gerät
Sensor
Wert
Zeitstempel
```

Beispiel:

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

---

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

Funktionen:

- Datenerfassung
- Datenspeicherung
- Visualisierung
- Automatisierung
- Geräteüberwachung
- Klimasteuerung

---

# Projektziel

Ziel des Projekts ist die Entwicklung einer modularen IoT-Plattform zur Überwachung und Steuerung von Geräten über MQTT.

Das System ist so aufgebaut, dass weitere Sensoren und Aktoren problemlos hinzugefügt werden können.

Beispiele:

```text
Pi4 → Bodenfeuchtigkeit

Pi5 → Wasserpumpe

Pi6 → Lichtsensor

Pi7 → Relais
```

Durch die automatische Geräteerkennung müssen neue Geräte nicht manuell in die Weboberfläche eingetragen werden.
