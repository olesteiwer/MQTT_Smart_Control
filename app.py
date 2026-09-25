from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import threading
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

# ==========================
# Datenbank
# ==========================

db = sqlite3.connect(
    "mqtt_smart_control.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device TEXT,
    sensor TEXT,
    value REAL,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS climate_settings (
    device TEXT PRIMARY KEY,
    mode TEXT,
    on_temp REAL,
    off_temp REAL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO climate_settings
(
    device,
    mode,
    on_temp,
    off_temp
)
VALUES
(
    'pi3',
    'AUTO',
    28,
    24
)
""")

db.commit()

# ==========================
# Geräte
# ==========================

devices = {}

# ==========================
# MQTT Publisher
# ==========================

mqtt_publish_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

mqtt_publish_client.connect(
    "localhost",
    1883
)

mqtt_publish_client.loop_start()

# ==========================
# MQTT Nachrichten
# ==========================

def on_message(client, userdata, msg):

    topic = msg.topic
    payload = msg.payload.decode()

    print(f"{topic}: {payload}")

    parts = topic.split("/")

    if len(parts) < 3:
        return

    device = parts[1]
    sensor = parts[2]

    if device not in devices:

        devices[device] = {
            "name": device,
            "status": "offline",
            "sensors": []
        }

    if sensor == "info":

        try:

            info = json.loads(payload)

            devices[device]["name"] = info.get(
                "name",
                device
            )

            devices[device]["sensors"] = info.get(
                "sensors",
                []
            )

        except Exception as e:

            print(e)

        return

    devices[device][sensor] = payload

    # ==========================
    # Klimaautomatik
    # ==========================

    if (
        device == "pi2"
        and sensor == "temperature"
    ):

        try:

            temp = float(payload)

            climate = cursor.execute(
                """
                SELECT
                    mode,
                    on_temp,
                    off_temp
                FROM climate_settings
                WHERE device='pi3'
                """
            ).fetchone()

            if climate:

                mode = climate[0]
                on_temp = climate[1]
                off_temp = climate[2]

                print(
                    f"AUTO Temp={temp} "
                    f"ON={on_temp} "
                    f"OFF={off_temp}"
                )

                if mode == "AUTO":

                    if temp >= on_temp:

                        print(
                            "KLIMA EIN"
                        )

                        mqtt_publish_client.publish(
                            "device/pi3/ac",
                            "ON"
                        )

                    elif temp <= off_temp:

                        print(
                            "KLIMA AUS"
                        )

                        mqtt_publish_client.publish(
                            "device/pi3/ac",
                            "OFF"
                        )

        except Exception as e:

            print(e)

    # ==========================
    # Temperatur speichern
    # ==========================

    if sensor == "temperature":

        try:

            cursor.execute(
                """
                INSERT INTO sensor_data
                (
                    device,
                    sensor,
                    value,
                    timestamp
                )
                VALUES
                (
                    ?, ?, ?, ?
                )
                """,
                (
                    device,
                    sensor,
                    float(payload),
                    datetime.now().strftime(
                        "%d.%m.%Y %H:%M:%S"
                    )
                )
            )

            db.commit()

        except Exception as e:

            print(e)

# ==========================
# MQTT Thread
# ==========================

def mqtt_thread():

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_message = on_message

    client.connect(
        "localhost",
        1883
    )

    client.subscribe(
        "device/#"
    )

    client.loop_forever()

threading.Thread(
    target=mqtt_thread,
    daemon=True
).start()

# ==========================
# API
# ==========================

@app.route("/api/devices")
def api_devices():

    return jsonify(devices)


@app.route("/api/device/<device>")
def api_device(device):

    return jsonify(
        devices.get(device, {})
    )


@app.route("/api/history/<device>")
def api_history(device):

    rows = cursor.execute(
        """
        SELECT
            value,
            timestamp
        FROM sensor_data
        WHERE device=?
        ORDER BY id DESC
        LIMIT 100
        """,
        (device,)
    ).fetchall()

    rows.reverse()

    return jsonify([
        {
            "value": row[0],
            "time": row[1]
        }
        for row in rows
    ])

# ==========================
# Klima API
# ==========================

@app.route("/api/climate")
def api_climate():

    data = cursor.execute(
        """
        SELECT
            mode,
            on_temp,
            off_temp
        FROM climate_settings
        WHERE device='pi3'
        """
    ).fetchone()

    return jsonify({
        "mode": data[0],
        "on_temp": data[1],
        "off_temp": data[2]
    })


@app.route(
    "/api/climate/<mode>/<on_temp>/<off_temp>"
)
def save_climate(
    mode,
    on_temp,
    off_temp
):

    cursor.execute(
        """
        UPDATE climate_settings
        SET
            mode=?,
            on_temp=?,
            off_temp=?
        WHERE device='pi3'
        """,
        (
            mode,
            float(on_temp),
            float(off_temp)
        )
    )

    db.commit()

    return "OK"

# ==========================
# Klima Manuell
# ==========================

@app.route("/ac/on")
def ac_on():

    mqtt_publish_client.publish(
        "device/pi3/ac",
        "ON"
    )

    return "OK"


@app.route("/ac/off")
def ac_off():

    mqtt_publish_client.publish(
        "device/pi3/ac",
        "OFF"
    )

    return "OK"

# ==========================
# Webseite
# ==========================

@app.route("/")
def home():

    return """
<!DOCTYPE html>
<html>

<head>

<title>
MQTT Smart Control V5
</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

body{
    margin:0;
    font-family:Arial;
    background:#1e1e1e;
    color:white;
}

header{
    background:#111;
    padding:15px;
}

h1{
    margin:0;
    color:#4CAF50;
}

#gear{
    float:right;
    cursor:pointer;
    font-size:28px;
}

.card{
    background:#2e2e2e;
    padding:15px;
    margin:10px;
    border-radius:10px;
}

#topInfo{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:20px;
}

