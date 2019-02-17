import re
import os
import sys
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import SGDClassifier
import subprocess
import joblib
import pandas as pd 
import numpy as np 

BUCKET = 'datathon-nlp-bucket' 

tweet_data = 'sentiment_analysis_data.csv' 
data_dir = 'gs://datathon-nlp-bucket' 

def preprocess_text(text):
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL', text)
    text = re.sub('@[^\s]+','USER', text)
    text = text.lower().replace("ё", "е")
    text = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = re.sub(' +',' ', text)
    return text.strip()

subprocess.check_call(['gsutil', 'cp', os.path.join(data_dir,
                                                    tweet_data),
                       tweet_data], stderr=sys.stdout)

n = ['ItemID', 'Sentiment', 'SentimentSource', 'SentimentText']
raw_data = pd.read_csv(tweet_data, names=n, header = 0, usecols=['Sentiment', 'SentimentText'])

neg, pos = raw_data.groupby('Sentiment')
neg_c = raw_data.Sentiment.value_counts()
sample_size = int(min(neg_c[0], neg_c[1]))
raw_data = np.concatenate((neg[1].values[:sample_size], pos[1].values[:sample_size]), axis=0)
labels = [1]*sample_size + [0]*sample_size


text_clf = Pipeline([('vect', CountVectorizer(stop_words='english')),
                     ('tfidf', TfidfTransformer()),
                     ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5, random_state=42)),]) 

tuned_parameters = {
    'vect__ngram_range': [(1, 1), (1, 2), (2, 2)],
    'tfidf__use_idf': (True, False),
    'tfidf__norm': ('l1', 'l2'),
    'clf__alpha': [1, 1e-1, 1e-2]
}

parameters_svm = {'vect__ngram_range': [(1, 1), (1, 2)],
                    'tfidf__use_idf': (True, False),
                    'clf-svm__alpha': (1e-2, 1e-3),
}
data = [preprocess_text(t[1]) for t in raw_data]

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.33, random_state=42)

clf = GridSearchCV(text_clf, parameters_svm, cv=3, verbose = 100)
clf.fit(x_train, y_train)

model_filename = 'model.joblib'
joblib.dump(clf, model_filename)

gcs_model_path = os.path.join('gs://', BUCKET,
    datetime.datetime.now().strftime('nlp_%Y%m%d_%H%M%S'), model_filename)
subprocess.check_call(['gsutil', 'cp', model_filename, gcs_model_path],
    stderr=sys.stdout)
