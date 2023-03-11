from openni import openni2 
from openni import _openni2 as c_api 
import sys, cv2
import numpy as np 

class Astra():
    def __init__(self, sensors, resolution):
        self.width, self.height = resolution
        self.fps = 30
        
        if ("color" in sensors) and ("ir" in sensors):
            print("[ERROR] cannot initiate color and ir sensors at the same time...")
            sys.exit()
        
        print("[INFO] initializing openni...")    
        openni2.initialize()
        
        print("[INFO] opening devices...") 
        devs = openni2.Device.open_all()
        
        if "depth" in sensors: self.depth_streams = []
        if "color" in sensors: self.color_streams = []
        if "ir" in sensors: self.ir_streams = []
        
        for idx, dev in enumerate(devs):
            # pixelFormat can also be "ONI_PIXEL_FORMAT_DEPTH_1_MM"
            if "depth" in sensors:
                print("[INFO] creating depth stream for camera {}...".format(
                    idx
                ))
                self.depth_streams.append(dev.create_depth_stream())
                self.depth_streams[idx].set_video_mode(
                    c_api.OniVideoMode(
                        pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM, 
                        resolutionX = self.width, 
                        resolutionY = self.height, 
                        fps = self.fps, 
                    )
                )
                self.depth_streams[idx].start() 
                
            if "ir" in sensors:
                print("[INFO] creating ir stream for camera {}...".format(
                    idx
                ))
                self.ir_streams.append(dev.create_ir_stream())
                self.ir_streams[idx].set_video_mode(
                    c_api.OniVideoMode(
                        pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_GRAY16,
                        resolutionX = self.width, 
                        resolutionY = self.height, 
                        fps = self.fps, 
                    )
                )
                self.ir_streams[idx].start()
                
            if "color" in sensors:
                print("[INFO] creating color stream for camera {}...".format(
                    idx
                ))
                self.color_streams.append(dev.create_color_stream())
                self.color_streams[idx].set_video_mode(
                    c_api.OniVideoMode(
                        pixelFormat = c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, 
                        resolutionX = self.width, 
                        resolutionY = self.height, 
                        fps = self.fps, 
                    )
                )
                self.color_streams[idx].start()
                
            if ("color" in sensors) and ("depth" in sensors):
                print("[INFO] synchronizong color and depth sensors for camera {}...".format(
                    idx
                ))
                devs[idx].set_image_registration_mode(openni2.IMAGE_REGISTRATION_DEPTH_TO_COLOR)
                devs[idx].set_depth_color_sync_enabled(True)
                
        self.devs = devs
        self.sensors = sensors
        
    def _destroy(self):
        for idx, dev in enumerate(self.devs):
            print("[INFO] closing camera {}...".format(
                idx
            ))
            
            if "depth" in self.sensors: self.depth_streams[idx].stop()
            if "color" in self.sensors: self.color_streams[idx].stop()
            if "ir" in self.sensors: self.ir_streams[idx].stop()
            
        openni2.unload()
        
    def _get_depth_frame(self, idx):
        frame = self.depth_streams[idx].read_frame()
        frame_data = frame.get_buffer_as_uint16()
        img = np.frombuffer(frame_data, dtype=np.uint16) 
        img.shape = (self.height, self.width)
        img = cv2.medianBlur(img, 3)
        img = cv2.flip(img, 1)
        
        return img
    
    def _get_ir_frame(self, idx):
        frame = self.ir_streams[idx].read_frame()
        frame_data = frame.get_buffer_as_uint16()
        img = np.frombuffer(frame_data, dtype=np.uint16) 
        img.shape = (self.height, self.width)
        img = np.multiply(img, int(65535/1023))
        img = cv2.GaussianBlur(img, (5,5), 0)
        img = cv2.flip(img, 1)
        
        return img
    
    def _get_color_frame(self, idx):
        frame = self.color_streams[idx].read_frame()
        frame_data = frame.get_buffer_as_uint8()
        img = np.frombuffer(frame_data, dtype=np.uint8) 
        img.shape = (self.height, self.width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.flip(img, 1)
        
        return img