#sensorCards{
    display:flex;
    flex-wrap:wrap;
    gap:20px;
}

.sensorItem{
    min-width:140px;
}

#chartCard{
    margin-top:5px;
}

canvas{
    background:white;
    border-radius:10px;
    max-height:220px;
}

#menu{
    position:fixed;
    top:70px;
    right:20px;
    width:320px;
    background:#2e2e2e;
    border-radius:10px;
    padding:15px;
    display:none;
    box-shadow:0 0 15px black;
}

.deviceButton{
    width:100%;
    padding:10px;
    margin-bottom:5px;
    border:none;
    border-radius:5px;
    cursor:pointer;
}

input,
select{
    width:100%;
    padding:8px;
    margin-top:5px;
    margin-bottom:10px;
}

button{
    cursor:pointer;
}

</style>

</head>

<body>

<header>

<h1>

MQTT Smart Control V5

<span
id="gear"
onclick="toggleMenu()">

⚙️

</span>

</h1>

</header>

<div id="menu">

<h3>Geräte</h3>

<div id="deviceList">
Lade...
</div>

<hr>

<h3>Klimaanlage (Pi3)</h3>

Modus

<select id="climateMode">

<option value="AUTO">
Automatik
</option>

<option value="MANUAL">
Manuell
</option>

</select>

Einschalten ab

<input
id="onTemp"
type="number">

Ausschalten ab

<input
id="offTemp"
type="number">

<button onclick="saveClimate()">
Speichern
</button>

<br><br>

<button onclick="acOn()">
❄️ Klima EIN
</button>

<button onclick="acOff()">
🛑 Klima AUS
</button>

</div>

<div class="card">

<div id="topInfo">

<div>

<h2 id="deviceTitle">
Kein Gerät ausgewählt
</h2>

<p id="deviceStatus">
Status
</p>

</div>

<div id="sensorCards"></div>

</div>

</div>

<div class="card" id="chartCard">

<h2>
Temperaturverlauf
</h2>

<canvas id="chart"></canvas>

</div>

<script>

let currentDevice = null;
let chart = null;

history.scrollRestoration = "manual";

function toggleMenu()
{
    const menu =
        document.getElementById(
            "menu"
        );

    menu.style.display =
        menu.style.display === "block"
        ? "none"
        : "block";
}

