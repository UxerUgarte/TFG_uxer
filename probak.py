#!/usr/bin/env python
import subprocess
import os
import multiprocessing
import time
import rospy
from geometry_msgs.msg import PointStamped

def launch(command):
    os.system(command)




# def publish_clicked_point(x, y, z):
#     command = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: %f
#   y: %f
#   z: 0.0" 
# """ % (x, y)

#     os.system(command)

def publish_clicked_point2(x, y, z):
    # Crear un nuevo mensaje
    msg = PointStamped()
    msg.header.stamp = rospy.Time.now()
    msg.header.frame_id = 'map'
    msg.point.x = x
    msg.point.y = y
    msg.point.z = z

    # Publicar el mensaje
    pub.publish(msg)

rospy.init_node('clicked_point_publisher', anonymous=True)

pub = rospy.Publisher('/clicked_point', PointStamped, queue_size=10)
    



# point1 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: %s
#   y: %s
#   z: 0.0" 
# """

if __name__ == "__main__":
    # subprocess.run(['roslaunch', 'ros_multi_tb3', 'single_tb2_house_teb_third_floor.launch'])
    # subprocess.run(['roslaunch', 'rrt_exploration', 'turtlebot_exploration.launch'])
#     point1 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: 39.0
#   y: 39.0
#   z: 0.0" 
# """
#     point2 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: -39.0
#   y: 39.0
#   z: 0.0" 
# """
#     point3 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: -39.0
#   y: -39.0
#   z: 0.0" 
# """
#     point4 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: 39.0
#   y: -39.0
#   z: 0.0" 
# """
#     point5 = """rostopic pub /clicked_point geometry_msgs/PointStamped "header:
#   seq: 0
#   stamp:
#     secs: 0
#     nsecs: 0
#   frame_id: 'map'
# point:
#   x: -8.16
#   y: 10.59
#   z: 0.0" 
# """
    launch1 = 'roslaunch ros_multi_tb3 single_tb2_house_teb_third_floor.launch'
    launch2 = 'roslaunch rrt_exploration turtlebot_exploration.launch'
    p1 = multiprocessing.Process(target=launch, args = (launch1,))
    
    p2 = multiprocessing.Process(target=launch, args = (launch2,))
    p1.start()
    time.sleep(10)
    p2.start()
    time.sleep(10)
    print("no para")
    # os.system('roslaunch ros_multi_tb3 single_tb2_house_teb_third_floor.launch')
    # os.system('roslaunch rrt_exploration turtlebot_exploration.launch')
    print("no para")
    
    # os.system(point1)
    # os.system(point2)
    # os.system(point3)
    # os.system(point4)
    # os.system(point5)#-8.16 x, 10.59 y
    # publish_clicked_point(39.0, 39.0, 0.0)
    # publish_clicked_point(-39.0, 39.0, 0.0)
    # publish_clicked_point(-39.0, -39.0, 0.0)
    # publish_clicked_point(39.0, -39.0, 0.0)
    # publish_clicked_point(-8.16, 10.59, 0.0)

    p1.join()
    p2.join()
    for i in range(10000):
        print(i)