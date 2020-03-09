import tweepy
import django
import os
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loginpage.settings')
django.setup()
from login.models import Product



auth = tweepy.OAuthHandler('71tAYJhN9kcj0i000U3hC0HK1', '6AmFWjObvcObMxxpHDU3UdP5P92C6rsOrJHl8ukus1dXFKxLHH')
auth.set_access_token('1222617206212775941-SgcYFFhzzeDa9n3jPuqVlr8qHWpDos', 'CKU8XRwt3AyrTawQEj7Do7bkJBzZCbXHqx4J4KsjOxZ3U')

api = tweepy.API(auth)

text = "#swimmingschedule"
schedule = "Monday 6pm"
name = "@zhuoyu89764257 "
tweet = name + schedule

product = Product.objects.all()

user = api.me()
public_tweets = api.home_timeline()
mentions = api.mentions_timeline()



number = mentions[0].text

def check_tweet(t):
    if text in t:
        return True
    else:
        return False


def func():
    while(True):
        p = product.filter(name='cat')
        if p.count() > 0:
            print('cat found!')
            break
        else:
            print('cat doesnt exist')
            time.sleep(3)

id = mentions[0].user.screen_name

print(id)

""" print(product) """
""" for tweet in public_tweets:
    print(tweet.text)
    print(user.name) """

""" api.update_status(tweet)
print(tweet) """