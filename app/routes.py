from flask import render_template, flash, redirect, url_for
from flask import request
from app import app, db
from app.forms import LoginForm, RegestrationForm
from flask_login import logout_user
from flask_login import current_user, login_user
from flask_login import login_required
from app.models import User, Book
from app.forms import BookForm
from werkzeug.urls import url_parse
import os
from flask import send_from_directory   
from app.forms import ResetPasswordRequestForm
from app.email import send_password_reset_email
from app.forms import ResetPasswordForm
from datetime import datetime

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    sort_type = request.form.get('sort_type')
    if sort_type == "2":
        books = current_user.get_books_by_name_desc() 
    elif sort_type == "3":
        books = current_user.get_books_by_author_asc() 
    elif sort_type == "4":
        books = current_user.get_books_by_author_desc() 
    else: 
         books = current_user.get_books_by_name_asc() 
    return render_template('index.html', title='Home', books = books)

@app.route('/logout')
def logout():
    current_user.last_seen = datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html',  title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegestrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email = form.email.data)
        user.set_password(form.password.data)
        user.set_profile(form.profile_type.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        if request.method == 'POST':
            existing_book = Book.query.filter(Book.name == form.name.data).filter(Book.user_id == current_user.id).first()
            book = Book(name = form.name.data, author = form.author.data, user = current_user)
            
            if ((existing_book != None)and(existing_book.name == form.name.data and  existing_book.author == form.author.data and existing_book.user_id == current_user.id)):
                flash('Book already exists!')
                return redirect(url_for('add_book'))
            
            book.create_time = datetime.utcnow()

            db.session.add(book)
            db.session.commit()
            flash('Your book succesfully added!')
            return redirect(url_for('index'))
    return render_template("add_book.html", title = 'Add_book', form = form)

@app.route('/delete/<id>', methods=['POST'])
def delete_book(id):
    Book.query.filter(Book.user_id == current_user.id).filter(Book.id == id).delete()
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
        else:
             flash('No existing user with this email!')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)
                           
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    Books = Book.query.filter(Book.user_id == user.id).order_by(Book.name.desc())
    if(user.is_public or user.is_public==None):
        return render_template('user.html', user=user, books = Books)
    else:
        flash('Sorry, user has private profile!')
        return redirect(url_for('index'))

@app.route('/new_books')
@login_required
def new_books():
    Books = Book.query.join(
            User, (User.id == Book.user_id)).filter(
                User.is_public == True).filter(
                Book.create_time > current_user.last_seen).order_by(
                    Book.create_time.desc())

    #Books = Book.query.filter(Book.create_time > current_user.last_seen).filter(User.query.filter(user)).order_by(Book.create_time.desc())
    return render_template('new_books.html', user=current_user, books = Books)