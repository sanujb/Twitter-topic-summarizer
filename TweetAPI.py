import tweepy
import json
import operator
from operator import itemgetter
from datetime import datetime
import re

def setAPI():
    # Consumer keys and access tokens, used for OAuth
    # consumer_key = 'U5y30mU7zvCBG3BdFp9zHxvNq'
    # consumer_secret = 'QLl2pICqZlj6mZsOduoTPa7RUKnK9WNdVnyvYHaX1T2xtxm93L'
    # access_token = '2469537072-2HDqiXpx1ROpxKE5j9IYIjC35ahAWguyz8zrLxj'
    # access_token_secret = 'WPOcb35aZhVCbOELat29kJ8R7XWZMj8m4sWoZjQ9pYIyL'
    consumer_key = 'aTtoeJlEi4ygfz7t26UkoZODq'
    consumer_secret = 'TowY5L8JhcbyfGvofBBMLqla81uH2rrcpCd3p3QfyNbWsGAkTF'
    access_token = '3699908722-sZofO5pzMiGZLHptghx1JThngwC65y9zyIWijMc'
    access_token_secret = 'DSuxRVWYwo02oXNylovlqmMIlw2jvG1hCifEYuvUuJYnW'

    # OAuth process, using the keys and tokens
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

    # auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True), auth

def get_trending_topics(loc):
    woeid = api.trends_closest(lat=loc[0], long=loc[1])[0]['woeid']
    trends = api.trends_place(woeid)[0]['trends']
    # with open('newtrends.txt') as infile:
    #     trends = json.load(infile)

    print(len(trends))
    trending_topics = {}
    for trend in trends:
        if trend['tweet_volume']:
            trend_name = trend['name'].strip('"').strip("'")
            trending_topics[trend_name] = (trend['tweet_volume'], trend['query'])

    print(trending_topics)
    return trending_topics
    # sorted_tt = sorted(trending_topics.items(), key=operator.itemgetter(1),reverse = True)
    #
    # final_topics = []
    # j=0
    # for key,value in sorted_tt:
    #     final_topics.append(str(key))
    #     print key
    #     j+=1
    #     if j==num_topics:
    #         break
    #
    # return final_topics

def getMaxID(tweets):
    id = float('inf')
    for t in tweets:
        if t['id'] < id:
            id = t['id']

    print(id, tweets[-1]['id'])
    return id

def getTweets(query, loc, total_count):
    # todo fix max ID, total_count.
    count_per_call = 5
    public_tweets = api.search(q=query, lang='en', result_type='recent', count=count_per_call,
                               geocode=str(loc[0])+','+str(loc[1])+','+'50mi') #1-recent
    public_tweets = [x._json for x in public_tweets]

    #queries and write to file
    for i in range(number_of_calls):
        next_tweets = api.search(q=query, lang='en', result_type='recent', count=count_per_call,
                                   geocode=str(loc[0]) + ',' + str(loc[1]) + ',' + '50mi', max_id=getMaxID(public_tweets))  # 2-recent
        public_tweets.extend([x._json for x in next_tweets])

    popular_tweets = api.search(q=query, lang='en', result_type='popular', count=count_per_call,
                               geocode=str(loc[0])+','+str(loc[1])+','+'50mi') #3-popular

    public_tweets.extend([x._json for x in popular_tweets])

    return public_tweets

