from model import ParkingEvent, Garage, connect_to_db, db
from app import app
import csv
from datetime import datetime

def load_sessions(file):
  with open(file) as csvfile:
    csvreader = csv.reader(csvfile)
    # next(csvreader)



  # floor = db.Column(db.Integer(), nullable=False)
  # duration = db.Column(db.Integer(), nullable=False)
  # lat = db.Column(db.Integer(), nullable=False)
  # long = db.Column(db.Integer(), nullable=False)
  # time = db.Column(db.String(64), nullable=False)
    for i, row in enumerate(csvreader):
      newParkingEvent = ParkingEvent(floor=row[0],
                                duration=row[1],
                                lat=row[2],
                                long=row[3],
                                time=row[4],
                                arrivDepart=row[5]
                                            )
      db.session.add(newParkingEvent)
      if i % 10 == 0:
        print i

    db.session.commit()

def load_garages(file):
    with open(file) as csvfile:
      csvreader = csv.reader(csvfile)
      next(csvreader)
      for i, row in enumerate(csvreader):
        newGarage = Garage(name=row[0],
                                addr=row[1],
                                lat=row[2],
                                long=row[3],
                                price=row[4],
                                spaces=row[5]
                                            )
        db.session.add(newGarage)
        if i % 10 == 0:
          print i

    db.session.commit()



if __name__ == '__main__':
  connect_to_db(app)
  db.create_all()

  load_sessions('./parkingData.csv');
  load_garages('./garageData.csv');
