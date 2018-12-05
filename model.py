from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ParkingEvent(db.Model):

  __tablename__ = "parkingevents"
  parkingevent_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  floor = db.Column(db.Integer(), nullable=False)
  duration = db.Column(db.Integer(), nullable=False)
  lat = db.Column(db.Float(), nullable=False)
  long = db.Column(db.Float(), nullable=False)
  time = db.Column(db.String(64), nullable=False)
  arrivDepart = db.Column(db.String(64), nullable=False)

class Garage(db.Model):
  __tablename__ = "garages"
  garage_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
  name = db.Column(db.String(64), nullable=False)
  lat = db.Column(db.Float(), nullable=False)
  long = db.Column(db.Float(), nullable=False)
  addr = db.Column(db.String(64), nullable=False)
  price = db.Column(db.Float(), nullable=False)
  spaces = db.Column(db.Integer, nullable=False)

def connect_to_db(app):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///parkingbuddy'  # weekend wanderlust map
    db.app = app
    db.init_app(app)

if __name__ == "__main__":
    # Allows interactive querying in the shell

    from app import app
    connect_to_db(app)
    print "Connected to DB."
