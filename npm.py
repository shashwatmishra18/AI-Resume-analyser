from datetime import datetime
import webbrowser
import requests
import speech_recognition as sr
import pyttsx3
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query.lower()
    except BaseException as ex:
        print("Could not understand audio:")
        return ""
        

greet_msgs = ['hi', 'hello', 'hey', 'greetings','hello there']
date_msgs = ['date',' tell me the date','what is the date today?']
time_msgs = ['time',' tell me the time','what is the time now?']
news_msgs =['news','tell me the news','what is the latest news?']
def get_news():
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=695e07af402f4b119f0703e9b19f4683"
    response = requests.get(url)
    data = response.json()
    articles = data['articles']
    for i in range(len(articles)):
        print(articles[i]['title'])

chat  =True
while chat:
    user_msg = input("Enter your message: ").lower()
    if user_msg in greet_msgs:
        print("Hello User. How may I help you?")
    elif user_msg in date_msgs:
        print(f"today date is : {datetime.now().date()} ")
    elif user_msg in time_msgs:
        current_time = datetime.now().time()
        print(f"Time is:", current_time.strftime("%I:%M:%S %p"))
    elif 'open' in user_msg:
        website_name = user_msg.split('open ')[-1]
        webbrowser.open(f"https://{website_name}.com")
    elif "calculate" in user_msg:
        expression = user_msg.split()[-1]
        result = eval(expression)
        print("Result is:", result) 
    elif user_msg in news_msgs:
        get_news()
    elif user_msg == 'bye':
        print("Goodbye! Have a great day!")
        chat = False
    else:
        print("Can't understand your message.")