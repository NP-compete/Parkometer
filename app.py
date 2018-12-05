from flask import Flask, render_template,jsonify,redirect
from flask_sqlalchemy import SQLAlchemy
from model import connect_to_db, ParkingEvent, Garage
from query_the_db import Coord, get_garage_states
import os
import requests
from requests_oauthlib import OAuth1
import datetime
import math


app = Flask(__name__)
db = SQLAlchemy(app)

import psycopg2

# try:
#     conn = psycopg2.connect("dbname='parkingbuddy' user='dbuser' host='localhost' password='dbpass'")
# except:
#     print "I am unable to connect to the database"



@app.route("/")
def index():
  parkingevents = ParkingEvent.query.all()
  # garagesList = Garage.query.all()
  return render_template("homepage.html", events=parkingevents)

@app.route("/garages")
def get_garages():
  print "hello"
  garageList = Garage.query.all()
  print garageList
  return jsonify({"garages": garageList})

@app.route('/automatic_api')
def get_automatic_json():
  access_client_id = os.environ['AUTOMATIC_CLIENT_ID']
  access_secret = os.environ['AUTOMATIC_SECRET']
  print access_client_id
  print access_secret

  url = 'https://api.automatic.com/trip/'
  auth = OAuth1(access_client_id, access_secret)


  headers = {"Authorization": "Bearer: e5cdd2a2f2c52ac2ff9825f53ac566f45c513991"}

  # response = requests.get('https://www.example.com').content
  response = requests.get(url, headers=headers)

  print response

  return jsonify({"lat":37.8033345, "long":-122.2695569})

@app.route("/garages.geojson")
def makejson():
    """Construct geojson for map markers."""

    parkingEvents = ParkingEvent.query.all()
    garageList = Garage.query.all()
    score_dict = get_garage_states()

    garage_geojson = {
                     "type": "FeatureCollection",
                     "features": []
                     }

    for garage in garageList:
      if score_dict[garage.name] <= 10:
        color = "#C70039"
      elif score_dict[garage.name] > 10 and score_dict[garage.name] <= 50:
        color = "#FF5733"
      else:
        color = "#FFC300"

      single_garage_json = {
                         "type": "Feature",
                         "properties": {
                            "name": garage.name,
                            "addr": garage.addr,
                            "price": garage.price,
                            "spaces": garage.spaces,
                            "scores": score_dict[garage.name],
                            "marker-symbol": "car",
                            "marker-color": color
                            },
                         "geometry": {
                            "coordinates": [
                                garage.long,
                                garage.lat],
                                "type": "Point"
                            },
                         "id": garage.garage_id
                         }
      garage_geojson["features"].append(single_garage_json)

    return jsonify(garage_geojson)


if __name__ == "__main__":
  app.debug = True
  connect_to_db(app)
  app.run()
