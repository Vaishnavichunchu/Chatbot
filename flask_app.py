from flask import Flask, render_template, request, jsonify



from flask_cors import CORS
from flask import Flask, g
import sqlite3
import nltk
nltk.download('punkt')
nltk.download('wordnet')

from chatbot import get_response_data, store_response_data, clean_up_sentence

app = Flask(__name__)
CORS(app)


@app.get('/')
def index_get():
    return render_template('base.html')


@app.get('/search')
def search():
    with app.app_context():
        print("calling db to fetch data ")
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect('Search.db')
           
            cursor = db.execute("Select tag||' ; '|| answer from Search order by count desc limit 3;")
            searches = cursor.fetchall()
            searches = [x[0] for x in searches]
            print("Top searches after update are ", str(searches))
            cursor = db.execute("Select * from Search")
            all_searches = cursor.fetchall()
            all_searches = [x[0] for x in all_searches]
            print("All searches after update are ", str(all_searches))
           

            
    return searches

@app.post('/predict')
def predict():
    text = request.get_json().get('message')
    print(">>>", text)
    query, tag, response = get_response_data(text)
    message = {'query': query,'tag' : tag,'answer': response}
    if "://" in str(message["answer"]):
        store_response_data(tag,message["answer"], app)
    return jsonify(message)


if __name__ == '__main__':
    app.run(debug=True)
