# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
Station = Base.classes.station


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
def home():
    """List all available api routes."""
   
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

#Convert the query results to a dictionary using `date` as the key and 
# `prcp` as the value. and Return the JSON representation of your dictionary.
@app.route('/api/v1.0/precipitation')
def precipitation():
    
    session=Session(engine)

    most_recent=session.query(measurement.date)\
    .order_by(measurement.date.desc()).first()

    date_time = dt.datetime.strptime(most_recent[0], '%Y-%m-%d')

    date1=date_time.date()
    date2=date1-dt.timedelta(days=365)
    precipitation=session.query(measurement.date, measurement.prcp)\
    .order_by(measurement.date.desc())\
    .filter(measurement.date<= date1)\
    .filter(measurement.date >= date2)\
    .all()
    session.close()

    daily_precip=[]
    for date, prcp in precipitation:
        precip_dict = {}
        precip_dict[date] = prcp
        daily_precip.append(precip_dict)
    
    return jsonify(daily_precip)

# Return a JSON list of stations from the dataset.
@app.route('/api/v1.0/stations')
def stations():
    
    session=Session(engine)
    stations = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(stations))

    return  jsonify(all_stations)

#Query the dates and temperature observations of the most active station 
# for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year
@app.route('/api/v1.0/tobs')
def tobs():
    
    session=Session(engine)
    most_recent=session.query(measurement.date)\
    .order_by(measurement.date.desc()).first()
    #convert query result into date
    date_time = dt.datetime.strptime(most_recent[0], '%Y-%m-%d')

    #get date ranges for query 
    date1=date_time.date()
    date2=date1-dt.timedelta(days=365)


    temp=session.query( measurement.tobs)\
    .filter(measurement.station =='USC00519281')\
    .filter(measurement.date<=date1)\
    .filter(measurement.date >=date2)\
    .all()
    session.close()

    tobs = list(np.ravel(temp))
    return jsonify(tobs)


# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` 
# for all dates greater than and equal to the start date.
@app.route('/api/v1.0/<start>')
def start_temp(start):

    """fetch temperatures from 'start' date to the latest or most recent data"""
   
    session=Session(engine)
    
    min_temp=session.query(func.min(measurement.tobs))\
    .filter(measurement.date >=start)\
    .all()

    max_temp=session.query(func.max(measurement.tobs))\
    .filter(measurement.date >=start)\
    .all()

    avg_temp=session.query(func.avg(measurement.tobs))\
    .filter(measurement.date >=start)\
    .all()

    session.close()
   
    temp_stats = {}
    temp_stats["TMIN"] = min_temp
    temp_stats["TMAX"] = max_temp
    temp_stats["TAVG"] = avg_temp
      
    return jsonify(temp_stats)



# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` 
# for dates between the start and end date inclusive.
@app.route('/api/v1.0/<start>/<end>')
def startend_temp(start, end):

    """fetch temperatures from 'start' date to 'end' date"""
   
    session=Session(engine)
    
    min_temp=session.query(func.min(measurement.tobs))\
    .filter(measurement.date >=start)\
    .filter(measurement.date <=end)\
    .all()

    max_temp=session.query(func.max(measurement.tobs))\
    .filter(measurement.date >=start)\
    .filter(measurement.date <=end)\
    .all()

    avg_temp=session.query(func.avg(measurement.tobs))\
    .filter(measurement.date >=start)\
    .filter(measurement.date <=end)\
    .all()


    session.close()
   
    temp_stats = {}
    temp_stats["TMIN"] = min_temp
    temp_stats["TMAX"] = max_temp
    temp_stats["TAVG"] = avg_temp
      

    #std_temps = list(np.ravel(temp_stats))
    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)      