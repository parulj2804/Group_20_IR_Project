'''
Library Description

'''
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
import pandas as pd
from .classifier_utils import Text_Classifier, Text_Classifier_Hindi
from collections import Counter
import numpy as np
from datetime import datetime
import pytz

UTC = pytz.utc
IST = pytz.timezone('Asia/Kolkata')

class Twitter_Utils:
  def __init__(self,):
    self.access_token = "1339636567497793542-GW2gQDvVy4pbmOBKLxoJgJiZhV17TU"
    self.access_token_secret = "DrIavL0cqg83Symq9dy40tL8A46DFMCmdxu5PPt7ZMIEq"
    self.api_key = "VMMTKHay4flWCjGDF7DwWAinX"
    self.api_secret = "I5R1dkFZXh8f3Kztw9KljdXfh1YwbUQ8YRBgi8AFqKXfME5Jr8"
    auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
    auth.set_access_token(self.access_token, self.access_token_secret)
    self.api = tweepy.API(auth)

  def get_user_tweets(self,user_id,tweet_count=50):
    '''
        Method Description
    '''
    tweets=None
    user_id=user_id.replace('"','')
    user_id=user_id.replace("''","")
    try:
        tweets = self.api.user_timeline(screen_name=user_id, count=tweet_count,include_rts = False,tweet_mode = 'extended')
    except Exception as e:
	#        with open('hate_burst.log','a') as f:
	#           curr_time=str(datetime.now(IST))
	#          msg="[Utils] [Twitter User Analytics]"+" Exception:"+str(e)
	#         f.write(curr_time+msg+'\n')
        return "invalid username"
    text_classifier = Text_Classifier()
    text_classifier_hindi = Text_Classifier_Hindi()

    processed_tweets = []
    for tweet in tweets:
      tweet_info=[]
      tweet_info.append(tweet.user.name)
      tweet_info.append(tweet.user.screen_name)
      tweet_info.append(tweet.full_text)
      tweet_info.append(tweet.created_at)
      try:
          tweet_info.append(tweet.entities['media'][0]['media_url_https'])
      except:
          print("Media Attribute Not Found in Tweet")
          tweet_info.append(0)
      tweet_info.append(tweet.user.location)
      tweet_info.append(tweet.lang)
      tweet_info.append(tweet.favorite_count)
      tweet_info.append('https://twitter.com/twitter/statuses/'+str(tweet._json['id']))

      hashtags=[]
      if len(tweet.entities['hashtags'])>0:
          for i in range(len(tweet.entities['hashtags'])):
              hashtags.append(tweet.entities['hashtags'][i]['text'])
      tweet_info.append(' '.join(hashtags))

      prediction=None
      if tweet.lang=='hi': #Hindi
          prediction = text_classifier_hindi.predict(tweet.full_text)
      else: # Default use English Model
          prediction = text_classifier.predict(tweet.full_text)
      tweet_info.append(prediction)

      processed_tweets.append(tweet_info)
    processed_tweets_df = pd.DataFrame(processed_tweets, columns=['name','username','tweet_text','created_at','media_url','location','language','likes','url','hashtags','sentiment'])
    data = self.get_stats(processed_tweets_df)
    data['dataframe']=processed_tweets_df
    return data


  def get_stats(self,processed_tweets_df):
    stats = {}
    counts_categories = dict(Counter(processed_tweets_df['sentiment']))
    counts_pos=0
    try:
        counts_pos = counts_categories['No Hate']
    except:
        print("No Hate")
        counts_pos = 0
    counts_neg=0
    try:
        counts_neg = counts_categories['Hate And Abusive']
    except:
        print("No Non-Hate")
        counts_neg = 0

    tweet_count = processed_tweets_df.shape[0]
    stats['counts_pos']=counts_pos
    stats['counts_neg']=counts_neg
    stats['tweet_count']=tweet_count
    processed_tweets_df_hate = processed_tweets_df[processed_tweets_df['sentiment']=="Hate And Abusive"]
    average_likes_hate = np.mean(processed_tweets_df_hate['likes'])
    processed_tweets_df_no_hate = processed_tweets_df[processed_tweets_df['sentiment']=='No Hate']
    average_likes_no_hate = np.mean(processed_tweets_df_no_hate['likes'])
    stats['average_likes_hate']=average_likes_hate
    stats['average_likes_no_hate']=average_likes_no_hate
    hashtags = ' '.join(processed_tweets_df_hate['hashtags'])
    hashtags_hate = hashtags.split(' ')
    stats['hashtags_hate']=[ x for x in hashtags_hate if x!='' and  x!=' ']
    most_common_words_hate = Counter(" ".join(processed_tweets_df_hate['tweet_text']).split()).most_common(100)
    text_classifier = Text_Classifier()
    try:
        most_common_words_hate.remove(text_classifier.stopwords)
    except:
        print("No Stop-Words in Most Common")
    stats['most_common_words_hate']=most_common_words_hate[:10]
    most_common_locations =  Counter(processed_tweets_df_hate['location']).most_common(3)
    stats['most_common_locations']=most_common_locations

    return stats

  def get_trending(self,):
    '''
        Returns list of trending topics in India
    '''
    woeid = 23424848 #woeid india
    trends = self.api.get_place_trends(woeid)
    trending = []
    for item in trends[0]['trends']:
      trending.append(item['name'])
    return trending

  def get_trending_tweets(self,hashtag,date,tweet_count=50):
    '''
        Method Description
    '''
    hashtag=hashtag.replace('"','')
    date=date.replace('"','')
    hashtag=hashtag.replace("'","")
    date=date.replace("'","")
    tweets = tweepy.Cursor(self.api.search_tweets,
                               hashtag,
                               since_id=date,
                               tweet_mode='extended').items(tweet_count)
    tweets = [tweet for tweet in tweets]

    text_classifier = Text_Classifier()
    text_classifier_hindi = Text_Classifier_Hindi()

    processed_tweets = []
    for tweet in tweets:
      tweet_info=[]
      tweet_info.append(tweet.user.name)
      tweet_info.append(tweet.user.screen_name)
      tweet_info.append(tweet.full_text)
      tweet_info.append(tweet.created_at)
      try:
          tweet_info.append(tweet.entities['media'][0]['media_url_https'])
      except:
          print("Media Attribute Not Found in Tweet")
          tweet_info.append(0)
      tweet_info.append(tweet.user.location)
      tweet_info.append(tweet.lang)
      tweet_info.append(tweet.favorite_count)
      tweet_info.append('https://twitter.com/twitter/statuses/'+str(tweet._json['id']))

      hashtags=[]
      if len(tweet.entities['hashtags'])>0:
          for i in range(len(tweet.entities['hashtags'])):
              hashtags.append(tweet.entities['hashtags'][i]['text'])
      tweet_info.append(' '.join(hashtags))

      prediction=None
      if tweet.lang=='hi': #Hindi
          prediction = text_classifier_hindi.predict(tweet.full_text)
      else: # Default use English Model
          prediction = text_classifier.predict(tweet.full_text)
      tweet_info.append(prediction)

      processed_tweets.append(tweet_info)
    processed_tweets_df = pd.DataFrame(processed_tweets, columns=['name','username','tweet_text','created_at','media_url','location','language','likes','url','hashtags','sentiment'])
    data = self.get_stats(processed_tweets_df)
    data['dataframe']=processed_tweets_df
    print(data['dataframe']['location'])
    print(data['dataframe']['hashtags'])
    print(data['dataframe']['tweet_text'])
    return data
