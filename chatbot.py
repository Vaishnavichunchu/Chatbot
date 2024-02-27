from tensorflow.keras.models import load_model
from flask import Flask, g
import sqlite3
from nltk.stem import WordNetLemmatizer
import random
import json
import pickle
import numpy as np
import nltk

from autocorrect import Speller
import nltk
nltk.download('punkt')
nltk.download('wordnet')

# Create a spell checker object
spell = Speller(lang='en')

print

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

model = load_model('chatbot_model.h5')


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(
        word.lower()) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.15
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        print("result ", r)
        if r[1] > 0.5:
            return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    try:
        tag = intents_list[0]['intent']
        print(intents_list)
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                print("res", result)
                break
        return tag,result
    except:
        return "tag","I do not understand..."


print("GO! Bot is running!")


def get_response_data(message):
    orig = message

    message = spell(message.lower())
    message = message.replace("chariot","chatbot")
    message = message.replace("academy","academics")
    message=message.replace("hotel","hostel")
    message=message.replace("ipac","iqac")
    message=message.replace("take me to","")
    message=message.replace("die","eie")
    message=message.replace("cbs","csbs")
    message=message.replace("carry","")
    message=message.replace("ns","nss")
    message=message.replace("had","hod")
    message=message.replace("naming","nagini")
    message=message.replace("narendra","rajendra")
    message=message.replace("mama","mam")
    message=message.replace("hanss","jhansi")
    message=message.replace("gallica","mallika")
    message=message.replace("examinationss","examinations")
    message=message.replace("go to the","")
    message = message.replace("hamlet","eamcet")
    message = message.replace("transsport","transport")
    message=message.replace("open","")
    if orig.lower() != message.lower():
        print("Corrected to ", message)

    ints = predict_class(message)
    tag, res = get_response(ints, intents)
    return message, tag, res


def store_response_data(tag,answer, app):
    with app.app_context():
        print("calling db to store data ")
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect('Search.db')
            db.execute('CREATE TABLE IF NOT EXISTS Search (count NUMBER, answer VARCHAR2, tag VARCHAR2 PRIMARY KEY)')
            # db.execute('ALTER TABLE Search ADD CONSTRAINT primary_tag PRIMARY KEY (tag)')
          
            db.execute('INSERT OR IGNORE INTO Search values(0,?, ?) ', [answer,tag])
            db.execute('UPDATE Search set count = count +1 where answer = ?;', [answer])
            db.commit()
            cursor = db.execute("Select * from Search order by count desc")
            searches = cursor.fetchall()
            db.close()
            print("Top searches after update are ", str(searches))
    return
