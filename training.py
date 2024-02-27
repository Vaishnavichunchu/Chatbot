# from pickletools import optimize
# from matplotlib import ticker
# from pyparsing import Word
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn import metrics 
import nltk
nltk.download('punkt')
nltk.download('wordnet')


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

lemmatizer = WordNetLemmatizer()

intents = json.loads(open('intents.json').read())
print(len(intents))

words = []
classes = []
documents = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

ignore_letters = ['?', '!', '.']
words = [lemmatizer.lemmatize(word.lower())
         for word in words if word not in ignore_letters]

words = sorted(set(words))
classes = sorted(set(classes))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

training = []

output_empty = [0] * len(classes)
for document in documents:
    bag = []
    word_patterns = document[0]
    word_patterns = [lemmatizer.lemmatize(
        word.lower()) for word in word_patterns]
    for word in words:
        bag.append(1) if word in word_patterns else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(document[1])] = 1
    training.append([bag, output_row])


random.shuffle(training)
training = np.array(training)
train_x = list(training[:, 0])

regularize = train_x
train_y = list(training[:, 1])
regularize_label = train_y

# print("training data length", len(train_x[0]))

intents_test = json.loads(open('testing.json').read())
words_test = []
classes_test = []
documents_test = []

for intent in intents_test['intents']:
    for pattern in intent['patterns']:
        word_list_test = nltk.word_tokenize(pattern)
        words_test.extend(word_list_test)
        documents_test.append((word_list_test, intent['tag']))
        if intent['tag'] not in classes_test:
            classes_test.append(intent['tag'])

words_test = [lemmatizer.lemmatize(word)
              for word in words_test if word not in ignore_letters]
words_test = sorted(set(words_test))
classes_test = sorted(set(classes_test))
pickle.dump(words_test, open('words_test.pkl', 'wb'))
pickle.dump(classes_test, open('classes_test.pkl', 'wb'))

test_data = []

output_empty_test = [0] * len(classes_test)
for document in documents_test:
    bag_test = []
    word_patterns_test = document[0]
    word_patterns_test = [lemmatizer.lemmatize(
        word.lower()) for word in word_patterns_test]
    for word in words_test:
        bag_test.append(
            1) if word in word_patterns_test else bag_test.append(0)
    output_row_test = list(output_empty_test)
    output_row_test[classes_test.index(document[1])] = 1
    test_data.append([bag_test, output_row_test])

random.shuffle(test_data)
test_data = np.array(test_data)
test_x = list(test_data[:, 0])
test_y = list(test_data[:, 1])

#this will build the required neural network model which is sequential in nature
#we are adding two dense layers 128 and 64 each
# model.compile(loss='categorical_crossentropy',
#               optimizer=sgd, metrics=['accuracy'])
test_x = regularize
#we are using Schotastic Gradient Descent with learning rate of 0.01
#finally we are compiling and evaluating th model

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='tanh'))
model.add(Dropout(0.15))
model.add(Dense(64, activation='tanh'))
model.add(Dropout(0.15))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(learning_rate=0.01, weight_decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',
              optimizer=sgd, metrics=['accuracy'])
hist = model.fit(np.array(train_x), np.array(train_y),
                 epochs=200, batch_size=5, verbose=1)


#we are dumping into .h5 file
# sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
test_y = regularize_label
# hist = model.fit(np.array(train_x), np.array(train_y), validation_split=0.1,
#                  epochs=200, batch_size=5, verbose=1)

score = model.evaluate(np.array(test_x), np.array(test_y), verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

model.save('chatbot_model.h5', hist)
print('Done')
