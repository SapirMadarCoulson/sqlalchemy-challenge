# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# reflect an existing database into a new model

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON list of precipitation data for the last year."""

 # Calculate 
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()

    # Convert to dictionary
    precip_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    station_list = session.query(Station.station).all()
    return jsonify(stations=[station[0] for station in station_list])

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the last year of the most active station."""
    # Most active station
    active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()
    most_active_station = active_station[0]

    # Calculate the date one year ago from the last data point
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)

    # Query the temperature observations for the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= last_year).all()

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end=None):
    """Return a JSON list of min, avg, and max temperature for a given start or start-end range."""
    if end:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    temp_stats = list(data[0])
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
#################################################
# Flask Routes
#################################################
