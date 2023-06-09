#!/usr/bin/env python3

#--------Include modules---------------
from copy import copy
import rospy
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from nav_msgs.msg import OccupancyGrid
import tf
from rrt_exploration.msg import PointArray
from time import time
from numpy import array
from numpy import linalg as LA
from numpy import all as All
from numpy import inf
from functions import robot,informationGain,discount, unvalid
from numpy.linalg import norm

# Subscribers' callbacks------------------------------
mapData=OccupancyGrid()
frontiers=[]
globalmaps=[]
unreachable = {}
centroids_dict = {}

def callBack(data):
	global frontiers
	frontiers=[]
	for point in data.points:
		frontiers.append(array([point.x,point.y]))

def mapCallBack(data):
    global mapData
    mapData=data
# Node----------------------------------------------

def node():
	global frontiers,mapData,globalmaps, unreachable, centroids_dict
	rospy.init_node('assigner', anonymous=False)
	
	first = True
	# fetching all parameters
	map_topic								= rospy.get_param('~map_topic','/map')
	info_radius							= rospy.get_param('~info_radius',1.0)					#this can be smaller than the laser scanner range, >> smaller >>less computation time>> too small is not good, info gain won't be accurate
	info_multiplier					= rospy.get_param('~info_multiplier',3.0)		
	hysteresis_radius				= rospy.get_param('~hysteresis_radius',3.0)			#at least as much as the laser scanner range
	hysteresis_gain					= rospy.get_param('~hysteresis_gain',2.0)				#bigger than 1 (biase robot to continue exploring current region
	frontiers_topic					= rospy.get_param('~frontiers_topic','/filtered_points')	
	delay_after_assignement	= rospy.get_param('~delay_after_assignement',0.5)
	rateHz 									= rospy.get_param('~rate',100)
	robot_namelist          = rospy.get_param('~robot_namelist', "robot1")
	max_time = rospy.get_param('~max_time',4)
	max_dist = rospy.get_param('~max_dist',1)
	rate = rospy.Rate(rateHz)
#-------------------------------------------
	rospy.Subscriber(map_topic, OccupancyGrid, mapCallBack)
	rospy.Subscriber(frontiers_topic, PointArray, callBack)
#---------------------------------------------------------------------------------------------------------------
	# perform name splitting for the robot
	robot_namelist = robot_namelist.split(',')
# wait if no frontier is received yet 
	while len(frontiers)<1:
		pass
	centroids=copy(frontiers)	
#wait if map is not received yet
	while (len(mapData.data)<1):
		pass

	robots=[]
	for i in range(0,len(robot_namelist)):
		robots.append(robot(name=robot_namelist[i]))

	for i in range(0,len(robot_namelist)):
		robots[i].sendGoal(robots[i].getPosition())
#-------------------------------------------------------------------------
#---------------------     Main   Loop     -------------------------------
#-------------------------------------------------------------------------
	while not rospy.is_shutdown():
		centroids=copy(frontiers)		
#-------------------------------------------------------------------------			
#Get information gain for each frontier point
		infoGain=[]
		for ip in range(0,len(centroids)):
			infoGain.append(informationGain(mapData,[centroids[ip][0],centroids[ip][1]],info_radius))
#-------------------------------------------------------------------------			
#get number of available/busy robots
		na=[] #available robots
		nb=[] #busy robots
		for i in range(0,len(robot_namelist)):
			if (robots[i].getState()==1):
				nb.append(i)
			else:
				na.append(i)	
		rospy.loginfo("available robots: "+str(na))	
#------------------------------------------------------------------------- 
#get dicount and update informationGain
		for i in nb+na:
			infoGain=discount(mapData,robots[i].assigned_point,centroids,infoGain,info_radius)

		for elem in centroids:
			pointStr = str(elem)
			if pointStr not in centroids_dict:
				centroids_dict[pointStr] = 0
#-------------------------------------------------------------------------            
		revenue_record=[]
		centroid_record=[]
		id_record=[]
		
		for ir in na:
			for ip in range(0,len(centroids)):
				cost=norm(robots[ir].getPosition()-centroids[ip])		
				threshold=1
				information_gain=infoGain[ip]
				if (norm(robots[ir].getPosition()-centroids[ip])<=hysteresis_radius):

					information_gain*=hysteresis_gain
				revenue=information_gain*info_multiplier-cost
				revenue_record.append(revenue)
				centroid_record.append(centroids[ip])
				id_record.append(ir)
		
		if len(na)<1:
			revenue_record=[]
			centroid_record=[]
			id_record=[]
			for ir in nb:
				for ip in range(0,len(centroids)):
					cost=norm(robots[ir].getPosition()-centroids[ip])		
					threshold=1
					information_gain=infoGain[ip]
					if (norm(robots[ir].getPosition()-centroids[ip])<=hysteresis_radius):
						information_gain*=hysteresis_gain
				
					if ((norm(centroids[ip]-robots[ir].assigned_point))<hysteresis_radius):
						information_gain=informationGain(mapData,[centroids[ip][0],centroids[ip][1]],info_radius)*hysteresis_gain

					revenue=information_gain*info_multiplier-cost
					revenue_record.append(revenue)
					centroid_record.append(centroids[ip])
					id_record.append(ir)
		
		rospy.loginfo("Posicion del rooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooot: "+str(robots[0].getPosition()))	
		rospy.loginfo("revenue record: "+str(revenue_record))	
		rospy.loginfo("centroid record: "+str(centroid_record))	
		# rospy.loginfo("robot IDs record: "+str(id_record))	
		
#-------------------------------------------------------------------------	
		if (len(id_record)>0):
			if not first:
				end = time()
				rospy.loginfo(previous_centroid + " pointaaaaaaaaa: " + str(end-start))
				robot_pos = robots[0].getPosition()
				target_p = robots[0].assigned_point
				robot_x = robot_pos[0]
				robot_y = robot_pos[1]
				dist = ((robot_x-target_p[0])**2 +(robot_y-target_p[1])**2)**0.5
				if dist <= max_dist:
					centroids_dict[previous_centroid] += (end-start) 
				if centroids_dict[previous_centroid] > max_time:
					unreachable[previous_centroid] = 0
			max = -1000000000
			
			for i in range(len(revenue_record)):
				if max<revenue_record[i] and str(centroid_record[i]) not in unreachable:
					winner_id = i
					max = revenue_record[i]
			start = time()
			first = False
			#winner_id=revenue_record.index(max(revenue_record))
			
			robots[id_record[winner_id]].sendGoal(centroid_record[winner_id])
			previous_centroid = str(centroid_record[winner_id])
			rospy.loginfo(robot_namelist[id_record[winner_id]] + "  assigned to  "+str(centroid_record[winner_id]))	
			rospy.loginfo("Unreachable: " + str(unreachable))
			rospy.loginfo(str(centroid_record[winner_id]) + " point: " + str(centroids_dict[str(centroid_record[winner_id])]))
			#rospy.loginfo("Probatzen hauuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu: " , str(mapData.data))
			rospy.sleep(delay_after_assignement)
		else:
			previous_centroid = 0
			first = True
#------------------------------------------------------------------------- 
		rate.sleep()
#-------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        node()
    except rospy.ROSInterruptException:
        pass
 
 
 
 
