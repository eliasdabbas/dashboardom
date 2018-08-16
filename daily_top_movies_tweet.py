import datetime
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import EngFormatter
import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from twython import Twython

APP_KEY = os.environ['APP_KEY'] 
APP_SECRET = os.environ['APP_SECRET']
OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

yesterday = datetime.datetime.today() - datetime.timedelta(2)
yesterday_fmt = datetime.datetime.strftime(yesterday, '%Y-%m-%d')

resp = requests.get('http://www.boxofficemojo.com/daily/chart/?view=1day&sortdate=' + yesterday_fmt)
soup = BeautifulSoup(resp.text, 'lxml')

table_data = [x.text for x in soup.select('center td')][14:234]

table_headers = ['td', 'ytd', 'title', 'studio', 'daily_gross_str', 'pct_chg_yd', 'lw', 'theaters', 
                 'avg', 'gross_to_date_str', 'day']
df = pd.DataFrame(np.array(table_data).reshape((20, 11)), columns=table_headers)

df['daily_gross'] = df['daily_gross_str'].str.replace(',|\$', '').astype(int)
df['gross_to_date'] = df['gross_to_date_str'].str.replace(',|\$', '').astype(int)
df2 = df.sort_values('gross_to_date', ascending=False).reset_index(drop=True)


x_vals = [df['daily_gross'], df2['gross_to_date']]
x_labels = ['\nDaily Boxoffice (US$)', '\nBoxoffice Gross To-Date (US$)']
subtitles = ['\nDaily Gross US$', '\nGross To-Date US$']
dfs = [df, df2]

for i in range(2):
    fig, ax = plt.subplots()
    fig.set_size_inches([7, 18])
    fig.set_facecolor('#eeeeee')
    ax.set_facecolor('#eeeeee')
    ax.set_frame_on(False)
    sns.barplot(x=x_vals[i],
                y=dfs[i]['title'],
                palette='tab20',
                dodge=False,                 
                hue=dfs[i]['studio'],
                ax=ax)
    ax.xaxis.set_major_formatter(EngFormatter())
    ax.yaxis.set_tick_params(labelsize=20)
    ax.xaxis.set_tick_params(labelsize=20)
    for j in range(20):
        ax.text(x=x_vals[i][::-1][j], 
                y=j, 
                s=f"${x_vals[i][::-1][j]:,}",
                fontsize=16,
                va='center')
    legend = ax.legend(loc=[1.05, 0.3], fontsize=20,
                       frameon=False, title='Studio')
    legend.set_title('Studio\n', {'size': 22})
    ax.grid(alpha=0.3)
    ax.set_xlabel(x_labels[i], fontsize=20)
    ax.set_ylabel('')
    ax.set_title('\nBoxoffice Mojo Top Movies - ' + soup.select('center > font b')[0].text + subtitles[i], 
             fontsize=25)
    fig.savefig(fname='daily.png' if i == 0 else 'gross_todate.png' , dpi=200,
                facecolor='#eeeeee', bbox_inches="tight")

daily_img = twitter.upload_media(media=open('daily.png', 'rb'))
todate_img = twitter.upload_media(media=open('gross_todate.png', 'rb'))

top_movies_text = 'Top #movies ' + datetime.datetime.strftime(yesterday, '%b %d\n') 
url = 'http://www.boxofficemojo.com/daily/chart/?view=1day&sortdate=' + yesterday_fmt
hashtags = ' '.join('#' + df['title'].str.replace(' |:|-|\'|!|\.|\?', ''))

hashtags_clean = hashtags[:hashtags[:188].rfind(' ')] 
tweet = top_movies_text  + url + '\n' + hashtags_clean

twitter.update_status(status=tweet, 
                      media_ids=[x['media_id'] for x in [daily_img, todate_img]])
