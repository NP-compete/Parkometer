import datetime
import math
from model import connect_to_db, ParkingEvent, Garage

# read the garage data
# class GarageData:
#     def __init__(self):
#         self.m = []
#         header = ["name",
#                   "address",
#                   "lat",
#                   "long",
#                   "price",
#                   "spaces"]
#         infile = open("./garageData.csv")
#         lines = infile.read().split("\n")
#         lines.pop(0) # remove supplied header line
#         for line in lines:
#             line = line.rstrip()
#             row = {}
#             tokens = line.split(",")
#             if tokens[2][0] == " ": # comma in address field between street and city
#                 tokens[1] = ", ".join([tokens[1],
#                                        tokens[2]])
#                 del tokens[2]
#             for i in range(len(header)):
#                 row[header[i]] = tokens[i]
#             self.m.append(row)
# gd = GarageData()
# print

# # read the parking event data
# class ParkingEventData:
#     def __init__(self):
#         self.m = []
#         header = ["floor",
#                   "duration",
#                   "lat",
#                   "long",
#                   "time",
#                   "arriveDepart"]
#         infile = open("/Users/nathan/code/parkingBuddy/parkingData.csv")
#         lines = infile.read().split("\n")
#         for line in lines:
#             line = line.rstrip()
#             row = {}
#             tokens = line.split(",")
#             for i in range(len(header)):
#                 row[header[i]] = tokens[i]
#             self.m.append(row)
#         # fix time data
#         timestrs = ["2015-04-12T17:45:01.123Z",
#                     "2015-04-12T17:48:01.123Z",
#                     "2015-04-12T18:46:01.123Z",
#                     "2015-04-12T18:55:01.123Z"]
#         for i,row in enumerate(self.m):
#             row["time"] = timestrs[i]
# ped = ParkingEventData()

class Coord:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    def display(self):
        return str(self.lat) + "," + str(self.lon)
    @staticmethod
    def haversine_distance(a, b):
        DEG_TO_RAD = math.pi / 180.0
        KM_TO_MILES = 0.621371
        startLat = float(a.lat)
        startLong = float(a.lon)
        endLat = float(b.lat)
        endLong = float(b.lon)
        dlat = (endLat - startLat) * DEG_TO_RAD
        dlong = (endLong - startLong) * DEG_TO_RAD
        # Diameter of the Earth at a given latitude, in kilometers
        # 6378 km is max (equatorial) radius, 6357 km is mean radius,
        # 6357 is min (polar) radius.
        # Calculate the diameter of the earth at the latitude of pt1
        d = 6378 - 21 * math.sin(startLat * DEG_TO_RAD)
        a = math.pow(math.sin(dlat / 2), 2) + \
            math.pow(math.cos(startLat * DEG_TO_RAD), 2) * \
            math.pow(math.sin(dlong / 2), 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        dist_km = math.fabs(c * d)
        dist_mi = dist_km * KM_TO_MILES
        return dist_mi
    def insideBox(self, west, east, south, north):
        # only works for western hemisphere, northern hemisphere
        rv = False
        westOk = west <= self.lon
        eastOk = self.lon <= east
        southOk = south <= self.lat
        northOk = self.lat <= north
        if westOk and eastOk and southOk and northOk:
            rv = True
        return rv

def get_garage_states():
    # for all garages, find their arrival and departure counts in the
    #  past hour
    # currentTime is in the iso format "2015-04-12T18:55:01.123Z"
    parkingEvents = ParkingEvent.query.all()
    garageList = Garage.query.all()
    pct_avail_by_garage_name = {} # percent availability for each garage by its name
    fmt = "%Y-%m-%d %H:%M:%S"
    for i,garage in enumerate(garageList):
        garageCoord = Coord(garage.lat,
                            garage.long) # assume that the lat and long are in float already
        #currentTimeStr = currentTime.replace("T"," ")
        #currentTimeStr = currentTimeStr.split(".")[0]
        #currentTime_dt = datetime.datetime.strptime(currentTimeStr,fmt)
        currentTime_dt = datetime.datetime.now()
        oneHourBack_dt = currentTime_dt - datetime.timedelta(hours=1)
        sumArrivalHr = 0
        sumDepartureHr = 0
        for parkingEvent in parkingEvents:
            # check if within the past hour
            eventTimeUnix = parkingEvent.time # a string as pulled from the db
            eventTime_dt = datetime.datetime.fromtimestamp(long(eventTimeUnix))
            #timestr = timestr.split(".")[0]
            #rowtime_dt = datetime.datetime.strptime(timestr,fmt)
            if oneHourBack_dt <= eventTime_dt:
                # check if within 30 m
                parkingEventCoord = Coord(float(parkingEvent.lat),
                                          float(parkingEvent.long))
                dist_mi = Coord.haversine_distance(garageCoord,
                                                   parkingEventCoord)
                dist_m = dist_mi * 1609.34
                if dist_m <= 30:
                    if parkingEvent.arriveDepart == "arrival":
                        sumArrivalHr += 1
                    if parkingEvent.arriveDepart == "departure":
                        sumDepartureHr += 1
        diffVehCountHour = sumArrivalHr - sumDepartureHr
        pct_avail = 0
        if diffVehCountHour >= 5:
            pct_avail = 10
        if diffVehCountHour <= -5:
            pct_avail = 90
        if -5 < diffVehCountHour and diffVehCountHour < 5:
            pct_avail = 90 - (diffVehCountHour + 5)*8
        pct_avail = 10 + (i%3)*40
        pct_avail_by_garage_name[garage.name] = pct_avail


    #rv = json.dumps(pct_avail_by_garage_name)
#     outfile = open("/Users/nathan/code/parkingBuddy/garage_pct_avail.csv",'wb')
#     header = ["Garage Name","pct_avail"]
#     outfile.write(",".join(header)+"\n")
#     for i,garage in enumerate(gd.m):
#         outfile.write(",".join([garage["name"],
#                                 str(pct_avail_by_garage_name[garage["name"]])]))
#         if i < len(gd.m)-1:
#             outfile.write("\n")
#     outfile.close()
    return pct_avail_by_garage_name


# @app.route("/garages.geojson")
# def makejson():
#     """Construct geojson for map markers."""

#     parkingEvents = ParkingEvent.query.all()
#     garageList = Garage.query.all()
#     score_dict = get_garage_states()

#     garage_geojson = {
#                      "type": "FeatureCollection",
#                      "features": [
#                         {
#                          "type": "Feature",
#                          "properties": {
#                             "name": garage.name,
#                             "addr": garage.addr,
#                             "price": garage.price,
#                             "spaces": garage.spaces,
#                             "scores": score_dict[garage.name]
#                             },
#                          "geometry": {
#                             "coordinates": [
#                                 garage.long,
#                                 garage.lat],
#                                 "type": "Point"
#                             },
#                          "id": garage.garage_id
#                          }
#                     for garage in garageList
#                     ]
#                 }
#     return jsonify(garage_geojson)


# currentTime = "2015-04-12T18:55:01.123Z"
# pct_avail_by_garage_name = get_garage_states(gd, ped, currentTime)
# print