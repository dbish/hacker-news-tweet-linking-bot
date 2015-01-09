from twython import Twython
import requests
import config
import time

class Info:
    def __init__(self, url, id):
        self.url = url
        self.id = id


def getTopStories():
    topStories = []
    resp = requests.get('https://hacker-news.firebaseio.com/v0/topstories.json')
    storyIds = resp.json()
    for storyId in storyIds:
        requestUrl = 'https://hacker-news.firebaseio.com/v0/item/'+str(storyId)+'.json'
        storyInfo = requests.get(requestUrl)
        storyUrl = storyInfo.json()['url']
        topStories.append(Info(storyUrl, storyId))

    return topStories
            
def getHNLink(url, topStories):
    forumUrl = None
    for story in topStories:
        if story.url == url:
            forumUrl = 'https://news.ycombinator.com/item?id='+str(story.id)

    return forumUrl

def getNewTweets():
    tweets = []

    try:
        with open("read_id.txt") as f:
            read_id = int(f.read())
           
    except IOError:
        read_id = 1

    twitter = Twython(config.APP_KEY, config.APP_SECRET, config.OAUTH_TOKEN, config.OATH_TOKEN_SECRET)
    user_timeline = twitter.get_user_timeline(screen_name="newsycombinator", since_id=read_id)
    if user_timeline:
        read_id = user_timeline[0]['id']

        for tweet in user_timeline:
            tweets.append(Info(tweet['entities']['urls'][-1]['expanded_url'], tweet['id']))

        with open("read_id.txt", "w") as f:
            f.write(str(read_id))
    
    return tweets


def postReply(id, message):
    message = ".@newsycombinator Forum link: "+ message
    twitter = Twython(config.APP_KEY, config.APP_SECRET, config.OAUTH_TOKEN, config.OATH_TOKEN_SECRET)
    twitter.update_status(status=message, in_reply_to_status_id=id)
    print(id)
    

def main():
    #get new tweets
    tweets = getNewTweets()


    #if there are new tweets, get top stories currently on HN
    if len(tweets) > 0:
        stories = getTopStories()
     
        #for each tweet, find the corresponding top story on HN
        for tweet in tweets:
            link = (getHNLink(tweet.url, stories))

            #if a link was found in the HN top stories, respond to each new tweet with the forum link
            if link != None:
                postReply(tweet.id, link)
    
            
        
if __name__== "__main__":
    main()