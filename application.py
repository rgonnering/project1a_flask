import os

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
#from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)
# bcrypt = Bcrypt(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# default route---------------------------------------------------
@app.route("/")
def index():
    return redirect(url_for('dashboard'))

# register -------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    message = None
    """
    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password")   
        if usern:
            render_template("registration.html", message="username passed")         
        if not usern:
            render_template("registration.html", message="no username")
        result = db.execute("INSERT INTO accounts (username, password) VALUES (:u, :p)", {"u": usern, "p": passw})
        db.commit()
        if result.rowcount > 0:
            session['user'] = usern
            return redirect(url_for('dashboard'))
    return render_template("registration.html", message="Fucked UP")
    """
    if request.method == "POST":
        try: 
            usern = request.form.get("username")
            passw = request.form.get("password")
            #passw_hash = bcrypt.generate_password_hash(passw).decode('utf-8')

            #result = db.execute("INSERT INTO accounts (username, password) VALUES (:u, :p)", {"u": usern, "p": passw_hash})
            result = db.execute("INSERT INTO accounts (username, password) VALUES (:u, :p)", {"u": usern, "p": passw})
            db.commit()

            if result.rowcount > 0:
                session['user'] = usern
                return redirect(url_for('dashboard'))

        except exc.IntegrityError:
            message = "Username already exists."
            db.execute("ROLLBACK")
            db.commit()

    return render_template("registration.html", message=message)


# logout -------------------------------------------------------
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# login -------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    message = None

    if request.method == "POST":
        usern = request.form.get("username")
        passw = request.form.get("password")
        print(usern, passw)
        result = db.execute("SELECT * FROM accounts WHERE username = :u", {"u": usern}).fetchone()

        if result is not None:
            print(result['username'], result['password'])
            #if bcrypt.check_password_hash(result['password'], passw) is True:
            if result['password'] == passw:
                session['user'] = usern
                return redirect(url_for('dashboard'))

    message = "Username or password is incorrect."
    return render_template("login.html", message=message)

# dashboard -------------------------------------------------------
@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template("dashboard.html", logged=session['user'])

# dashboard/search route ------------------------------------------
@app.route("/dashboard/search", methods=["POST"])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = None
    query = request.form.get("searchbox")
    query = '%' + query.lower() + '%'
    results = db.execute("SELECT * FROM books WHERE lower(title) LIKE :q OR isbn LIKE :q OR lower(author) LIKE :q", {"q": query}).fetchall()
    return render_template("search.html", results=results)

#  -------------------------------------------------------
@app.route("/b/<string:isbn>", methods=["GET", "POST"])
def info(isbn):

    
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        comment = request.form.get("comment")
        my_rating = request.form.get("rating")
        #book = db.execute("INSERT INTO reviews (acc_id, book_id, comment, rating) VALUES (:a, :b, :c, :r)", {"a": session['user'], "b": isbn, "c": comment, "r": my_rating})
        book = db.execute("INSERT INTO reviews (username, isbn, mycomment, myreview) VALUES (:a, :b, :c, :r)", {"a": session['user'], "b": isbn, "c": comment, "r": my_rating})
        db.commit()

    book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    reviews = db.execute("SELECT * FROM reviews WHERE isbn = :q1", {"q1": isbn}).fetchall()

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()
    gr_rating = (data['books'][0]['average_rating'])

    return render_template("info.html", book_info=book, reviews=reviews, rating=gr_rating)

# api/isbn route -----------------------------------------------
@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    reviews = db.execute("SELECT * FROM reviews WHERE book_id = :q1", {"q1": isbn}).fetchall()
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()['books'][0]
    
    return jsonify({
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "review_count": data['reviews_count'],
        "average_rating": data['average_rating']
    })