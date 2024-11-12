
'''import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob'''
import pandas as pd


nltk.download('all')

def preprocessing(tweet):
    words = word_tokenize(tweet.lower(),"english")
    wordsFiltered = [word for word in words if word not in stopwords.words('english')]
    lemmatizer = WordNetLemmatizer()
    wordsLemmatized = [lemmatizer.lemmatize(word) for word in wordsFiltered]
    processed_tweet = ' '.join(wordsLemmatized)
    return processed_tweet

def polarity(tweet):

    preprocessedTweet = preprocessing(tweet)
    return TextBlob(preprocessedTweet).sentiment.polarity

def main(dataset):

    positive = 0
    negative = 0
    neutral = 0
    sum = 0.0

    for tweet in dataset:
        polar = polarity(tweet)
        #print(polar)
        sum += polar
        if polar>0.4:
            positive+=1
        elif polar<-0.4:
            negative+=1
        else:
            neutral+=1

    positivePercentage = positive/len(dataset)
    negativePercentage = negative/len(dataset)
    average = sum/len(dataset)

    #print("In the past month,",len(dataset),"tweets have been published about the company\nOf those tweets,",positivePercentage*100,"% were positive and",negativePercentage*100,"% were negative\nThe average sentiment of the tweets (-1 negative, 1 positive) was",average)
    return positivePercentage,negativePercentage,average,len(dataset)


dataset = pd.read_csv(f"aggregated_data.csv")
print(main(dataset))



