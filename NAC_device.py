'''
Neo Andor Camera Device
for more infos: 
https://pylablib.readthedocs.io/en/stable/.apidoc/pylablib.devices.Andor.html#pylablib.devices.Andor.AndorSDK3.AndorSDK3Camera.get_all_attributes
*******************
@authors: Emma Martinelli, Andrea Bassi. Politecnico di Milano

'''
import numpy as np
import pylablib as pll
from pylablib.devices import Andor
import matplotlib.pyplot as plt


class NeoAndorDevice(object):
    def __init__(self):
        self.cam = Andor.AndorSDK3Camera(idx=0)

    #acquisition mode
    def acquisition_setup(self,nf):
        self.cam.setup_acquisition(mode='sequence',nframes=nf)
    def acquisition_clear(self):
        self.cam.clear_acquisition()
    def acquisition_start(self):
        self.cam.start_acquisition()
    def acquisition_progress(self):
        return self.cam.acquisition_in_progress()
    def acquisition_stop(self):
        self.cam.stop_acquisition()

    #images
    def image_read(self):
        return self.cam.read_oldest_image()
    def image_wait(self):
        self.cam.wait_for_frame(since="now", nframes=1, timeout=None)
    def image_snap(self):
        return self.cam.snap()

    #close the camera
    def close(self):
        self.cam.close()

    #sensitivity/dynamic range
    def dynamic_range(self,mode):
        if '16 bit' in mode:
            self.cam.set_attribute_value('SimplePreAmpGainControl', 2)
        if '11 bit (low noise)' in mode:
            self.cam.set_attribute_value('SimplePreAmpGainControl', 1)
        if '11 bit (high well capacity)' in mode:
            self.cam.set_attribute_value('SimplePreAmpGainControl', 0)

    def readout_rate(self,mode):
        if '200 MHz' in mode:
            self.cam.set_attribute_value('PixelReadoutRate', 2)
        if '560 MHz' in mode:
            self.cam.set_attribute_value('PixelReadoutRate', 3)

    def overlap(self, mode):
        self.cam.set_attribute_value('Overlap', mode)

    def frame_rate(self):
        return self.cam.get_attribute_value('FrameRate')

    #read temperature
    def temperature(self):
        return self.cam.get_temperature()

    #cooling on or off
    def cooler_check(self):
        return self.cam.is_cooler_on()
    def cooler_set(self, on):
        self.cam.set_cooler(on)

    #ROI width&height
    def roi_get(self):
        return self.cam.get_roi()
    def roi_set(self,hstart,hend,vstart,vend,hbin,vbin):
        self.cam.set_roi(hstart,hend,vstart,vend,hbin,vbin)

    def exposure_get(self):
        return self.cam.get_exposure()
    def exposure_set(self, exp):
        self.cam.set_exposure(exp)

    #get the acquisition frame rate (min e max)
    def frame_time(self):
        return self.cam.get_frame_timings()

    #camera info
    def camera_info(self):
        return self.cam.get_device_info()

    def image_size(self):
        hstart, hend, vstart, vend, hbin, vbin = self.roi_get()
        width = (hend - hstart) // hbin
        height = (vend - vstart) // vbin
        return (width, height)

    def detector_size(self):
        return self.cam.get_detector_size()

    #trigger
    def trigger_get(self):
        return self.cam.get_trigger_mode()
    def trigger_set(self,mode):
        self.cam.set_trigger_mode(mode)

if __name__ == '__main__':

    try:    
        camera = NeoAndorDevice()
        camera.acquisition_clear()
        print('Cooler On?:', camera.cooler_check())
        camera.dynamic_range('16 bit')
        
        camera.acquisition_setup(1)
        camera.acquisition_start()
        camera.image_wait()
        frame=camera.image_read()
        #print('Acquired image shape:',frame.shape)
        #frame=camera.image_snap()

        plt.imshow(frame)
        plt.show()
    except Exception as err:
        print(err)
    
    finally:
        camera.close()