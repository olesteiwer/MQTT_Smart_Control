import paho.mqtt.client as mqtt
import adafruit_dht
import board
import json
import time

# ==========================
# Einstellungen
# ==========================

DEVICE_ID = "pi2"
BROKER = "172.20.10.7"

# DHT11 an GPIO4
dht = adafruit_dht.DHT11(board.D4)

# ==========================
# MQTT
# ==========================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

def on_connect(client, userdata, flags, reason_code, properties):

    print("MQTT verbunden")

    client.publish(
        f"device/{DEVICE_ID}/info",
        json.dumps({
            "name": "Temperatur Sensor Pi",
            "sensors": [
                "temperature",
                "humidity"
            ]
        }),
        retain=True
    )

    client.publish(
        f"device/{DEVICE_ID}/status",
        "online",
        retain=True
    )

client.on_connect = on_connect

client.will_set(
    f"device/{DEVICE_ID}/status",
    "offline",
    retain=True
)

client.connect(
    BROKER,
    1883,
    60
)

client.loop_start()

# ==========================
# Hauptschleife
# ==========================

try:

    while True:

        try:

            temperature = dht.temperature
            humidity = dht.humidity

            if temperature is not None and humidity is not None:

                print(
                    f"Temperatur: {temperature:.1f}°C | "
                    f"Feuchtigkeit: {humidity}%"
                )

                client.publish(
                    f"device/{DEVICE_ID}/temperature",
                    round(temperature, 1)
                )

                client.publish(
                    f"device/{DEVICE_ID}/humidity",
                    int(humidity)
                )

                client.publish(
                    f"device/{DEVICE_ID}/status",
                    "online"
                )

        except Exception as e:

            print(
                "DHT11 Fehler:",
                e
            )

        time.sleep(30)

except KeyboardInterrupt:

    print("Beendet")

finally:

    client.publish(
        f"device/{DEVICE_ID}/status",
        "offline",
        retain=True
    )

    client.disconnect()
