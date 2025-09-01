import os
from flask import Flask, render_template, request, jsonify
import gpiozero
from gpiozero.pins.mock import MockFactory
# Only needed for Windows testing
gpiozero.Device.pin_factory = MockFactory()

from gpiozero import LED
from openai import OpenAI
from dotenv import load_dotenv




# export OPENAI_API_KEY="your_api_key_here"   # Linux/Mac
# setx OPENAI_API_KEY "your_api_key_here"     # Windows


app = Flask(__name__)
# client = OpenAI(api_key=os.getenv( "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"))
# client = genai.Client(api_key="YOUR_API_KEY")

# LEDs
bathroom_led = LED(17)
bedroom_led = LED(27)
kitchen_led = LED(22)
garden_led = LED(5)
living_room_led = LED(6)    
garage_led = LED(13)


led_states = {"bathroom": False, "bedroom": False, "kitchen": False, "garden": False, "living_room": False,
               "garage": False, }

@app.route("/")
def home():
    return render_template("home.html", led_states=led_states)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    # Ask ChatGPT
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a smart home assistant. Interpret commands to toggle lights (bathroom, bedroom, kitchen)."},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content

    # Simple LED trigger (optional: parse reply to actually toggle LEDs)
    if "bathroom" in user_message.lower():
        if "on" in user_message.lower():
            bathroom_led.on()
            led_states["bathroom"] = True
        elif "off" in user_message.lower():
            bathroom_led.off()
            led_states["bathroom"] = False

    if "bedroom" in user_message.lower():
        if "on" in user_message.lower():
            bedroom_led.on()
            led_states["bedroom"] = True
        elif "off" in user_message.lower():
            bedroom_led.off()
            led_states["bedroom"] = False

    if "kitchen" in user_message.lower():
        if "on" in user_message.lower():
            kitchen_led.on()
            led_states["kitchen"] = True
        elif "off" in user_message.lower():
            kitchen_led.off()
            led_states["kitchen"] = False

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
