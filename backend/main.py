import os
import datetime
import pyttsx3
import speech_recognition as sr
import requests
import webbrowser

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set to female voice

# SerpAPI Key
serpapi_key = "0ad90729f3b43284e4b84a684d70076e2b5d3cd2a0d8c5bbd8afc7bc3349e206"  # Replace with your actual SerpAPI key

# OpenWeatherMap API Key
weather_api_key = "6f7ddc83a6fb6ef393098942e91d5159"  # Replace with your actual OpenWeatherMap API key

# Path where executables are likely installed
program_files = [r"C:\Program Files", r"C:\Program Files (x86)", r"C:\Users\awmha\AppData\Local"]

def speak(audio):
    """Converts text to speech and also prints to console."""
    print(f"Assistant: {audio}")  # Displaying text
    engine.say(audio)
    engine.runAndWait()

def wish_user():
    """Greets the user based on the time of the day."""
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am your Assistant. How can I help you today?")

def take_command():
    """Captures the user's voice and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower()
    except sr.WaitTimeoutError:
        speak("Sorry, I didn't hear anything. Please try again.")
        return "None"
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that. Can you please repeat?")
        return "None"
    except Exception as e:
        print(f"Error: {e}")
        speak("Sorry, I encountered an error. Please try again.")
        return "None"

def open_application(app_name):
    """Dynamically searches for the app's executable and opens it."""
    app_name = app_name.lower() + ".exe"
    found = False
    for path in program_files:
        for root, dirs, files in os.walk(path):
            if app_name in [f.lower() for f in files]:  # Case-insensitive check
                app_path = os.path.join(root, app_name)
                os.startfile(app_path)
                speak(f"Opening {app_name}")
                found = True
                break
        if found:
            break
    if not found:
        speak(f"Sorry, I couldn't find an application named {app_name}. Opening it in Chrome instead.")
        webbrowser.open(f"https://www.google.com/search?q={app_name.replace('.exe', '')}")

def tell_time():
    """Tells the current time and date."""
    str_time = datetime.datetime.now().strftime("%I:%M %p")
    str_date = datetime.datetime.now().strftime("%B %d, %Y")
    speak(f"The time is {str_time}. Today's date is {str_date}.")
    

def get_weather(city):
    """Gets weather information for a city using OpenWeatherMap API."""
    if not city:
        speak("You didn't specify a city. Please try again.")
        return
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(complete_url)
        weather_data = response.json()
        if weather_data["cod"] == 200:
            main = weather_data["main"]
            weather_desc = weather_data["weather"][0]["description"]
            temp = main["temp"]
            humidity = main["humidity"]
            wind_speed = weather_data["wind"]["speed"]
            speak(f"The temperature in {city} is {temp} degrees Celsius with {weather_desc}. "
                  f"Humidity is {humidity}% and wind speed is {wind_speed} m/s.")
        else:
            speak("City not found. Please try again.")
    except Exception as e:
        speak("Sorry, I couldn't retrieve the weather information.")
        print(f"Error fetching weather data: {e}")

def search_serpapi(query):
    """Search for answers using SerpAPI."""
    url = f"https://serpapi.com/search.json?engine=google&q={query}&api_key={serpapi_key}"
    try:
        response = requests.get(url)
        data = response.json()
        print(data)

        # Check for direct answers in the 'answer_box' field
        if 'answer_box' in data:
            answer = data['answer_box'].get('answer') or data['answer_box'].get('snippet')
            if answer:
                speak(f"The answer is: {answer}")
                return

        # If no direct answer, check for organic results
        elif 'organic_results' in data:
            first_result = data['organic_results'][0]
            speak(f"The answer is: {first_result['snippet']}")
            return

        else:
            speak("Sorry, I couldn't find a proper answer.")
    except Exception as e:
        speak("There was an error accessing SerpAPI.")
        print(f"Error accessing SerpAPI: {e}")

def main():
    wish_user()
    while True:
        query = take_command()

        if query == "none":
            continue

        if 'weather' in query:
            speak("Which city?")
            city = take_command()
            if city == "none" or not city:
                speak("I didn't understand the city name. Please try again.")
            else:
                get_weather(city)

        elif 'time' in query:
            tell_time()

        elif 'date' in query or "today's date" in query or "what is today's date" in query:
            str_date = datetime.datetime.now().strftime("%B %d, %Y")  # Directly fetching the current date
            speak(f"Today's date is {str_date}.")

        elif 'open' in query:
            app_name = query.replace("open", "").strip()
            open_application(app_name)

        elif 'search' in query or 'who' in query or 'what' in query or 'where' in query:
            search_serpapi(query)  # This triggers SerpAPI search for general queries.

        elif 'exit' in query or 'quit' in query:
            speak("Goodbye!")
            break

        else:
            speak("I'm not sure how to help with that. Please try again.")

if __name__ == '__main__':
    main()
