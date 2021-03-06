from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from time import time
import jwt
from app import app

user_book = db.Table('user_book',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True)
)#many to many relationship

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_public = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    books = db.relationship(
        'Book', secondary=user_book,
        backref=db.backref('user', lazy='dynamic'))

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def set_profile(self, profile_type):
        self.is_public = profile_type

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_books_by_name_desc(self):
        return Book.query.join(
            user_book, (user_book.c.book_id == Book.id)).filter(
                user_book.c.user_id == self.id).order_by(Book.name.desc())
    def get_books_by_name_asc(self):
        return Book.query.join(
            user_book, (user_book.c.book_id == Book.id)).filter(
                user_book.c.user_id == self.id).order_by(Book.name)
    def get_books_by_author_desc(self):
        return Book.query.join(
            user_book, (user_book.c.book_id == Book.id)).filter(
                user_book.c.user_id == self.id).order_by(Book.author.desc())
    def get_books_by_author_asc(self):
        return Book.query.join(
            user_book, (user_book.c.book_id == Book.id)).filter(
                user_book.c.user_id == self.id).order_by(Book.author)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    author = db.Column(db.String(20))
    create_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Book {}>' % self.name