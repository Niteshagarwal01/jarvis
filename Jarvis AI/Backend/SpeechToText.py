from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
from deep_translator import GoogleTranslator
from langdetect import detect
from indic_transliteration.sanscript import transliterate, ITRANS, DEVANAGARI

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = "en";  // This will be replaced dynamically
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the placeholder language with the language from .env
HtmlCode = HtmlCode.replace('recognition.lang = "en"', f'recognition.lang = "{InputLanguage}"')

# Write the modified HTML to a file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define template path
TemplDirPath = f"{os.getcwd()}/Frontend/Files"
os.makedirs(TemplDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(f"{TemplDirPath}/Status.data", "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's", "can you"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def UniversalTranslator(text):
    try:
        lang = detect(text)
        if lang == 'en':
            text = transliterate(text, ITRANS, DEVANAGARI)
        translated = GoogleTranslator(source='hi', target='en').translate(text)
        return translated
    except:
        return text


def SpeechRecognition():
    file_url = f"file://{os.getcwd()}/Data/Voice.html"
    driver.get(file_url)
    driver.find_element(by=By.ID, value="start").click()

    time.sleep(5)  # Give a few seconds to record

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text
            if Text:
                driver.find_element(by=By.ID, value="end").click()

                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("translating...")
                    translated = UniversalTranslator(Text)
                    return QueryModifier(translated)
        except:
            continue

if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)
