#!/usr/bin/env python

import cv2
import rospy
import numpy as np
from sensor_msgs.msg import Image 
from std_msgs.msg import Float32
from std_msgs.msg import Float32MultiArray
from cv_bridge import CvBridge

class Image_processor:

    def __init__(self):

        self.bridge = CvBridge()

        self.image_raw = None

        self.CM = Float32MultiArray()
        self.density = Float32()

        self.xlimit = 1280

        self.ylimit = 720

        self.erode = None

        self.dt = 0.1

        rospy.init_node('Image_processor')

        rospy.Subscriber('/video_source/raw', Image, self.img_callback)
        
        self.mask_pub = rospy.Publisher('/img_properties/color/msk', Image, queue_size=10)
        self.density_pub = rospy.Publisher('/img_properties/color/density', Float32, queue_size=10)
        self.xy_pub = rospy.Publisher('/img_properties/color/xy',Float32MultiArray , queue_size=10)

        self.rate = rospy.Rate(10)
        # rospy.on_shutdown(self.stop)

        self.t1 = rospy.Timer(rospy.Duration(self.dt), self.timer_callback)


    def timer_callback(self, time):
        self.color_msk()

        self.color_density()

        self.color_xy()

    def img_callback(self,msg):
        self.image_raw = self.bridge.imgmsg_to_cv2(msg, "passthrough")
        
        # cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='CV_8UC3')

    def color_msk(self):
        hsv = cv2.cvtColor(self.image_raw, cv2.COLOR_BGR2HSV)
        #maskr = cv2.inRange(hsv, (170, 70, 70), (180, 255,255))
        #maskg = cv2.inRange(hsv, (36, 40, 40), (86, 255,255))
        #maskb = cv2.inRange(hsv, (94, 80, 2), (126, 255,255))
        #maskw = cv2.inRange(hsv, (0, 0, 195), (180, 60,255))
        masky = cv2.inRange(hsv, (15, 100, 100), (30, 255,255))

	#Cambiar mascara de acuerdo al color buscado
        dilate = cv2.dilate(masky, (5, 5), iterations = 6)

        self.erode = cv2.erode(dilate, (5, 5),iterations = 6)



        
    #720
        self.mask_pub.publish(self.bridge.cv2_to_imgmsg(cv2.bitwise_not(self.erode)))
    

    def color_density(self):
        
        den = np.sum(self.erode)/(self.xlimit*self.ylimit*255)

        self.density_pub.publish(den)
        

    def color_xy(self):
        msg = Float32MultiArray()
        M = cv2.moments(self.erode)
        
        msg.data = cen = [int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])] if M["m00"] != 0 else [int(self.xlimit/2), int(self.ylimit/2)]
        
        self.xy_pub.publish(msg)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    img_p = Image_processor()
    try:
        img_p.run()
    except:
        pass


			




