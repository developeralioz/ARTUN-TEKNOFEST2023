from dronekit import connect, VehicleMode, LocationGlobalRelative, Locations
import time
import math
from firebase import db
from pymavlink import mavutil
from datetime import datetime, timedelta

connection_string = "tcp:10.211.55.6:5762"
print("Connecting to vehicle on: ", connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(targetAltitude):
    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(targetAltitude)  # Take off to target altitude
    """
    Wait until the vehicle reaches a safe height before processing the goto
    (otherwise the command after Vehicle.simple_takeoff will execute immediately).
    """
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= targetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def advanced_goto(aLocation):
    vehicle.simple_goto(aLocation)
    while True:
        currentLocation = get_current_location()
        distance = get_distance_metres(currentLocation, aLocation)
        send_live_location()
        if distance <= 2:
            break
        time.sleep(0.1)
    time.sleep(1)


def wait_until_armable():
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)


def send_live_location():
    liveLocation = get_current_location()
    live_location_lat = liveLocation.lat
    live_location_long = liveLocation.lon

    db.child("Live").update({"live_location_lat": live_location_lat})
    db.child("Live").update({"live_location_long": live_location_long})


def clear_firebase_data():
    db.child("HospitalLocation").update({"hospitalLocation_lat": 0})
    db.child("HospitalLocation").update({"hospitalLocation_long": 0})
    db.child("Live").update({"live_location_lat": 0})
    db.child("Live").update({"live_location_long": 0})
    db.child("Delivery").update({"estimated_delivery_time": "0"})
    db.child("Delivery").update({"isDelivered": False})


def mode_land():
    vehicle.mode = "LAND"
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt <= 1:
            print("Reached target altitude")
            break
        time.sleep(1)


def calculate_delivery_time(aLocation):
    x = get_distance_metres(get_current_location(), aLocation)
    v = 5
    t = int(x / v)

    print(datetime.now().strftime("%H:%M"))
    calculated_delivery_time = datetime.now() + timedelta(minutes=1, seconds=t)
    print(calculated_delivery_time.strftime("%H:%M"))
    calculated_delivery_time_formatted = calculated_delivery_time.strftime("%H:%M")

    db.child("Delivery").update({"estimated_delivery_time": calculated_delivery_time_formatted})


def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat * dlat) + (dlong * dlong)) * 1.113195e5


def get_current_location():
    return vehicle.location.global_relative_frame
