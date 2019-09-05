from collections import Counter

from flask import Flask, render_template
from flask_bootstrap import Bootstrap

import pandas as pd
dashboard_df = pd.read_csv('data/dashboards_df.csv', keep_default_na=False)
tag_counts = Counter(dashboard_df['tags'].str.cat(sep=', ').split(', '))


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()


@app.route('/')
def home():
    return render_template('home.html', dashboard_df=dashboard_df,
                           tag_counts=sorted(tag_counts.items(),
                                             key=lambda x: x[1],
                                             reverse=True))


@app.route('/<dash_name>')
def name(dash_name):
    dash_df = dashboard_df[dashboard_df['dashboard']==dash_name]
    try:
        return render_template(template_name_or_list='dashboard.html',
                               dash_name=dash_name, **dash_df.to_dict('rows')[0],
                               dashboards=dashboard_df['dashboard'],
                               dashboard_df=dashboard_df)
    except Exception:
        return render_template('404.html', dashboard_df=dashboard_df)


@app.route('/tag/<tag>')
def tag(tag):
    return render_template('tags.html', tag=tag, dashboard_df=dashboard_df)


@app.route('/googlebe42ea5ea9569ea7.html')
def google_verification():
    return 'google-site-verification: googlebe42ea5ea9569ea7.html'
