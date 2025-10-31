from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

app = Flask(__name__)
ma = Marshmallow(app)

# set the database URI via SQLAlchemy, 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://db_dev:123456@localhost:5432/trello_clone_db"

# to avoid the deprecation warning
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#create the database object
db = SQLAlchemy(app)

class Card(db.Model):
    # define the table name for the db
    __tablename__= "cards"
    # Set the primary key, we need to define that each attribute is also a column in the db table, remember "db" is the object we created in the previous step.
    id = db.Column(db.Integer,primary_key=True)
    # Add the rest of the attributes. 
    title = db.Column(db.String())
    description = db.Column(db.String())
    date = db.Column(db.Date())
    status = db.Column(db.String())
    priority = db.Column(db.String())
    
    
#create the Card Schema with Marshmallow, 
#it will provide the serialization needed for converting the data into JSON
class CardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # Fields to expose
        model = Card
        load_instance = True


#single card schema, when one card needs to be retrieved
card_schema = CardSchema()

#multiple card schema, when many cards need to be retrieved
cards_schema = CardSchema(many=True)
    
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
        title = "Start the project",
        description = "Stage 1, creating the database",
        status = "To Do",
        priority = "High",
        date = date.today()
    )
    # Add the object as a new row to the table
    db.session.add(card1)
    
    # create the second card object
    card2 = Card(
        # set the attributes, not the id, SQLAlchemy will manage that for us
        title = "SQLAlchemy and Marshmallow",
        description = "Stage 2, integrate both modules in the project",
        status = "Ongoing",
        priority = "High",
        date = date.today()
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
  

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/cards", methods=["GET"])
def get_cards():
    #get all the cards from the database table
    stmt = db.select(Card)
    cards = db.session.scalars(stmt).all()
    # Convert the cards from the database into a JSON format and store them in result
    result = cards_schema.dump(cards)
    #return result in JSON format
    return jsonify(result)

