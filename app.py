from flask import Flask, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import random
from datetime import datetime

app = Flask(__name__)
ma = Marshmallow(app)

# set the database URI via SQLAlchemy,
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://db_dev:123456@localhost:5432/trello_clone_db"
)

# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# create the database object
db = SQLAlchemy(app)


class Card(db.Model):
    # define the table name for the db
    __tablename__ = "cards"
    # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
    id = db.Column(db.Integer, primary_key=True)
    # Add the rest of the attributes.
    title = db.Column(db.String())
    description = db.Column(db.String())
    date = db.Column(db.Date())
    status = db.Column(db.String())
    priority = db.Column(db.String())


# create the Card Schema with Marshmallow,
# it will provide the serialization needed for converting the data into JSON
class CardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # Fields to expose
        model = Card
        load_instance = True


# single card schema, when one card needs to be retrieved
card_schema = CardSchema()

# multiple card schema, when many cards need to be retrieved
cards_schema = CardSchema(many=True)


# CLI Commands
# create app's cli command named create, then run it in the terminal as "flask create",
# it will invoke create_db function
@app.cli.command("create")
def create_db():
    db.create_all()
    print("Tables created")


@app.cli.command("seed")
def seed_db():
    from datetime import date

    # create the first card object
    card1 = Card(
        # set the attributes, not the id, SQLAlchemy will manage that for us
        title="Start the project",
        description="Stage 1, creating the database",
        status="To Do",
        priority="High",
        date=date.today(),
    )
    # Add the object as a new row to the table
    db.session.add(card1)

    # create the second card object
    card2 = Card(
        # set the attributes, not the id, SQLAlchemy will manage that for us
        title="SQLAlchemy and Marshmallow",
        description="Stage 2, integrate both modules in the project",
        status="Ongoing",
        priority="High",
        date=date.today(),
    )
    # Add the object as a new row to the table
    db.session.add(card2)
    # commit the changes
    db.session.commit()
    print("Table seeded")


@app.cli.command("drop")
def drop_db():
    db.drop_all()
    print("Tables dropped")


# Routes

art_dict = {
    "composition 8": {
        "When": "1923",
        "Artist": "Vasily Kandinsky",
        "Medium": "Oil Painting",
        "Place": "Moscow",
        "Periods": ["Suprematism", "Abstract art"],
    },
    "Royal Red and Blue": {
        "When": "1954-1954",
        "Artist": "Mark Rothko",
        "Medium": "Oil Paint",
        "Place": "Litvak Descent",
        "Periods": ["Washington Color School"],
    },
    "Starry Night": {
        "When": "1889",
        "Artist": "Vincent van Gogh",
        "Medium": "Oil Painting",
        "Place": "Netherlands",
        "Periods": ["Post-Impressionism", "Modern art"],
    },
}


@app.route("/")
def hello():
    return """<p>Hi, welcome to my API! Here are the endpoints that are available:</p>
    <ul>
    <li>Current Time: /time</li>
    <li>Educator Info: /educators</li>
    <li>Cards: /cards</li>
    <li>Coin Flip: /coinflip</li>
    </ul>"""


@app.route("/cards", methods=["GET"])
def get_cards():
    # get all the cards from the database table
    stmt = db.select(Card)
    cards = db.session.scalars(stmt).all()
    # Convert the cards from the database into a JSON format and store them in result
    result = cards_schema.dump(cards)
    # return result in JSON format
    return jsonify(result)


@app.route("/time")
def current_time():
    time_dict = {"current time": str(datetime.now().strftime("%H:%M"))}
    return json.dumps(time_dict)


@app.route("/educators")
def educators():
    educator_dict = {
        "educators": [
            {"Name": "Oliver", "Specialty": "Automated testing"},
            {"Name": "Jairo", "Specialty": "Discrete Mathematics"},
            {"Name": "Amir", "Specialty": "Web Development"},
            {"Name": "Iryna", "Specialty": "Database Engineering"},
            {"Name": "George", "Specialty": "Internet Security"},
        ]
    }
    return json.dumps(educator_dict)
  
# Custom route
@app.route("/some_value/<some_value>")
def some_page(some_value):
    return f"<p>You gave the value {some_value} in the route!</p>"


@app.route("/starry_night")
def homepage():
     return json.dumps(art_dict["Starry Night"])
   
@app.route("/art/<painting_name>")
def get_painting(painting_name):
    # Returns information on a painting in the collection.
    
    # If there's no such painting, we return a 404 NOT FOUND error!
    if not painting_name in art_dict:
        abort(404)
    
    return json.dumps(art_dict[painting_name])

@app.route("/artists/<artist_name>")
def get_artist(artist_name):
    # Returns a list of paintings by a given artist.
    art_list = []
    for painting in art_dict.values():
        if artist_name == painting["Artist"]: 
            art_list.append(painting)
    
    # If there's no such artist, we return a 404 NOT FOUND error!
    if not art_list:
        abort(404)

    return json.dumps(art_list)


@app.route("/coinflip")
def coinflip():
    result = ["heads", "tails"]
    return jsonify({"result": random.choice(result)})


# @app.route("/success/<int:score>")
# def success():
#     return "You passed the exam with a score of " + str(score)


@app.route("/results/<int:score>")
def results(score):
    if score >= 50:
        result = "Success"
    else:
        result = "Fail"
    return result
  
@app.route("/calculate/<int:num1>/<string:operation>/<int:num2>")
def calculate(num1, operation, num2):
    if operation == "add":
        result = num1 + num2
        return f"The sum of {num1} and {num2} is {result}"
    elif operation == "subtract":
        result = num1 - num2
        return f"The difference of {num1} and {num2} is {result}"
    elif operation == "multiply":
        result = num1 * num2
        return f"The product of {num1} and {num2} is {result}"
    elif operation == "divide":
        result = num1 / num2
        return f"The quotient of {num1} and {num2} is {result}"
    else:
        return "Invalid operation"
  


@app.route("/string_route/<string:some_string>")
def string_route(some_string):
    """A route that accepts a string variable."""
    return f"The string value is {some_string}"

@app.route("/int_route/<int:some_int>")
def int_route(some_int):
    """A route that accepts an integer variable."""
    return f"The integer value is {some_int}"

@app.route("/float_route/<float:some_float>")
def float_route(some_float):
    """A route that accepts a float variable."""
    return f"The float value is {some_float}"

@app.route("/path_route/<path:some_path>")
def path_route(some_path):
    # A route that takes you to another page.
    return f"The URL path is {some_path}"