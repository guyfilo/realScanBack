import pyrealsense2 as rs
import cv2
import numpy as np
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path
import time

class Camera:

    def __init__(self):
        self.pipe = None
        self.ready = False
        self.frames = None
        self.profile = None
        self.recorder = None
        self.record_status = 0

    def init_pipes(self, fileName):

        ctx = rs.context()
        if len(ctx.devices) == 0:
            return -1
        try:
            # Declare pointcloud object, for calculating pointclouds and texture mappings
            pc = rs.pointcloud()
            # We want the points object to be persistent so we can display the last cloud when a frame drops
            points = rs.points()

            # Declare RealSense pipeline, encapsulating the actual device and sensors
            pipe = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)
            config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
            config.enable_record_to_file(fileName)
            # Enable depth stream
            config.enable_stream(rs.stream.depth)

            # Start streaming with chosen configuration
            self.profile = pipe.start(config)
            self.recorder = self.profile.get_device().as_recorder()
            self.recorder.pause()

        except:
            return -1
        self.ready = True
        self.pipe = pipe
        return 0

    def update_frames(self):
        try:
            self.frames = self.pipe.wait_for_frames()
            return 0
        except:
            self.ready = False
            self.pipe = None
            self.frames = None
            cv2.destroyAllWindows()
            return -1

    def record_start(self):
        self.recorder.resume()
        self.record_status = 1

    def record_stop(self):
        self.recorder.pause()
        self.record_status = 0


    def frames_to_ply(self, frames_num, path):
        # We'll use the colorizer to generate texture for our PLY
        # (alternatively, texture can be obtained from color or infrared stream)

        try:

            saver = rs.save_single_frameset(path + "/" + str(frames_num) + "_")
            saver.process(self.frames)

        except:
            return -1


    def distance(self):
        if self.ready:
            depth = self.frames.get_depth_frame()
            if not depth:
                return
            width = depth.get_width()
            height = depth.get_height()
            dist_to_center = depth.get_distance(int(width / 2), int(height / 2))
            return dist_to_center
        return 0

    def close_pipe(self):
        if not self.ready:
            return -1
        self.pipe.stop()
        self.pipe = None
        self.frames = None
        self.ready = False
        cv2.destroyAllWindows()

    def display(self):
        # Wait for a coherent pair of frames: depth and color
        depth_frame = self.frames.get_depth_frame()
        color_frame = self.frames.get_color_frame()
        if not depth_frame or not color_frame:
            return

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Stack both images horizontally
        #images = np.hstack((color_image, depth_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_NORMAL)
        cv2.imshow('RealSense', color_image)
        cv2.waitKey(1)

    def show_image(self, path):
        # Create object for parsing command-line options
        parser = argparse.ArgumentParser(description="Read recorded bag file and display depth stream in jet colormap.\
                                        Remember to change the stream resolution, fps and format to match the recorded.")
        # Add argument which takes path to a bag file as an input
        parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
        # Parse the command line arguments to an object
        args = path
        """# Safety if no parameter have been given
        if not args.input:
            print("No input paramater have been given.")
            print("For help type --help")
            exit()
        # Check if the given file have bag extension"""
        """if os.path.splitext(args)[1] != ".bag":
            print("The given file is not of correct file format.")
            print("Only .bag files are accepted")
            exit()"""
        try:
            # Create pipeline
            pipeline = rs.pipeline()

            # Create a config object
            config = rs.config()
            # Tell config that we will use a recorded device from filem to be used by the pipeline through playback.
            rs.config.enable_device_from_file(config, args)
            # Configure the pipeline to stream the depth stream
            config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

            # Start streaming from file
            pipeline.start(config)

            # Create opencv window to render image in
            cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)

            # Create colorizer object
            colorizer = rs.colorizer();

            # Streaming loop
            while True:
                # Get frameset of depth
                frames = pipeline.wait_for_frames()

                # Get depth frame
                depth_frame = frames.get_depth_frame()

                # Colorize depth frame to jet colormap
                depth_color_frame = colorizer.colorize(depth_frame)

                # Convert depth_frame to numpy array to render image in opencv
                depth_color_image = np.asanyarray(depth_color_frame.get_data())

                # Render image in opencv window
                cv2.imshow("Depth Stream", depth_color_image)
                key = cv2.waitKey(1)
                # if pressed escape exit program
                if key == 27:
                    cv2.destroyAllWindows()
                    break

        finally:
            pass

if __name__ == '__main__':
    c = Camera()
    c.show_image("Patient_2/2020-10-01_1/1.bag516.bag")

