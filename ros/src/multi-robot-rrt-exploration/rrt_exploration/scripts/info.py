#!/usr/bin/env python3

import rospy
import pandas as pd
#import matplotlib.pyplot as plt
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import PoseStamped
import time
import subprocess
import os
import pickle as pc

count_changed_cells = 0
robot_positions = []

#global run_time, max_changed_cells
count_time = 0
start_time = time.time()

def callback_gridmap(msg2):
    global mapData
    mapData = msg2

def callback_pose(odomMsg):
    global msg
    msg = odomMsg

def timer_callback_gridmap(event):
    rospy.loginfo("Recogiendo datos del gridmap...")

    global count_changed_cells

    gridmap = mapData.data
    count_changed_cells = 0
    rospy.loginfo("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    for cell in gridmap:
        #print(cell)
        if cell != -1:
            count_changed_cells += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    rospy.loginfo("Se han cambiado {} celdas del mapa. Tiempo de ejecución: {} segundos.".format(count_changed_cells, elapsed_time))

    if count_changed_cells >= max_changed_cells or elapsed_time >= run_time:
        end_time = time.time()
        elapsed_time = end_time - start_time
        rospy.loginfo("Se han cambiado {} celdas del mapa. Tiempo de ejecución: {} segundos. Terminando ejecución...".format(count_changed_cells, elapsed_time))



        #Save the map
        command = 'rosrun map_server map_saver -f ' + filename2
        os.system(command)

        #Load the data
        f = open(filename, 'rb')
        my_data = pc.load(f)
        f.close()

        my_data['robot_positions'] = robot_positions
        my_data['time'] = elapsed_time
        my_data['changed_cells'] = count_changed_cells
        if count_changed_cells >= max_changed_cells:
            my_data['completed'] = True
        else:
            my_data['completed'] = False

        #Write new data
        f = open(filename, 'wb')
        pc.dump(my_data, f)
        f.close()

        

        time.sleep(2)

        #subprocess.run(['rosnode', 'kill', '-a'])
        os.system('rosnode kill -a')
        # Detener la ejecución del nodo
        #rospy.signal_shutdown("Se han cambiado {} celdas del mapa".format(count_changed_cells))

    

def timer_callback_pose(event):
    global count_time, count_changed_cells

    x = msg.pose.pose.position.x
    y = msg.pose.pose.position.y
    z = msg.pose.pose.position.z
    # Añadir la posición a la lista de posiciones del robot
    robot_positions.append((x, y, z))
    count_time += 1
    rospy.loginfo("counted_time: %s, timer: %s", count_time, time.time() - start_time )
    rospy.loginfo("count_changed_cells: %s", count_changed_cells)
    rospy.loginfo("robot positiooooooooooooooooooooooooooooooooooon: x=%s, y=%s, z=%s", x, y, z )
    elapsed_time = time.time() - start_time
    # Terminar la ejecución del nodo después de `run_time` segundos
    # if elapsed_time >= run_time:
    #     gridmap = mapData.data
    #     count_changed_cells = 0
    #     for cell in gridmap:
    #         #print(cell)
    #         if cell != -1:
    #             count_changed_cells += 1
    #     rospy.loginfo("Se ha superado el tiempo máximo de ejecución de {} segundos. Terminando ejecución...".format(run_time))
    #     #Save the map
    #     command = 'rosrun map_server map_saver -f ' + filename2
    #     os.system(command)

    #     #Load the data
    #     f = open(filename, 'rb')
    #     my_data = pc.load(f)
    #     f.close()

    #     my_data['robot_positions'] = robot_positions
    #     my_data['time'] = elapsed_time
    #     my_data['changed_cells'] = count_changed_cells
    #     my_data['completed'] = False

    #     #Write new data
    #     f = open(filename, 'wb')
    #     pc.dump(my_data, f)
    #     f.close()
    #     # Detener la ejecución del nodo
    #     #subprocess.run(['rosnode', 'kill', '-a'])
    #     os.system('rosnode kill -a')
    #     rospy.signal_shutdown("Se ha superado el tiempo máximo de ejecución")

# Obtener los parámetros del nodo


rospy.init_node('info')
max_changed_cells = rospy.get_param('~max_changed_cells', 190000)
run_time = rospy.get_param('~run_time', 900)
filename = rospy.get_param('~filename')
filename2 = rospy.get_param('~filename2')
rospy.loginfo("Mac run timeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee:"+str(run_time))
# Suscribirse al tópico del mapa
rospy.Subscriber('/map', OccupancyGrid, callback_gridmap)
rospy.Timer(rospy.Duration(10), timer_callback_gridmap)
rospy.Subscriber('/odom', Odometry, callback_pose)
rospy.Timer(rospy.Duration(1), timer_callback_pose)

rospy.spin()
# while not rospy.is_shutdown():
#     pass


