# -*- coding: utf-8 -*-

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative


# Set up option parsing to get connection string
connection_string = '/dev/ttyACM0'
# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)


def arm_and_takeoff(aTargetAltitude):
    
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto
    #  (otherwise the command after Vehicle.simple_takeoff will execute
    #   immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        # Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt >= aTargetAltitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)


def move_to_designated_point(point):
    print("Moving to designated point")
    vehicle.simple_goto(point)
    while True:
        distance = vehicle.location.global_frame.distance_to(point)
        print('Distance to target: ', distance)
        if distance < 1:  # Adjust the threshold as needed
            print("Reached designated point")
            break
        time.sleep(1)


def land_in_designated_point():
    print("Landing in designated point")
    vehicle.mode = VehicleMode("LAND")
    while vehicle.armed:
        print("Waiting to land...")
        time.sleep(1)


def drop_parcel():
    # Assuming servo is connected to channel 7
    # Send servo command to release parcel
    vehicle.channels.overrides['7'] = 1900  # Adjust servo PWM value as needed
    time.sleep(2)  # Allow time for the parcel to drop
    vehicle.channels.overrides['7'] = None  # Release the servo control


# Main execution
try:
    arm_and_takeoff(5)

    # Move to a designated point
    point1 = LocationGlobalRelative(13.011654, 77.705102, 5)
    move_to_designated_point(point1)

    # Land in the designated point
    land_in_designated_point()

    # Drop the parcel
    drop_parcel()

    # Take off again
    arm_and_takeoff(5)

    # Return to the initial takeoff location
    initial_takeoff_location = vehicle.home_location
    move_to_designated_point(initial_takeoff_location)

    # Land at the initial takeoff location
    land_in_designated_point()

except KeyboardInterrupt:
    print("Keyboard Interrupt detected. Landing the drone.")
    vehicle.mode = VehicleMode("LAND")
    vehicle.close()
