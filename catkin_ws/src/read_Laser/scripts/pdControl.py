#!/usr/bin/env python


# Set kp, kd to use a PD controller
# Subscribes to wall_error topic, gets angle error and velocity error
# Corrects angle and velocity input with error term
# Publishes velocity and angle in drive_param msg to drive_parameters topic

import rospy
import numpy as np
import math
from race.msg import drive_param
from race.msg import pid_input

# PD controller gains, velocity
kp = 5
kd = .25
prevError = 0
angleOffset = 18.0 * np.pi/180
angleUpperLimit = 30 * np.pi/180
angleLowerLimit = -30 * np.pi/180

# Publish angle/velocity inputs after accounting for error
commandPub = rospy.Publisher('drive_parameters', drive_param, queue_size = 1)



# Callback for subscriber, takes error as input, publishes velocity and steering angle
def controller(feedback):
    global kp, kd, commandPub, prevError
	
	# Error is proportionalGain*error + derivativeGain * difference
    error = kp*feedback.pid_error + kd*(prevError - feedback.pid_error)
    
    # Corrected angle
    angleCorrected = angleOffset + error*np.pi/180
    
    # Apply angle upper/lower limits
    if angleCorrected > angleUpperLimit:
        angleCorrected = angleUpperLimit
        
    if angleCorrected < angleLowerLimit:
        angleCorrected = angleLowerLimit
    
    
    # Set velocity based on angle. When turning we want to go slower
    # Full speed ahead if angle less than 1
    if abs(angleCorrected) < 1:
        velocity = 3.5
    
    # Go slow if turning angle more than 10
    if abs(angleCorrected) > 10:
        velocity = .75
    
    # Go Super slow if turning angle more than 20
    if abs(angleCorrected) > 20:
        velocity = .3
	 
        
    # Apply velocity bounds if for some reason our velocity is messed up
    if velocity < 0:
        velocity = 1
    
    if velocity > 3.5:
        velocity = 3.5
        
    
    # Set and publish a drive_param message
    msg = drive_param()
    msg.angle = angleCorrected
    msg.velocity = velocity
    commandPub.publish(msg)


# Set up node and subscriber for pd controller
def pdControl():
	# Initiate node, subscriber
	rospy.init_node('pdControl', anonymous = True)
	rospy.Subscriber("wall_error", pid_input, controller) # error will be on wall_error topic
	rospy.spin()


if __name__ == '__main__':
	pdControl()












