import os
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    total_equity = 0
    # get stocks
    stocks = db.execute(
        "SELECT symbol, name, price, SUM(shares) as total_shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING total_shares > 0", user_id)
    # find user and cash
    cash = db.execute("SELECT cash from users where id = ?", user_id)[0]["cash"]
    # make list
    curr_prices = []
    for stock in stocks:
        quote = lookup(stock["symbol"])
        curr_prices.append({
            "symbol": quote["symbol"],
            "name": quote["name"],
            "shares": stock["total_shares"],
            "curr_share_price": quote["price"],
            "compound_shares": quote["price"] * stock["total_shares"]
        })
        total_equity += quote["price"] * stock["total_shares"]
    total_equity += cash
    # push to HTML
    return render_template("index.html", curr_prices=curr_prices, stocks=stocks, cash=cash, usd=usd, total_equity=total_equity)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy stocks"""
    if request.method == "POST":
        # Check shares
        quote = lookup(request.form.get("symbol"))

        if quote == None:
            return apology("type something please")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Enter a round number please")

        if shares <= 0:
            return apology("Please enter a number")
        # check cash
        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])

        cash_remaining = rows[0]["cash"]

        price_per_share = quote["price"]

        total_price = price_per_share * shares

        item_name = quote["name"]

        if total_price > cash_remaining:
            return apology("You broke")
        # Update database
        db.execute("UPDATE users SET cash = cash - :price WHERE id = :user_id", price=total_price, user_id=session["user_id"])
        db.execute("INSERT INTO transactions (user_id, name, symbol, shares, price) VALUES(:user_id, :name, :symbol, :shares, :price)",
                   user_id=session["user_id"],
                   name=item_name,
                   symbol=request.form.get("symbol").upper(),
                   shares=shares,
                   price=price_per_share)

        flash("money to blow!")

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT symbol, shares, price, time FROM transactions where user_id = :user_id ORDER BY time ASC", user_id=session["user_id"])

    for i in range(len(transactions)):
        transactions[i]["price"] = usd(transactions[i]["price"])

    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if lookup(request.form.get("symbol")) == None:
        return apology("Invalid symbol", 400)

    if request.method == "POST":
        symbol = request.form.get("symbol")
        market = lookup(symbol)

        return render_template("quoted.html", moeilijk=market, usd=usd)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Access data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("Password it not the same", 400)
        # check password for lower, upper, number, symbol. using import re
        if not username:
            return apology("Username is required")
        elif not password:
            return apology("Password is required")
        elif len(password) < 5:
            return apology("min length 5")
        elif re.search("[0-9]", password) is None:
            return apology("Make sure your password has a number in it")
        elif re.search("[A-Z]", password) is None:
            return apology("Make sure your password has a capital letter in it")
        elif re.search("[a-z]", password) is None:
            return apology("Make sure your password uses lower case letters")
        elif re.search("[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", password) is None:
            return apology("Make sure your password uses special characters")

        security_hash = generate_password_hash(request.form.get("password"))
        # Add the user's credentials into the database
        try:
            db.execute("insert into users (username, hash) values(?, ?)", username, security_hash)
        except:
            return apology("Username already exists!")

        #flash("Registration successful")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        if quote == None:
            return apology("type something please")

        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("Round number please")

        if shares <= 0:
            return apology("Choose amount of shares")

        rows = db.execute(
            "SELECT symbol, SUM(shares) as total_shares FROM transactions WHERE user_id = :user_id GROUP BY symbol HAVING total_shares > 0;", user_id=session["user_id"])
        for row in rows:
            if shares > row["total_shares"]:
                return apology("Selling too many shares")

        rows = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session["user_id"])

        cash_remaining = rows[0]["cash"]

        price_per_share = quote["price"]

        total_price = price_per_share * shares

        item_name = quote["name"]

        db.execute("UPDATE users SET cash = cash + :price WHERE id = :user_id", price=total_price, user_id=session["user_id"])
        db.execute("INSERT INTO transactions (user_id, name, symbol, shares, price) VALUES(:user_id, :name, :symbol, :shares, :price)",
                   user_id=session["user_id"],
                   name=item_name,
                   symbol=request.form.get("symbol"),
                   shares=-1 * shares,
                   price=price_per_share)

        flash("Paper hands!")

        return redirect("/")

    else:
        rows = db.execute(
            "SELECT symbol FROM transactions WHERE user_id = :user_id GROUP by symbol HAVING SUM(shares) > 0;", user_id=session["user_id"])
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])


@app.route("/loan", methods=["GET", "POST"])
@login_required
def loan():
    """Take a loan without interest or return policy so its free money"""
    if request.method == "POST":
        db.execute("UPDATE users SET cash = cash + :amount WHERE id=:user_id",
                   amount=request.form.get("cash"), user_id=session["user_id"])
        flash("You are rich!")
        return redirect("/")
    else:
        return render_template("loan.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)