from datetime import timedelta, date

from flask import (
    render_template,
    redirect,
    flash,
    url_for,
    session, request, Response, json
)
from flask_bcrypt import check_password_hash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask_wtf.csrf import generate_csrf
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError

from app import create_app, db, login_manager, bcrypt
from forms import login_form, register_form
from models import User, Watchlist
from src.DataFetcher import fetchDataForTickerSymbol

MIMETYPE = "application/json"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()


@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

@app.after_request
def add_csrf_cookie(response: Response):
    if response.status_code in range(200, 400) and not response.direct_passthrough:
        response.set_cookie("csrftoken", generate_csrf(), secure=True)
    return response


@app.route('/')
def homepage():
    if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
        return '<meta http-equiv="refresh" content="0; url=https://isthisstockgood.com" />'

    template_values = {
        'page_title': "Is This Stock Good?",
        'current_year': date.today().year,
    }
    return render_template('home.html', **template_values)


@app.route('/search', methods=['POST'])
def search():
    if request.environ['HTTP_HOST'].endswith('.appspot.com'):  # Redirect the appspot url to the custom url
        return '<meta http-equiv="refresh" content="0; url=http://isthisstockgood.com" />'

    ticker = request.values.get('ticker')
    template_values = fetchDataForTickerSymbol(ticker)
    if not template_values:
        return render_template('json/error.json', **{'error': 'Invalid ticker symbol'})
    return render_template('json/stock_data.json', **template_values)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('homepage'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
                           form=form,
                           text="Login",
                           title="Login",
                           btn_action="Login"
                           )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data

            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
            )

            db.session.add(newuser)
            db.session.commit()
            flash("Account Successfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash("Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash("User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash("Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash("Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash("An error occurred !", "danger")
    return render_template("auth.html",
                           form=form,
                           text="Create account",
                           title="Register",
                           btn_action="Register account"
                           )


@app.route("/logout", strict_slashes=False)
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/watchlist", methods=("GET", "POST", "DELETE"), strict_slashes=False)
@login_required
def watchlist():
    if request.method == "POST":
        symbol = request.values.get('ticker')
        watchlist = Watchlist.query.filter_by(userid=current_user.id).first()

        if watchlist is None:
            new_watchlist = Watchlist(userid=current_user.id, symbols=symbol)
            db.session.add(new_watchlist)
            db.session.commit()
        else:
            symbols = watchlist.symbols.split(",")
            symbols.append(symbol)
            symbols = list(dict.fromkeys(symbols))
            watchlist.symbols = ','.join(symbols)
            db.session.add(watchlist)
            db.session.commit()

        return Response(
            response=json.dumps(
                {
                    "success": True
                }
            ),
            status=200,
            mimetype=MIMETYPE
        )
    elif request.method == "DELETE":
        symbol = request.values.get('ticker')
        watchlist = Watchlist.query.filter_by(userid=current_user.id).first()
        if watchlist is not None:
            symbols = watchlist.symbols.split(",")
            try:
                symbols.remove(symbol)
            except ValueError:
                return Response(
                    response=json.dumps(
                        {
                            "success": False,
                            "error": f"Symbol {symbol} is not in your watchlist."
                        }
                    ),
                    status=404,
                    mimetype=MIMETYPE
                )

            watchlist.symbols = ",".join(symbols)
            db.session.add(watchlist)
            db.session.commit()

        return Response(
            response=json.dumps(
                {
                    "success": True
                }
            ),
            status=200,
            mimetype=MIMETYPE
        )
    else:
        data = Watchlist.query.filter_by(userid=current_user.id).first()

        return Response(
            response=json.dumps({
                "success": True,
                "data": data.symbols if data is not None else ""
            }),
            status=200,
            mimetype=MIMETYPE
        )


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
