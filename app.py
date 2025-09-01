import os
from flask import Flask, render_template, request, jsonify
import gpiozero
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LEDs on Raspberry Pi (BCM numbering)
leds = {
    "bathroom": gpiozero.LED(17),
    "bedroom": gpiozero.LED(27),
    "kitchen": gpiozero.LED(22),
    "livingroom": gpiozero.LED(6),
    "garage": gpiozero.LED(13),
    "garden": gpiozero.LED(5),
}

led_states = {room: False for room in leds}

# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():
    return render_template("home.html", led_states=led_states)


@app.route("/toggle", methods=["POST"])
def toggle():
    data = request.get_json()
    room = data.get("room")

    if room not in leds:
        return jsonify({"error": "Invalid room"}), 400

    if led_states[room]:
        leds[room].off()
        led_states[room] = False
    else:
        leds[room].on()
        led_states[room] = True

    return jsonify({"room": room, "state": "ON" if led_states[room] else "OFF"})


@app.route("/status", methods=["GET"])
def status():
    return jsonify(led_states)


@app.route("/set", methods=["POST"])
def set_light():
    data = request.get_json()
    room = data.get("room")
    state = data.get("state")

    if room not in leds or state not in ["on", "off"]:
        return jsonify({"error": "Invalid input"}), 400

    if state == "on":
        leds[room].on()
        led_states[room] = True
    else:
        leds[room].off()
        led_states[room] = False

    return jsonify({"room": room, "state": state.upper()})


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a smart home assistant. Interpret commands to toggle lights (bathroom, bedroom, kitchen, livingroom, garage, garden)."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content

    # Parse message for LED control
    for room in leds:
        if room in user_message.lower():
            if "on" in user_message.lower():
                leds[room].on()
                led_states[room] = True
            elif "off" in user_message.lower():
                leds[room].off()
                led_states[room] = False

    return jsonify({"reply": reply, "led_states": led_states})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
