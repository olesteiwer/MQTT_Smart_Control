import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json

# ==========================
# Einstellungen
# ==========================

DEVICE_ID = "pi3"

BROKER = "172.20.10.7"   # Pi1 IP anpassen

AC_LED_PIN = 17

# ==========================
# GPIO
# ==========================

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

GPIO.setup(
    AC_LED_PIN,
    GPIO.OUT
)

GPIO.output(
    AC_LED_PIN,
    GPIO.LOW
)

# ==========================
# MQTT
# ==========================

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

# ==========================
# MQTT Befehle
# ==========================

def on_message(client, userdata, msg):

    topic = msg.topic
    payload = msg.payload.decode()

    print(
        f"{topic}: {payload}"
    )

    if topic == "device/pi3/ac":

        if payload == "ON":

            GPIO.output(
                AC_LED_PIN,
                GPIO.HIGH
            )

            client.publish(
                "device/pi3/acstatus",
                "ON",
                retain=True
            )

            print(
                "Klimaanlage EIN"
            )

        elif payload == "OFF":

            GPIO.output(
                AC_LED_PIN,
                GPIO.LOW
            )

            client.publish(
                "device/pi3/acstatus",
                "OFF",
                retain=True
            )

            print(
                "Klimaanlage AUS"
            )

# ==========================
# MQTT Connect
# ==========================

def on_connect(
    client,
    userdata,
    flags,
    reason_code,
    properties
):

    print(
        "MQTT verbunden"
    )

    client.subscribe(
        "device/pi3/ac"
    )

    client.publish(
        "device/pi3/info",
        json.dumps({
            "name":
            "Klimaanlage",

            "sensors":
            [
                "acstatus"
            ]
        }),
        retain=True
    )

    client.publish(
        "device/pi3/status",
        "online",
        retain=True
    )

# ==========================
# MQTT Setup
# ==========================

client.on_connect = on_connect
client.on_message = on_message

client.will_set(
    "device/pi3/status",
    "offline",
    retain=True
)

client.connect(
    BROKER,
    1883,
    60
)

# ==========================
# Hauptschleife
# ==========================

try:

    client.loop_forever()

except KeyboardInterrupt:

    pass

finally:

    client.publish(
        "device/pi3/status",
        "offline",
        retain=True
    )

    GPIO.cleanup()
