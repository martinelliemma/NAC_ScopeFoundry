'''
Neo Andor Camera Hardware
*******************
@authors: Emma Martinelli, Andrea Bassi. Politecnico di Milano

'''
from mimetypes import inited

from ScopeFoundry import HardwareComponent
#from NAC_device import NeoAndorDevice                          # for NAC_app
from Andor_ScopeFoundry.NAC_device import NeoAndorDevice        # for SPIM_app

class NeoAndorHW(HardwareComponent):
    name='NeoAndorHW'
    
    def setup(self):   
        self.infos = self.settings.New(name='name', dtype=str)
        self.cooler=self.settings.New(name='cooler',dtype=str, choices=['True', 'False'], initial = 'True', ro=False)
        self.temperature = self.settings.New(name='temperature', dtype=float, ro=True, unit=chr(176)+'C' )
        self.dynamic_range= self.settings.New(name='dynamic_range', dtype=str, choices=['16 bit', '11 bit (low noise)', '11 bit (high well capacity)'],
                                              initial = '11 bit (low noise)', ro=False, reread_from_hardware_after_write=True)
        self.exposure_time = self.settings.New(name='exposure_time', vmax=50, initial=0.05,
                                               vmin=0, spinbox_step=0.01, dtype=float, ro=False, unit='s',
                                               reread_from_hardware_after_write=True)
        self.readout_rate = self.settings.New(name='Pixel readout rate', dtype=str, choices=['200 MHz', '560 Mhz'],
                                              initial='560 MKz', ro=False)
        self.overlap = self.settings.New(name='overlap', dtype=str, choices=['True', 'False'], initial='True', ro=False)
        self.frame_rate = self.settings.New(name='Frame rate', dtype=float, ro=True, unit='Hz')
        self.frame_num = self.settings.New(name='frame_num',initial= 10, spinbox_step = 1,
                                           dtype=int, ro=False)

        self.trigger = self.settings.New(name='trigger', dtype=str, choices=['int', 'ext'], initial = 'int', ro=False)
        
        self.image_width = self.settings.New(name='image_width', dtype=int, ro=True,unit='px')
        self.image_height = self.settings.New(name='image_height', dtype=int, ro=True,unit='px')


    def connect(self):
        # create an instance of the Device
        self.camera = NeoAndorDevice()      
        
        # connect settings to Device methods
        self.temperature.hardware_read_func = self.camera.temperature
        self.frame_rate.hardware_read_func = self.camera.frame_rate
        self.infos.hardware_read_func = self.camera.camera_info
        self.cooler.hardware_set_func = self.camera.cooler_set
        self.cooler.hardware_read_func= self.camera.cooler_check

        self.dynamic_range.hardware_set_func=self.camera.dynamic_range

        self.exposure_time.hardware_set_func = self.camera.exposure_set
        self.exposure_time.hardware_read_func = self.camera.exposure_get

        self.trigger.hardware_read_func = self.camera.trigger_get
        self.trigger.hardware_set_func = self.camera.trigger_set

        self.image_width.hardware_read_func = self.camera.camera_width
        self.image_height.hardware_read_func = self.camera.camera_height
        
        self.read_from_hardware()
        
    def disconnect(self):
        if hasattr(self, 'camera'):
            self.camera.close() 
            del self.camera
            
        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None


