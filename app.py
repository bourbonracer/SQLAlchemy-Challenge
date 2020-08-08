# Dependencies
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt

# Database set up
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

# Table references
measurement = base.classes.measurement
station = base.classes.station

# Create an app
app = Flask(__name__)

# Define routes
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

# Precipitation route - query, ravel, jsonify
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(measurement.date, measurement.prcp).all()
    session.close()
    date_prcp = list(np.ravel(results))
    return jsonify(date_prcp)

# Stations route - query, ravel, jsonify
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    statn = list(np.ravel(results))
    return jsonify(statn)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    recent_date = session.query(measurement.date).\
            filter(func.strftime("%Y/%m/%d", measurement.date)).\
            order_by(measurement.date.desc()).first()
    recent_date
    # Query previous year stations' activities by first row in descending order (most activities)
    active_station = session.query(measurement.station, func.count(measurement.station)).\
                            group_by(measurement.station).\
                            order_by(func.count(measurement.station).desc()).\
                            filter(measurement.date <= (dt.date(2017, 8, 23) - dt.timedelta(days=365))).\
                            filter(measurement.date >= (dt.date(2017, 8, 23) - dt.timedelta(days=730))).first()

    # Ravel for list
    ly_station = list(np.ravel(active_station))

    # Query date and tobs according to previous year active station
    py_station = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station==ly_station[0]).\
                filter(measurement.date <= (dt.date(2017, 8, 23) - dt.timedelta(days=365))).\
                filter(measurement.date >= (dt.date(2017, 8, 23) - dt.timedelta(days=730))).all()

    # Ravel for list and jsonify
    py_active_station = list(np.ravel(py_station))
    session.close()
    return jsonify(py_active_station)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end = None):
    session = Session(engine)
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
    session.close()
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)