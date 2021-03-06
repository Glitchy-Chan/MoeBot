import datetime
import json
import os
import random
import time

import praw
import requests
import tweepy
from discord import Embed
from discord import Webhook, RequestsWebhookAdapter

while not(time.sleep(7200)):
    # Getting them tokens
    with open("secrets.json", "r") as f:
        config = json.load(f)

    # Cache with all of the submission ids
    with open('cache.json', 'r') as f:
        cache = json.load(f)

    # Praw and Tweepy auth
    reddit = praw.Reddit(client_id=config["Moe-Reddit-Client"],
                         client_secret=config["Moe-Reddit-Secret"],
                         user_agent="Reddit Twitter Bot")
    auth = tweepy.OAuthHandler(config["Moe-Twitter-Consumer"], config["Moe-Twitter-Secret"])
    auth.set_access_token(key=config["Moe-Twitter-Key"], secret=config["Moe-Twitter-Key-Secret"])
    twitter = tweepy.API(auth)


    def get_post(fails=0):
        """Yoinks a random submission from r/Moescape to post on twitter"""
        print("Getting post from reddit")

        try:
            posts = [post for post in reddit.subreddit('Moescape').hot(limit=20)]
            random_post_number = random.randint(0, 19)
            random_post = posts[random_post_number]

            if fails >= 3:
                print("MoeBot has failed to get a post too many times, going to sleep!")
                return
            elif random_post.id in cache['post-ids']:
                fails = fails + 1
                print(f"already posted image {random_post.url}")
                get_post(fails)

            else:
                post_name = random_post.title
                post_comments = random_post.num_comments
                post_likes = random_post.score
                post_link = random_post.shortlink
                post_image = get_image(random_post.url)
                post_discord_image = random_post.url

                cache['post-ids'].append(f'{random_post.id}')
                with open('cache.json', 'w+') as c:
                    json.dump(cache, c, indent=4)
                tweet(post_name, post_comments, post_likes, post_link, post_image, post_discord_image)

        except Exception as error:
            print(f"[EROR] MoeBot has run into an error: [{error}]")
            log = open('logs.txt', 'a')
            log.write(f'[{datetime.datetime.utcnow()}] [{type(error)}] \n'
                      f'END OF ERROR \n')
            log.close()
            return


    def get_image(url):
        file_name = os.path.basename(url[-18:])
        img_path = f"./pics/{file_name}"
        print(f"MoeBot is Downloading image: {url}")
        resp = requests.get(url, stream=True)

        try:
            with open(img_path, 'wb') as image:
                for chunk in resp:
                    image.write(chunk)
            return img_path

        except Exception as error:
            print(f"[EROR] MoeBot has run into an error: [{error}]")
            log = open('logs.txt', 'a')
            log.write(f"[{datetime.datetime.utcnow()}] [{type(error)}] \n"
                      f"END OF ERROR \n")
            log.close()
            return


    def tweet(post_name, post_comments, post_likes, post_link, post_image, post_discord_image):
        """Simply tweets out the submission"""

        try:
            print(f"MoeBot tweeting out post: {post_link} \n"
                  f"with image {post_image}")
            twitter.update_with_media(post_image, f"{post_name} \n"
                                                  f"💬 {post_comments} | ❤ {post_likes} \n \n"
                                                  f"🔗 {post_link}")

            print("MoeBot posting to discord")
            webhook = Webhook.partial(config["Moe-Discord-ID"],
                                      config["Moe-Discord-Token"],
                                      adapter=RequestsWebhookAdapter())
            emb = Embed(color=0xbc25cf, description=f"**[{post_name}]({post_link})**")
            emb.set_image(url=post_discord_image)
            emb.set_footer(text=f"💬{post_comments} | ❤ {post_likes}")

            webhook.send(embed=emb)

        except Exception as error:
            print(f"[EROR] MoeBot has run into an error: [{error}]")
            log = open('logs.txt', 'a')
            log.write(f"[{datetime.datetime.utcnow()}] [{type(error)}] \n"
                      f"END OF ERROR \n")
            log.close()

        time.sleep(6)
        print(f"MoeBot is removing file {post_image}")
        try:
            os.remove(post_image)
            print(f"MoeBot removed file {post_image}")

        except FileNotFoundError:
            print(f"MoeBot ran into an error removing {post_image}")
            log = open('logs.txt', 'a')
            log.write(f"[{datetime.datetime.utcnow()}] [File Not Found] \n"
                      f"END OF ERROR \n")
            log.close()


    if __name__ == "__main__":
        get_post()
