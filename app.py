## Step 2 - Climate App
#   Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.
#   * Use FLASK to create your routes.
#   ### Routes
#   * `/api/v1.0/precipitation`
#   * Query for the dates and temperature observations from the last year.
#   * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#   * Return the JSON representation of your dictionary.
#   * `/api/v1.0/stations`
#   * Return a JSON list of stations from the dataset.
#   * `/api/v1.0/tobs`
#   * Return a JSON list of Temperature Observations (tobs) for the previous year
#   * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`
#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
#   ## Hints
#   * You will need to join the station and measurement tables for some of the analysis queries.
#   * Use Flask `jsonify` to convert your API data into a valid JSON response object.
#   ## Copyright
#   Data Boot Camp Â©2018. All Rights Reserved.
#

import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, render_template


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///static/Resources/hawaii.sqlite")
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return render_template("index.html")

@app.route("/api/v1.0/precipitation")
def precipitation():
    ### * `/api/v1.0/precipitation`
    #   * Query for the dates and temperature observations from the last year.
    #   * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    #   * Return the JSON representation of your dictionary.
    """Return a list of rain fall for prior year"""
    #    * Query for the dates and precipitation observations from the last year.
    #           * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    #           * Return the json representation of your dictionary.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = (dt.datetime.strptime(last_date[0], '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    temperature = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.date > last_year). \
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` and `prcp` as the keys and values
    rain_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        rain_totals.append(row)

    return jsonify(rain_totals)

#########################################################################################
@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())
#########################################################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
    #    * Query for the dates and temperature observations from the last year.
    #           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    #           * Return the json representation of your dictionary.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.date > last_year). \
        order_by(Measurement.date).all()

    # Create a list of dicts with `date` and `tobs` as the keys and values
    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)
#########################################################################################
@app.route("/api/v1.0/<start>")
def trip1(start):
    # go back one year from start date and go to end of data for Min/Avg/Max temp
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################
@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

    # go back one year from start/end date and get Min/Avg/Max temp
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)