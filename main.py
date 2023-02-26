from base_functions import *
from firebase import db
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, Locations, LocationGlobal

# PARAMETERS
altitude = 10

# Waiting for vehicle to initialise
wait_until_armable()

# Get home location
home = get_current_location()
homeLocation_lat = home.lat
homeLocation_lon = home.lon
homeLocation = LocationGlobalRelative(homeLocation_lat, homeLocation_lon, altitude)
send_live_location()

# Start Mission
#wpList
while True:
    hospitalLocation_lat = db.child("HospitalLocation").child("hospitalLocation_lat").get().val()
    hospitalLocation_long = db.child("HospitalLocation").child("hospitalLocation_long").get().val()

    if (hospitalLocation_lat and hospitalLocation_long) != 0:
        hospitalLocation = LocationGlobalRelative(hospitalLocation_lat, hospitalLocation_long, altitude)

        send_live_location()
        calculate_delivery_time(hospitalLocation)

        arm_and_takeoff(altitude)
        advanced_goto(hospitalLocation)
        mode_land()
        send_live_location()

        while not db.child("Delivery").child("isDelivered").get().val():
            time.sleep(1)

        send_live_location()
        arm_and_takeoff(altitude)
        advanced_goto(homeLocation)
        mode_land()
        send_live_location()

        time.sleep(10)
        clear_firebase_data()
        break
