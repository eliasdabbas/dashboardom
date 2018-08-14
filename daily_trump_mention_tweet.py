import datetime
import os
import matplotlib
matplotlib.use('Agg')
from matplotlib.ticker import EngFormatter
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import advertools as adv
from twython import Twython
import pandas as pd

now = datetime.datetime.now()

APP_KEY = os.environ['APP_KEY'] 
APP_SECRET = os.environ['APP_SECRET']

OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

trump_replies = []

for i in range(10):
    temp = twitter.search(q='to:realdonaldtrump -filter:retweets',
                          lang='en',
                          result_type='recent',
                          count=100,
                          trim_user=False,
                          include_entities=True,
                          max_id=None if i == 0 else [x['id'] for x in trump_replies[-1]['statuses']][-1] - 1,
                          tweet_mode='extended')
    trump_replies.append(temp)

tweet_text_replies = []
user_name_replies = []
user_screen_name_replies = []
user_followers_count_replies = []
hashtags_replies = []
mentions_replies = []

for response in trump_replies:
    for tweet in response['statuses']:
        tweet_text_replies.append(tweet['full_text'])
        user_name_replies.append(tweet['user']['name'])
        user_screen_name_replies.append(tweet['user']['screen_name'])
        user_followers_count_replies.append(tweet['user']['followers_count'])
        hashtag_list_replies = [x['text'] for x in tweet['entities']['hashtags']]
        hashtags_replies.append(hashtag_list_replies)
        mention_list_replies = [x['screen_name'] for x in tweet['entities']['user_mentions']]
        mentions_replies.append(mention_list_replies)


df_replies = pd.DataFrame({
    'tweet_text': tweet_text_replies,
    'user_name': user_name_replies,
    'user_screen_name': user_screen_name_replies,
    'user_followers_count': user_followers_count_replies,
    'hashtags': hashtags_replies,
    'mentions': mentions_replies
})

word_freq_responses = adv.word_frequency(df_replies['tweet_text'], 
                   df_replies['user_followers_count'],
                   rm_words=adv.stopwords['english'] + ['@realdonaldtrump', "it’s", '&'])
word_freq_hashtags = adv.word_frequency([' '.join(x) for x in df_replies['hashtags']], 
                   df_replies['user_followers_count'])
word_freq_mentions = adv.word_frequency([' '.join(x) for x in df_replies['mentions']], 
                   df_replies['user_followers_count'])
word_freq_mentions = word_freq_mentions[word_freq_mentions['word'] != 'realdonaldtrump'].reset_index(drop=True)

df_list = [
    word_freq_responses,
    word_freq_hashtags,
    word_freq_mentions,
]

titles = [
    'Word',
    'Hashtag',
    'Mention'
]

figure_titles = [
    'Words',
    '#Hashtags',
    '@Mentions'
]

prefixes = [
    '',
    '#',
    '@'
]
for i in range(3):
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches((12, 14), forward=True)
    fig.set_facecolor('#f0f0f0')

    fig.text(0.5, 0.955, ha='center', fontsize=21,
             s=figure_titles[i] + ' Used in Replies to @realDonaldTrump\n' + 
             datetime.datetime.strftime(now, '%A %d %b %Y - %H:%M:%S UTC (') + str(len(df_replies)) + ' tweets)\n\n')
    for j in range(2):
        ax[j].set_frame_on(False)
        ax[j].grid(alpha=0.2)
        ax[j].xaxis.set_major_formatter(EngFormatter())
        ax[j].yaxis.set_tick_params(labelsize=16)
        ax[j].xaxis.set_tick_params(labelsize=16)
        if j == 0:
            ax[j].set_title(titles[i] + ' Reach\n(times used x total followers of tweeters)',
                            pad=-25, fontsize=18)

            ax[j].barh(y=prefixes[i] + df_list[i]['word'][:20][::-1], 
                       width=df_list[i]['wtd_freq'][:20][::-1], 
                       color='#002663', alpha=0.8)
            for x in range(20):
                ax[j].text(df_list[i]['wtd_freq'][:20][::-1][x],
                           prefixes[i] + df_list[i]['word'][:20][::-1][x],
                           s=f"{df_list[i]['wtd_freq'][:20][::-1][x]:,}",
                           va='center', 
                           fontsize=16)

        if j == 1:
            ax[j].set_title(titles[i] + ' Count\n(number of times used)',
                            pad=-25, fontsize=18)
            ax[j].barh(y=prefixes[i] + df_list[i].sort_values(['abs_freq'], ascending=False).reset_index()['word'][:20][::-1], 
                       width=df_list[i].sort_values(['abs_freq'], ascending=False).reset_index()['abs_freq'][:20][::-1],
                       color='#002663', alpha=0.8)
            for x in range(20):
                ax[j].text(df_list[i].sort_values(['abs_freq'], ascending=False).reset_index()['abs_freq'][:20][::-1][x],
                           prefixes[i] + df_list[i].sort_values(['abs_freq'], ascending=False).reset_index()['word'][:20][::-1][x],
                           s=f"{df_list[i].sort_values(['abs_freq'], ascending=False).reset_index()['abs_freq'][:20][::-1][x]:,}",
                           va='center', fontsize=16)

    plt.tight_layout()
    fig.savefig(fname=figure_titles[i] + ' ' + datetime.datetime.strftime(now, '%A %d %b %Y - %H:%M:%S UTC') + '.png', 
                dpi=150, bbox_inches='tight',
                facecolor='#f0f0f0', )

tweet_header = ('How did people respond to @realDonaldTrump tweets today?\n' + 
                datetime.datetime.strftime(now, '%A %d %b %Y %H:%M:%S UTC'))
remaining_len = 280 - len(tweet_header)
top_hashtags =  '\n'.join('#' + word_freq_hashtags['word'].head(6)) 
top_tweeters = ' '.join('@' + df_replies['user_screen_name'].value_counts().to_frame().reset_index()['index'].head(6))
final_tweet = tweet_header + '\nTop hashtags:\n' + top_hashtags +'\nMost active accounts:\n' + top_tweeters

if len(final_tweet) > 280:
    last_space = max(final_tweet[:280].rfind(' '), final_tweet[:280].rfind('\n'))
    final_tweet = final_tweet[:last_space]

home_timeline = twitter.get_home_timeline(tweet_mode='extended', count=200)
latest_trump_tweet_id = [x for x in home_timeline if '@realDonaldTrump tweets today' in x['full_text']][0]['id']

img_words = twitter.upload_media(media=open(figure_titles[0] + ' ' + datetime.datetime.strftime(now, '%A %d %b %Y - %H:%M:%S UTC') + '.png', 'rb'))
img_hashtags = twitter.upload_media(media=open(figure_titles[1] + ' ' + datetime.datetime.strftime(now, '%A %d %b %Y - %H:%M:%S UTC') + '.png', 'rb'))
img_mentions = twitter.upload_media(media=open(figure_titles[2] + ' ' + datetime.datetime.strftime(now, '%A %d %b %Y - %H:%M:%S UTC') + '.png', 'rb'))

twitter.update_status(status=final_tweet,
#     in_reply_to_status_id=latest_trump_tweet_id,
    media_ids=[x['media_id'] for x in [img_words, img_hashtags, img_mentions]])