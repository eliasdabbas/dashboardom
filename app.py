import os

from collections import Counter
from datetime import datetime
from threading import Thread

from flask import Flask, render_template, session, redirect, url_for, abort
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email

import pandas as pd
dashboard_df = pd.read_csv('data/dashboards_df.csv', keep_default_na=False)
tag_counts = Counter(dashboard_df['tags'].str.cat(sep=', ').split(', '))
basedir = os.path.abspath(os.path.dirname(__file__))


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

app.config['DASHBOARDOM_MAIL_SUBJECT_PREFIX'] = '[Dashboardom]'
app.config['DASHBOARDOM_MAIL_SENDER'] = 'Dashboardom Admin <dashboardommail@gmail.com>'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        suffix = '...' if len(self.message) > 50 else ''
        return f'<Email {str(self.date)[:10]}: "{self.message[:50]+suffix}">'


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String)
    name = db.Column(db.String)
    emails = db.relationship(Email, backref='user')

    def __repr__(self):
        return f"<User {self.email_address}>"


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(subject,
                  sender=app.config['DASHBOARDOM_MAIL_SENDER'],
                  recipients=[to])
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


# @app.before_request
# def redirect_nonwww():
#     """Redirect non-www requests to www."""
#     urlparts = urlparse(request.url)
#     if 'www' not in urlparts.netloc:
#         urlparts_list = list(urlparts)
#         print(urlparts_list)
#         urlparts_list[1] = 'www.dashboardom.com'
#         return redirect(urlunparse(urlparts_list), code=301)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User,  Email=Email)


@app.route('/')
def home():
    return render_template('home.html', dashboard_df=dashboard_df,
                           tag_counts=sorted(tag_counts.items(),
                                             key=lambda x: x[1],
                                             reverse=True))


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', dashboard_df=dashboard_df)


@app.route('/<dash_name>')
def name(dash_name):
    dash_df = dashboard_df[dashboard_df['dashboard'] == dash_name]
    if dash_df.empty:
        abort(404)
    return render_template(template_name_or_list='dashboard.html',
                           dash_name=dash_name,
                           **dash_df.to_dict('rows')[0],
                           dashboards=dashboard_df['dashboard'],
                           dashboard_df=dashboard_df)


@app.route('/tag/<tag>')
def tag(tag):
    if not bool(dashboard_df['tags'].str.contains(tag).any()):
        abort(404)
    return render_template('tags.html', tag=tag, dashboard_df=dashboard_df)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        send_email('eliasdabbas@gmail.com',
                   'Dashboardom inquiry',
                   'contact_email',
                   name=form.name.data,
                   from_email=form.email.data,
                   msg=form.message.data)
        user = User.query.filter_by(email_address=form.email.data).first()
        if user is None:
            user = User(name=form.name.data,
                        email_address=form.email.data)
            db.session.add(user)
            db.session.commit()
        email = Email(message=form.message.data,
                      date=datetime.utcnow(),
                      user=user)
        db.session.add_all([email, user])
        db.session.commit()
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
