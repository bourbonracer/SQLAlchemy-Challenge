# Dependencies
import numpy as np
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database set up
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

# Table references
measurement = base.classes.measurement
station = base.classes.station
session = Session(engine)

# Create an app
app = Flask(__name__)

# Define route
@app.route("/")
def home():
    return(
        f"Welcome to Hawaii Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(measurement.date, measurement.prcp).all()
    date_prcp = list(np.ravel(results))
    return jsonify(date_prcp)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    statn = list(np.ravel(results))
    return jsonify(statn)

@app.route("/api/v1.0/tobs")
def tobs():
    active_station = session.query(measurement.station, func.count(measurement.station)).\
                            group_by(measurement.station).\
                            order_by(func.count(measurement.station).desc()).\
                            filter(measurement.date <= (dt.date(2017, 8, 23) - dt.timedelta(days=365))).\
                            filter(measurement.date >= (dt.date(2017, 8, 23) - dt.timedelta(days=730))).all()
    ly_active_station = list(np.ravel(active_station))
    return jsonify(ly_active_station)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end = None):
    if end == None:
        results = session.query(func.max(measurement.tobs),\
                                  func.min(measurement.tobs),\
                                  func.avg(measurement.tobs)).\
                                  filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(func.max(measurement.tobs),\
                                  func.min(measurement.tobs),\
                                  func.avg(measurement.tobs)).\
                                  filter(measurement.date >= start).\
                                  filter(measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)