function loadDevices()
{
    fetch("/api/devices")

    .then(r => r.json())

    .then(data =>
    {
        let html = "";

        let firstDevice = null;

        for(let id in data)
        {
            if(firstDevice === null)
            {
                firstDevice = id;
            }

            let icon =
                data[id].status === "online"
                ? "🟢"
                : "🔴";

            let active =
                currentDevice === id
                ? "background:#4CAF50;color:white;"
                : "";

            html += `
            <button
                class="deviceButton"
                style="${active}"
                onclick="selectDevice('${id}')">

                ${icon}
                ${data[id].name}

            </button>
            `;
        }

        document.getElementById(
            "deviceList"
        ).innerHTML = html;

        if(
            currentDevice === null &&
            firstDevice !== null
        )
        {
            currentDevice =
                firstDevice;

            updateDevice();
        }
    });
}

function selectDevice(device)
{
    currentDevice = device;

    loadDevices();

    updateDevice();
}

function updateDevice()
{
    if(!currentDevice)
    {
        return;
    }

    const scrollPos =
        window.scrollY;

    fetch(
        "/api/device/" +
        currentDevice
    )

    .then(r => r.json())

    .then(data =>
    {
        document.getElementById(
            "deviceTitle"
        ).innerText =
            data.name ||
            currentDevice;

        document.getElementById(
            "deviceStatus"
        ).innerText =
            "Status: " +
            (data.status || "offline");

        let html = "";

        for(let key in data)
        {
            if(
                key === "name" ||
                key === "status" ||
                key === "sensors" ||
                key === "humidity"
            )
            {
                continue;
            }

            let displayName = key;

            if(key === "temperature")
            {
                displayName =
                    "Temperatur";
            }

            if(key === "acstatus")
            {
                displayName =
                    "Klimaanlage";
            }

            html += `
            <div class="sensorItem">

                <h3>${displayName}</h3>

                <p>${data[key]}</p>

            </div>
            `;
        }

        document.getElementById(
            "sensorCards"
        ).innerHTML = html;

        if(currentDevice === "pi2")
        {
            document.getElementById(
                "chartCard"
            ).style.display = "block";

            loadChart();
        }
        else
        {
            document.getElementById(
                "chartCard"
            ).style.display = "none";
        }

        window.scrollTo(
            0,
            scrollPos
        );
    });
}

function loadChart()
{
    fetch(
        "/api/history/" +
        currentDevice
    )

    .then(r => r.json())

    .then(data =>
    {
        const labels =
            data.map(
                x => x.time.split(" ")[1]
            );

        const values =
            data.map(
                x => x.value
            );

        if(chart)
        {
            chart.destroy();
        }

        chart =
        new Chart(
            document.getElementById(
                "chart"
            ),
            {
                type:"line",

                data:
                {
                    labels: labels,

                    datasets:
                    [{
                        label:
                            "Temperatur °C",

                        data:
                            values,

                        borderColor:
                            "#4CAF50",

                        backgroundColor:
                            "rgba(76,175,80,0.2)",

                        tension: 0.4,

                        fill: true
                    }]
                },

                options:
                {
                    responsive: true,

                    maintainAspectRatio:false,

                    plugins:
                    {
                        legend:
                        {
                            labels:
                            {
                                color:"white"
                            }
                        }
                    },

                    scales:
                    {
                        x:
                        {
                            ticks:
                            {
                                color:"white"
                            }
                        },

                        y:
                        {
                            ticks:
                            {
                                color:"white"
                            }
                        }
                    }
                }
            }
        );
    });
}

function loadClimate()
{
    fetch("/api/climate")

    .then(r => r.json())

    .then(data =>
    {
        document.getElementById(
            "climateMode"
        ).value =
            data.mode;

        document.getElementById(
            "onTemp"
        ).value =
            data.on_temp;

        document.getElementById(
            "offTemp"
        ).value =
            data.off_temp;
    });
}

function saveClimate()
{
    const mode =
        document.getElementById(
            "climateMode"
        ).value;

    const on =
        document.getElementById(
            "onTemp"
        ).value;

    const off =
        document.getElementById(
            "offTemp"
        ).value;

    fetch(
        "/api/climate/"
        + mode
        + "/"
        + on
        + "/"
        + off
    );
}

function acOn()
{
    fetch("/ac/on");
}

function acOff()
{
    fetch("/ac/off");
}

setInterval(
    updateDevice,
    3000
);

setInterval(
    loadDevices,
    15000
);

loadDevices();
loadClimate();

</script>

</body>

</html>
"""
# ==========================
# Flask Start
# ==========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
