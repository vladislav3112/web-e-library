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

@app.route('/')
@app.route('/index')
@login_required
def index():
    books = current_user.get_books() 
    return render_template('index.html', title='Home', books = books)

@app.route('/logout')
def logout():
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
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title = 'Register', form = form)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(name = form.name.data, author = form.author.data, user = current_user)
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