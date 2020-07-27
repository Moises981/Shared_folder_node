#! /usr/bin/env python
import numpy as np
import pandas as pd
import rospy
import os


rospy.init_node('CSV')
rate = rospy.Rate(0.25)

while not rospy.is_shutdown():
    data = np.random.rand(30000,3)
    DF  = pd.DataFrame({'x':data[:,0],'y':data[:,1],'z':data[:,2]})
    DF.to_csv('~/Desktop/Catkin_ws/src/shared_folders/Backup/Data.csv')
    os.popen('cp ~/Desktop/Catkin_ws/src/shared_folders/obj_files/05_27_d8_meshio.obj  ~/Desktop/Catkin_ws/src/shared_folders/Backup/3D.obj')
    print 'Send'
    rate.sleep()
