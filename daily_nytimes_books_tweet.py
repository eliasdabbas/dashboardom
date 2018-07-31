import datetime
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
from twython import Twython


APP_KEY = os.environ['APP_KEY'] 
APP_SECRET = os.environ['APP_SECRET']

OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

home_timeline = twitter.get_home_timeline(tweet_mode='extended')
latest_books_tweet_id = [x for x in home_timeline if '#NYTimes Bestselling' in x['full_text']][0]['id']


api_key = os.environ['NYTIMES_API_KEY'] 
base_url = 'https://api.nytimes.com/svc/books/v3/lists.json?api-key='
amzn_aff_id = 'tag=ed076-20'
nyt_logo_img = 'poweredby_nytimes_200a.png'

book_lists4tweets = [
    ('advice-how-to-and-miscellaneous', 'audio-fiction'),
    ('audio-nonfiction', 'business-books'),
    ('combined-print-and-e-book-fiction', 'combined-print-and-e-book-nonfiction'),
    ('hardcover-fiction', 'hardcover-nonfiction'),
    ('paperback-nonfiction', 'picture-books'),
    ('science', 'series-books'),
    ('young-adult-hardcover', 'young-adult-paperback')
]

list_name = book_lists4tweets[datetime.datetime.today().weekday()]
list_name = list_name[0] if datetime.datetime.now().hour % 2 else list_name[1]

resp = requests.get(base_url + api_key + '&list=' + list_name)
ranks = [x['rank'] for x in resp.json()['results']]
weeks_on_list = [x['weeks_on_list'] for x in resp.json()['results']]
titles = [x['book_details'][0]['title'] for x in resp.json()['results']] 
titles = [x.title() for x in titles]
authors = [x['book_details'][0]['author'] for x in resp.json()['results']] 

book_ids =  [re.findall('dp/(.*)\?', resp.json()['results'][x]['amazon_product_url'])[0] 
             for x in range(len(resp.json()['results']))]
book_urls = [f'https://amzn.com/dp/{x}/?tag=ed076-20' for x in book_ids]

df = pd.DataFrame({
    'title': titles,
    'author': authors,
    'rank': ranks,
    'weeks_on_list': weeks_on_list,
})

df['urls'] = book_urls


if not set(df['weeks_on_list']) == {0}:
    plt.subplot(1, 9, 2)
    plt.axis('off')
    plt.imshow(df.iloc[:, 3:4].values, aspect='auto', alpha=0.55, cmap='Greens')
    plt.yticks([])
    plt.xticks([])
    for j in range(len(df)):
        plt.text(0, j + 0.022, str(df.iloc[:, 3:4].values[j][0]), 
                 va='center', ha='center', fontsize=14)
    plt.text(0, -1, 'Weeks \non list', ha='center', fontsize=12)

plt.subplot(1, 9, 3)
for i in range(len(df)):    
    plt.text(0, i/len(df) + 0.03, f"{len(df)-i:>4}. "  + df['title'][len(df)-1-i] + ' - ' + df['author'][len(df)-1-i], 
             va='center', fontsize=14,
             bbox=dict(facecolor='#f5f5f5' if i%2 else 'none', 
                       edgecolor='none'))
    plt.axis('off')

plt.text(x=0.5, y=1.05, 
         s='\n'.join(['NY Times Bestselling Books - ' + resp.json()['results'][0]['bestsellers_date'],
                      resp.json()['results'][0]['list_name']]) , fontsize=20)
plt.tight_layout(pad=-2.2)
plt.figimage(mpimg.imread(nyt_logo_img))
plt.savefig(fname=resp.json()['results'][0]['list_name'] + resp.json()['results'][0]['bestsellers_date'], 
            dpi=180, bbox_inches="tight")
plt.close()

tweet_header = '\n'.join(['#NYTimes Bestselling #Books: ' + resp.json()['results'][0]['bestsellers_date'],
                      resp.json()['results'][0]['list_name']])
title_hashtags = '#' + df['title'].str.replace(' |,|:|-', '')
author_hashtags = '#' + df['author'].str.replace(' |,|:|-', '')
tweet_links = '\n'.join(['\n'.join([title, author,url] ) 
                         for title, author, url in zip(title_hashtags, author_hashtags, df['urls'])]) 
remaining_len = 280 - len(tweet_header)
tweet = tweet_header + '\n' + tweet_links[:tweet_links[:remaining_len].rfind('\n')]

chart_img_file = resp.json()['results'][0]['list_name'] + resp.json()['results'][0]['bestsellers_date']
media = twitter.upload_media(media=open(chart_img_file + '.png', 'rb'))
twitter.update_status(status=tweet, 
                      in_reply_to_status_id=latest_books_tweet_id,
                      media_ids=[media['media_id']])