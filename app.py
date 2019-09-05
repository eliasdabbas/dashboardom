from collections import Counter

from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

import pandas as pd
dashboard_df = pd.read_csv('data/dashboards_df.csv', keep_default_na=False)
tag_counts = Counter(dashboard_df['tags'].str.cat(sep=', ').split(', '))


class ContactForm(FlaskForm):
    name = StringField('Name*', validators=[DataRequired()])
    email = StringField('Email*', validators=[DataRequired(), Email()])
    message = TextAreaField('Message*', validators=[DataRequired()])
    submit = SubmitField('Submit')


def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    return app


app = create_app()
app.config['SECRET_KEY'] = 'my secret key'


@app.route('/')
def home():
    return render_template('home.html', dashboard_df=dashboard_df,
                           tag_counts=sorted(tag_counts.items(),
                                             key=lambda x: x[1],
                                             reverse=True))


@app.route('/<dash_name>')
def name(dash_name):
    dash_df = dashboard_df[dashboard_df['dashboard'] == dash_name]
    try:
        return render_template(template_name_or_list='dashboard.html',
                               dash_name=dash_name,
                               **dash_df.to_dict('rows')[0],
                               dashboards=dashboard_df['dashboard'],
                               dashboard_df=dashboard_df)
    except Exception:
        return render_template('404.html', dashboard_df=dashboard_df)


@app.route('/tag/<tag>')
def tag(tag):
    return render_template('tags.html', tag=tag, dashboard_df=dashboard_df)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        return redirect(url_for('contact_thankyou'))
    return render_template('contact.html', form=form,
                           dashboard_df=dashboard_df)


@app.route('/contact_thankyou')
def contact_thankyou():
    return render_template('contact_thankyou.html',
                           dashboard_df=dashboard_df)


@app.route('/googlebe42ea5ea9569ea7.html')
def google_verification():
    return 'google-site-verification: googlebe42ea5ea9569ea7.html'
