#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PointStamped
import time

rospy.init_node('clicked_point_publisher')

l = [(39.0, 39.0, 0.0), (-39.0, 39.0, 0.0), (-39.0, -39.0, 0.0), (39.0, -39.0, 0.0), (-8.16, 10.59, 0.0)]

pub = rospy.Publisher('/clicked_point', PointStamped, queue_size=10)

count = 0
time.sleep(1)
while not rospy.is_shutdown():
    if count == 5:
        #Shutdown the node
        rospy.signal_shutdown("The messages for the topic /clicked_point are published.")
    # Create the message
    msg = PointStamped()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = 'map'
    msg.point.x = l[count][0]
    msg.point.y = l[count][1]
    msg.point.z = 0.0

    # Publish the message
    pub.publish(msg)

    count += 1

