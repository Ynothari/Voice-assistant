import os
import datetime
import pyttsx3
import speech_recognition as sr
import requests
import webbrowser

# =========================== CONFIGURATION ============================ #

# Text-to-speech engine initialization
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Female voice

# API keys (replace with your real keys)
serpapi_key = "0ad90729f3b43284e4b84a684d70076e2b5d3cd2a0d8c5bbd8afc7bc3349e206"
weather_api_key = "6f7ddc83a6fb6ef393098942e91d5159"

# Common program search paths
program_paths = [r"C:\Program Files", r"C:\Program Files (x86)", r"C:\Users\awmha\AppData\Local"]

# =========================== CORE FUNCTIONS =========================== #

def speak(text):
    """Convert text to speech and print to console."""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def wish_user():
    """Greet the user according to the time of day."""
    hour = datetime.datetime.now().hour
    greeting = "Good Morning!" if hour < 12 else "Good Afternoon!" if hour < 18 else "Good Evening!"
    speak(f"{greeting} I am your Assistant. How can I help you today?")

def take_command():
    """Listen from the microphone and return recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            speak("Listening timed out. Please try again.")
            return "none"

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return "none"
    except sr.RequestError as e:
        speak("Speech service is down.")
        print(f"Speech recognition error: {e}")
        return "none"

# =========================== FEATURE FUNCTIONS =========================== #

def open_application(app_name):
    """Open an application by searching its executable name."""
    app_exec = app_name.lower().strip() + ".exe"
    found = False

    for path in program_paths:
        for root, dirs, files in os.walk(path):
            if app_exec in (f.lower() for f in files):
                os.startfile(os.path.join(root, app_exec))
                speak(f"Opening {app_name}")
                found = True
                return

    speak(f"Couldn't find {app_name} on this system. Searching online instead.")
    webbrowser.open(f"https://www.google.com/search?q={app_name}")

def tell_time_and_date():
    """Speak current time and date."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%B %d, %Y")
    speak(f"The time is {time_str} and today's date is {date_str}.")

def get_weather(city):
    """Fetch and speak weather data from OpenWeatherMap."""
    if not city:
        speak("You didn't specify a city.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"

    try:
        res = requests.get(url)
        data = res.json()
        if data.get("cod") != 200:
            speak("City not found. Please try again.")
            return

        main = data["main"]
        weather_desc = data["weather"][0]["description"]
        temp = main["temp"]
        humidity = main["humidity"]
        wind_speed = data["wind"]["speed"]

        speak(f"The weather in {city} is {weather_desc}. "
              f"Temperature: {temp}°C, Humidity: {humidity}%, Wind speed: {wind_speed} meters per second.")
    except Exception as e:
        speak("Could not fetch weather information.")
        print(f"Weather API error: {e}")

def search_serpapi(query):
    """Search and speak answers using SerpAPI."""
    try:
        url = f"https://serpapi.com/search.json?engine=google&q={query}&api_key={serpapi_key}"
        res = requests.get(url)
        data = res.json()

        if "answer_box" in data:
            answer = data["answer_box"].get("answer") or data["answer_box"].get("snippet")
            if answer:
                speak(f"The answer is: {answer}")
                return

        if "organic_results" in data and data["organic_results"]:
            result = data["organic_results"][0]
            snippet = result.get("snippet") or result.get("title")
            speak(f"The top result says: {snippet}")
            return

        speak("I couldn't find a direct answer.")
    except Exception as e:
        speak("Search failed.")
        print(f"SerpAPI error: {e}")

# =========================== MAIN LOOP =========================== #

def main():
    wish_user()
    while True:
        query = take_command()
        if query == "none":
            continue

        if "weather" in query:
            speak("Which city?")
            city = take_command()
            if city != "none":
                get_weather(city)

        elif any(word in query for word in ["time", "date"]):
            tell_time_and_date()

        elif "open" in query:
            app = query.replace("open", "").strip()
            if app:
                open_application(app)
            else:
                speak("Please specify the application name.")

        elif any(word in query for word in ["search", "who", "what", "where", "how", "why"]):
            search_serpapi(query)

        elif any(word in query for word in ["exit", "quit", "bye", "stop"]):
            speak("Goodbye!")
            break

        else:
            speak("I'm not sure how to help with that. Please try another command.")

# =========================== ENTRY POINT =========================== #

if __name__ == "__main__":
    main()
