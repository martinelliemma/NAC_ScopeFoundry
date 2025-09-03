'''
Neo Andor Camera Hardware
*******************
@authors: Emma Martinelli, Andrea Bassi. Politecnico di Milano

'''
from mimetypes import inited

from ScopeFoundry import HardwareComponent
from NAC_device import NeoAndorDevice                          # for NAC_app
# from NAC_ScopeFoundry.NAC_device import NeoAndorDevice        # for SPIM_app

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

        # self.roi = self.settings.New(name='ROI', dtype=str, choices=['full', 'define'], initial = 'full', ro=False)
        self.roi_hstart = self.settings.New(name='roi_hstart', initial= 0, spinbox_step = 1, dtype=int, ro=False,
                                            unit='px', reread_from_hardware_after_write=True)
        self.roi_hend = self.settings.New(name='roi_hend', initial= 2560, spinbox_step = 1, dtype=int, ro=False,
                                            unit='px', reread_from_hardware_after_write=True)
        self.roi_vstart = self.settings.New(name='roi_vstart', initial= 0, spinbox_step = 1, dtype=int, ro=False,
                                            unit='px', reread_from_hardware_after_write=True)
        self.roi_vend = self.settings.New(name='roi_vend', initial= 2160, spinbox_step = 1, dtype=int, ro=False,
                                            unit='px', reread_from_hardware_after_write=True)
        self.hbin = self.settings.New(name='hbin', initial= 1, spinbox_step = 1, dtype=int, ro=False,
                                            reread_from_hardware_after_write=True)
        self.vbin = self.settings.New(name='vbin', initial= 1, spinbox_step = 1, dtype=int, ro=False,
                                            reread_from_hardware_after_write=True)

        self.image_size = self.settings.New(name='image_size', dtype=str, ro=True,unit='px')
        self.detector_size = self.settings.New(name='detector_size', dtype=str, ro=True,unit='px')


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

        self.trigger.hardware_set_func = self.camera.trigger_set
        self.trigger.hardware_read_func = self.camera.trigger_get

        # LQ tuple per comodità
        lqs = (self.roi_hstart, self.roi_hend, self.roi_vstart,
               self.roi_vend, self.hbin, self.vbin)

        # Funzione di set unica
        def _apply_roi(_=None):
            vals = tuple(int(lq.val) for lq in lqs)
            self.camera.roi_set(*vals)
            for lq, rv in zip(lqs, self.camera.roi_get()):
                lq.update_value(rv)
            return True

        # Set/read in un colpo
        for i, lq in enumerate(lqs):
            lq.hardware_set_func = _apply_roi
            lq.hardware_read_func = lambda idx=i: self.camera.roi_get()[idx]

        # Applica ROI iniziale
        _apply_roi()

        self.image_size.hardware_read_func = self.camera.image_size
        self.detector_size.hardware_read_func = self.camera.detector_size
        
        self.read_from_hardware()
        
    def disconnect(self):
        if hasattr(self, 'camera'):
            self.camera.close() 
            del self.camera
            
        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None


