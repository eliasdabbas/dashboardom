import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter, PercentFormatter
import requests
import pandas as pd
from twython import Twython

APP_KEY = os.environ['APP_KEY'] 
APP_SECRET = os.environ['APP_SECRET']

OAUTH_TOKEN = os.environ['OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['OAUTH_TOKEN_SECRET']

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

home_timeline = twitter.get_home_timeline(tweet_mode='extended')
latest_crypto_tweet_id = [x for x in home_timeline if '#CryptoCurrency prices' in x['full_text']][0]['id']

resp = requests.get('https://api.coinmarketcap.com/v2/ticker/?limit=20')
global_crypto = requests.get('https://api.coinmarketcap.com/v2/global/')
total_market_cap = global_crypto.json()['data']['quotes']['USD']['total_market_cap']

timestamp = resp.json()['metadata']['timestamp']
timestamp = pd.to_datetime(resp.json()['metadata']['timestamp'], unit='s')

df_raw = pd.DataFrame.from_dict(resp.json()['data'], orient='index').reset_index(drop=True)
quotes = pd.DataFrame.from_records([x['USD'] for x in df_raw['quotes']]) 
df = pd.concat([df_raw, quotes], axis=1)
df['pct_of_tot_mkt_cap'] = df['market_cap'] / total_market_cap

titles = [
    '\n'.join([
        'Crypto Currencies Market Cap US$',
        'Total Market Cap : ' + 
        f"${global_crypto.json()['data']['quotes']['USD']['total_market_cap']:,.0f}",
        'Total Trading Volume 24h: ' + f"${global_crypto.json()['data']['quotes']['USD']['total_volume_24h']:,.0f}",
        datetime.datetime.strftime(timestamp, format='%a. %b. %d, %Y')
    ]),
    '\n'.join([
        'Crypto Currency Prices US$ (Change in 24h)',
        datetime.datetime.strftime(timestamp, format='%a. %b. %d, %Y')
    ]),
    '\n'.join([
        'Crypto Currency % of Total Crypto Market',
        datetime.datetime.strftime(timestamp, format='%a. %b. %d, %Y')
    ])
]

widths = [
    'market_cap',
    'price',
    'pct_of_tot_mkt_cap'
]

for i in range(3):
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 10)
    fig.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')
    ax.set_frame_on(False)
    ax.grid(alpha=0.3)
    ax.barh(y=df.sort_values(['market_cap'])['name'],
            width=df.sort_values(['market_cap'])[widths[i]],
            color='steelblue',
            alpha=1)
    ax.set_title(titles[i], size=18)
    ax.xaxis.set_major_formatter(EngFormatter() if i != 2 else PercentFormatter(xmax=1))
    ax.set_xlabel('Market Cap US$' if i == 0 else '', size=13)
    ax.xaxis.set_tick_params(labelsize=13)
    ax.yaxis.set_tick_params(labelsize=13)
    if i == 0:
        for j, num in enumerate(df.sort_values(['market_cap'])['market_cap']):
            ax.text(num, j, f"${num:,.0f}", ha='left', va='center', size=13)
    elif i == 1:
        for j, (price, pct) in enumerate(zip(df.sort_values(['market_cap'])['price'], df.sort_values(['market_cap'])['percent_change_24h'])):
            ax.text(price, j, f"${price:,.3f}" + ' (' + f"{pct:,.1f}" + '%)', 
                    ha='left', va='center', size=13,
                    color='green' if pct > 0 else 'red')
    elif i == 2:
        for j, pct in enumerate(df.sort_values(['market_cap'])['pct_of_tot_mkt_cap']):
            ax.text(pct, j, f"{pct:.1%}",
                    ha='left', va='center', size=13)

    ax.annotate(s='Data: coinmarketcap.com', xy=(10, 15),
                xycoords='figure pixels', fontsize=12, alpha=0.8)
    fig.tight_layout()
    fig.subplots_adjust(right=0.8)
    fig.savefig(fname=widths[i] + '.png', dpi=150, facecolor='#fafafa')
    plt.close()

tweet_header = '#CryptoCurrency prices for ' + datetime.datetime.strftime(timestamp, format='%a. %b. %d, %Y')

tweet_details = ('#' + df['name'].str.replace(' ', '') + 
                 ' ' + '$' + df['symbol'] + ': $' + 
                 df['price'].round(2).astype(str)).str.cat(sep='\n')
remaining_len = 280 - len(tweet_header)
details_upto = tweet_details[:remaining_len].rfind('\n')

home_timeline = twitter.get_home_timeline(tweet_mode='extended')
latest_crypto_tweet_id = [x for x in home_timeline if '#CryptoCurrency prices' in x['full_text']][0]['id']

img_market_cap = twitter.upload_media(media=open('market_cap.png', 'rb'))
img_price = twitter.upload_media(media=open('price.png', 'rb'))
img_pct_of_tot_mkt_cap = twitter.upload_media(media=open('pct_of_tot_mkt_cap.png', 'rb'))

twitter.update_status(status='\n'.join([
    tweet_header, tweet_details[:details_upto]]),
    in_reply_to_status_id=latest_crypto_tweet_id,
    media_ids=[x['media_id'] for x in [img_price, img_market_cap, img_pct_of_tot_mkt_cap]])