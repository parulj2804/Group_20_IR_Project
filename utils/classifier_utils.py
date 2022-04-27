'''
Library Description

'''
import keras
import re
import nltk
from nltk.corpus import stopwords
import string
import pickle
from keras.preprocessing import sequence
from datetime import datetime
import pytz
import os
import logging

UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

class Text_Classifier():
    def __init__(self,):
        base_dir=os.getcwd()
        self.load_model=keras.models.load_model("/var/www/hate_burst/utils/models/EnglishModel.h5")
        with open('/var/www/hate_burst/utils/models/tokenizerEnglish.pickle', 'rb') as handle:
            self.load_tokenizer = pickle.load(handle)
        with open('/var/www/hate_burst/utils/models/stopwords.pkl', 'rb') as handle:
            self.stopwords = pickle.load(handle)
        self.stemmer = nltk.SnowballStemmer("english")

    def preprocessing(self,text):
        text = str(text).lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        text = [word for word in text.split(' ') if word not in self.stopwords]
        text=" ".join(text)
        text = [self.stemmer.stem(word) for word in text.split(' ')]
        text=" ".join(text)
        return text

    def predict(self, query):
        query = [self.preprocessing(query)]
        seq = self.load_tokenizer.texts_to_sequences(query)
        padded = sequence.pad_sequences(seq, maxlen=500)
        pred = self.load_model.predict(padded)
        #print("pred", pred) #TODO: Replace by Log Statement
        if pred < 0.5:
            # print("No Hate")
            return "No Hate"
        else:
            # print("Hate And Abusive")
            return "Hate And Abusive"

class Text_Classifier_Hindi():
    def __init__(self,):
        self.load_model=keras.models.load_model("/var/www/hate_burst/utils/models/HindiModel.h5")
        with open('/var/www/hate_burst/utils/models/tokenizerHindi.pickle', 'rb') as handle:
            self.load_tokenizer = pickle.load(handle)
        with open('/var/www/hate_burst/utils/models/stopwords.pkl', 'rb') as handle:
            self.stopwords = pickle.load(handle)
        self.stemmer = nltk.SnowballStemmer("english")

    def preprocessing(self,text):
        text = str(text).lower()
        text = re.sub('\[.*?\]', '', text)
        text = re.sub('https?://\S+|www\.\S+', '', text)
        text = re.sub('<.*?>+', '', text)
        text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
        text = re.sub('\n', '', text)
        text = re.sub('\w*\d\w*', '', text)
        text = [word for word in text.split(' ') if word not in self.stopwords]
        text=" ".join(text)
        text = [self.stemmer.stem(word) for word in text.split(' ')]
        text=" ".join(text)
        return text

    def predict(self, query):
        query = [self.preprocessing(query)]
        seq = self.load_tokenizer.texts_to_sequences(query)
        padded = sequence.pad_sequences(seq, maxlen=300)
        pred = self.load_model.predict(padded)
        #print("pred", pred) #TODO: Replace by Log Statement
        if pred < 0.4:
            # print("No Hate")
            return "No Hate"
        else:
            # print("Hate And Abusive")
            return "Hate And Abusive"
