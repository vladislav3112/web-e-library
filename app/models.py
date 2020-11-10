from app import db
from app import login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    books = db.relationship('Book', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_books_by_name_desc(self):
        return Book.query.filter(Book.user_id == self.id).order_by(Book.name.desc())
    def get_books_by_name_asc(self):
        return Book.query.filter(Book.user_id == self.id).order_by(Book.name)
    def get_books_by_author_desc(self):
        return Book.query.filter(Book.user_id == self.id).order_by(Book.author.desc())
    def get_books_by_author_asc(self):
        return Book.query.filter(Book.user_id == self.id).order_by(Book.author)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    author = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #image = db.Column(ImageColumn(size=(300, 300, True), thumbnail_size=(30, 30, True)))

    def __repr__(self):
        return '<Book {}>' % self.name