def preprocess(public_tweets):
    #Start Preprocessing
    max_tweets_by_user = 5  #Above this value, user tweets removed
    minReputationRatio = 0.01
    minUserAge = 2  #In days
    maxHashTags = 3
    maxURLs = 2
    spam_tweets = []
    user_dict = {}
    #1. Check for spam-bot like users
    currentTime = datetime.now()
    spam_stats = {'hashtags':0,'url':0,'hash+url':0}
    for i in range(len(public_tweets)):
        user_id = public_tweets[i]['user']['id']
        if user_id in user_dict:
            k = user_dict[user_id]
            k.append(i)
            user_dict[user_id] = k
        else:
            verification = public_tweets[i]['user']['verified']
            reputation = public_tweets[i]['user']['followers_count']/float(public_tweets[i]['user']['followers_count'] + float(public_tweets[i]['user']['friends_count'])+0.00001)
            creationDate = public_tweets[i]['user']['created_at']
            creationDate = creationDate[0:-11] + creationDate[-5:]
            creationDate = datetime.strptime(creationDate,'%a %b %d %H:%M:%S %Y')
            user_dict[user_id] = [[verification,reputation,creationDate],i]

        #Also check tweets for too many #tags or urls
        hashtags = len(public_tweets[i]['entities']['hashtags'])
        URLs = len(public_tweets[i]['entities']['urls'])
        if hashtags > maxHashTags:
            spam_stats['hashtags']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue
        if URLs > maxURLs:
            spam_stats['url']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue
        if URLs == maxURLs and hashtags == maxHashTags-1:
            spam_stats['hash+url']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue

    a=0
    b=0
    c=0
    a1,b1,c1 = 0,0,0
    for k in user_dict:
        if len(user_dict[k]) - 1 > max_tweets_by_user:
            a1+=1
            for i in user_dict[k][1:]:
                a+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0
            continue
        if user_dict[k][0][1] < minReputationRatio:
            b1+=1
            for i in user_dict[k][1:]:
                b+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0
            continue
        if (currentTime - user_dict[k][0][2]).days < minUserAge:
            c1+=1
            for i in user_dict[k][1:]:
                c+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0

    spam_stats['Users_maxTweets'] = a1
    spam_stats['Users_lowRep'] = b1
    spam_stats['Users_minAge'] = c1

    spam_stats['Tweets_maxTweets'] = a
    spam_stats['Tweets_lowRep'] = b
    spam_stats['Tweets_minAge'] = c

    public_tweets = [x for x in public_tweets if x!=0]

    #2. Remove URLs
    for i in range(len(public_tweets)):
        urls = public_tweets[i]['entities']['urls']
        if len(urls) == 0:
            continue
        len_prev = 0    #length of previous URL
        for k in urls:
            k['indices'][0]-=len_prev
            k['indices'][1]-=len_prev
            len_prev+= k['indices'][1] - k['indices'][0]
            public_tweets[i]['text'] =  public_tweets[i]['text'][0:k['indices'][0]] + public_tweets[i]['text'][k['indices'][1]:]

    # for i in range(len(public_tweets)):
    #     url_index = public_tweets[i]['text'].find('http')
    #     if url_index != -1:
    #         public_tweets[i]['text'] = public_tweets[i]['text'][0:url_index-1]
    #
    # for k in public_tweets:
    #     new = str()
    #     for l in k['text']:
    #         if l!='\n':
    #             new+=l
    #     k['text'] = new

    #3. Remove @, RT @:
    for k in public_tweets:
        k['text'] = k['text'].replace('\n','').replace('http','').replace('...',' ').replace(u'\u2026', '')
        while '@' in k['text']:
            pos_start = k['text'].find('@')
            pos_end = pos_start+1
            while True:
                if pos_end == len(k['text']):
                    break
                elif k['text'][pos_end] != ' ':
                    pos_end+=1
                else:
                    break
            k['text'] = k['text'][0:pos_start] + k['text'][pos_end+1:]

        myre = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u26FF\u2700-\u27BF])+',
            re.UNICODE)
        k['text'] = myre.sub(r'', k['text']) # no emoji

        # while u'\u2026' in k['text']:
        #     pos_start = k['text'].find(u'\u2026')
        #     k['text'] = k['text'][0:pos_start] + k['text'][pos_start+1:]

        # while '...' in k['text']:
        #     pos_start = k['text'].find('...')
        #     k['text'] = k['text'][0:pos_start] +' '+ k['text'][pos_start+3:]

        if k['text'][0:3] == 'RT ' or k['text'][0:3] == 'rt ':
            k['text'] = k['text'][3:]

        k['text'] = k['text'].rstrip().lstrip()

    #3. Check for Duplicate Tweets
    # public_tweets = sorted(public_tweets, key=lambda k: k['text'])  #sorting the list of dictionaries by the tweet text
    spam_stats['duplicate'] = 0
    # i=0
    # while True:
    #     if i == len(public_tweets) - 1:
    #         break
    #     tweet = public_tweets[i]['text']
    #     if tweet == public_tweets[i+1]['text']:
    #         spam_stats['duplicate']+=1
    #         public_tweets[i+1]['text'] = ''
    #         for j in range(i+2,len(public_tweets)):
    #             if public_tweets[j]['text'] == tweet:
    #                 spam_stats['duplicate']+=1
    #                 public_tweets[j]['text'] = ''
    #             else:
    #                 break
    #         i=j-1
    #     i+=1

    dup_set = set()
    for t in public_tweets:
        if t['text'] in dup_set:
            spam_stats['duplicate']+=1
            t['text'] = ''
            continue
        dup_set.add(t['text'])

    public_tweets = [x for x in public_tweets if x['text'] != '']
    # print ('printing spam tweets')
    # for k in spam_tweets:
    #     print (k['text'])

    with open('./Data/fetchedTweets.txt', 'w+') as text_file:
        for k in public_tweets:
            text_file.write(str((currentTime - user_dict[k['user']['id']][0][2]).days) +'\t'+ str(user_dict[k['user']['id']][0][1]) +'\t'+ str(k['user']['statuses_count']) +'\t'+ str(k['retweet_count']) +'\t'+ k['text'].encode('utf-8') + '\n') #[age,reputation,statuses_count,retweet_count,text]

    return public_tweets,spam_stats,spam_tweets

api, auth = setAPI()
number_of_calls = 5