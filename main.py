import os
import telebot
import google.generativeai as palm
import requests
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()

my_secret = os.environ['palm2']
my_secret2 = os.environ['bot']
my_secret4 = os.environ['test']
palm.configure(api_key=my_secret)

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 1,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024,
    'stop_sequences': [],
    'safety_settings': [
        {"category": "HARM_CATEGORY_DEROGATORY", "threshold": 4},
        {"category": "HARM_CATEGORY_TOXICITY", "threshold": 4},
        {"category": "HARM_CATEGORY_VIOLENCE", "threshold": 4},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": 4},
        {"category": "HARM_CATEGORY_MEDICAL", "threshold": 4},
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": 4},
    ]
}

bot = telebot.TeleBot(my_secret2)

chat_histories = {}

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_input = message.text
    chat_id = message.chat.id

    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    chat_histories[chat_id].append({"role": "user", "content": user_input})
    chat_histories[chat_id] = chat_histories[chat_id][-10:]

    bot.send_chat_action(chat_id=message.chat.id, action='typing')

    url = my_secret4
    payload = {"query": user_input}
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        search_results = response.json()
        prompt = f"Hello! I am HelpingAI, a chatbot developed by Abhay Koul, a 16-year-old who has been working on AI and AI-related projects since Jan 2023. If you're looking for more information about Abhay Koul's projects and HelpingAI, I would recommend joining the Discord community. You can find additional details there. For more info visit: https://github.com/HelpingAI, https://replit.com/@Devastation-war, join Discord https://discord.gg/2EeZcJjyRd. Based on the user's query '{user_input}' and the previous messages {chat_histories[chat_id]}, here are some insights based on the following search results: {search_results}. If the search results are insufficient, I will provide the best possible answer using the available information."

        # Generating a response using GenerativeAI based on the constructed prompt
        response = palm.generate_text(**defaults, prompt=prompt)
        if response.result:
            bot.reply_to(message, response.result)  # Sending the generated response to the user
        else:
            bot.reply_to(message, "I'm sorry, I couldn't generate a response. Please try again.")

bot.polling()  # Initiating bot polling to continuously check for new messages
