
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob


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


dataset = ["I hate this product", "I love this product","What are you saying? This product is awful","I can't believe I bought it, its a waste of money","not that bad","meh, it was okay","It is too expensive","its shit"]
print(main(dataset))



