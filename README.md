# MQTT Smart Control

Ein IoT-Überwachungssystem auf Basis von MQTT und Raspberry Pi.

Das Projekt ermöglicht die Überwachung von Sensorwerten, die automatische Erkennung von MQTT-Clients, die Speicherung von Messwerten in einer Datenbank sowie die Steuerung einer simulierten Klimaanlage.

---

# Funktionen

✅ MQTT-Kommunikation

✅ Automatische Geräteerkennung

✅ Live-Dashboard

✅ Temperaturüberwachung

✅ Temperaturverlauf als Diagramm

✅ SQLite-Datenbank

✅ Klimaautomatik

✅ Manuelle Klimasteuerung

✅ Online-/Offline-Erkennung

✅ Weboberfläche

---

# Hardware

## Pi1 - Server

Aufgaben:

- Flask Webserver
- MQTT Broker (Mosquitto)
- SQLite Datenbank
- MQTT Smart Control Dashboard

## Pi2 - Temperatursensor

Hardware:

- Raspberry Pi
- DHT11

Aufgaben:

- Temperatur messen
- Luftfeuchtigkeit messen
- MQTT-Werte senden

MQTT Topics:

```text
device/pi2/temperature
device/pi2/humidity
device/pi2/status
