"""
https://jeffzzq.medium.com/ros2-image-pipeline-tutorial-3b18903e7329
This node publishes the camera feed topic /image_raw

Camera specs: 
width: 1280
height: 720
30fps

ABS
Length Approx.6cm 2.36in
Pixel 1million pixels
Photosensitive chip: OV9726(1/6.5“)
Field of view: 63°No Distortion
Output:USB2.0

TODO: remember to change the camera input channel
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('usbcamera_publisher')
        
        # Open the USB camera using a mode supported by the device.
        self.image_pub = self.create_publisher(Image, '/stinger/camera_0/image_raw', 10) # queue size 10
        self.timer = self.create_timer(1.0 / 30.0, self.publish_image)
        self.cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.br = CvBridge()

        if not self.cap.isOpened():
            self.get_logger().error("Could not open video device.")
            return

        self.get_logger().info(
            "Opened /dev/video0 at "
            f"{int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
            f"{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))} @ "
            f"{self.cap.get(cv2.CAP_PROP_FPS):.1f} fps"
        )

    def publish_image(self):
        ret, frame = self.cap.read() # capture a frame from the usb cam
        if ret and frame is not None: # is captured successfully
            # Publish the image frame
            self.image_pub.publish(self.br.cv2_to_imgmsg(frame, 'bgr8'))
        else:
            self.get_logger().error("Failed to capture image.")

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    camera_publisher = CameraPublisher()
    rclpy.spin(camera_publisher)
    camera_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
