'''
Neo Andor Camera Measurement
*******************
@authors: Emma Martinelli, Andrea Bassi. Politecnico di Milano

'''
from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
from ScopeFoundry import h5_io
import pyqtgraph as pg
import numpy as np
import os, time

class NeoAndorMeasure(Measurement):
    name = "NeoAndormeasure"
    
    def setup(self):
        self.ui_filename = sibling_path(__file__, "camera.ui")
        self.ui = load_qt_ui_file(self.ui_filename) 
        
        self.settings.New('save_h5', dtype=bool, initial=False)         
        # how often we want to update the display
        self.settings.New('refresh_period', dtype = float, unit ='s', spinbox_decimals = 3, initial = 0.05, vmin = 0)
        
        self.settings.New('xsampling', dtype=float, unit='um', initial=0.0586, spinbox_decimals = 3) 
        self.settings.New('ysampling', dtype=float, unit='um', initial=0.0586, spinbox_decimals = 3)
        self.settings.New('zsampling', dtype=float, unit='um', initial=1.0)
        
        self.auto_range = self.settings.New('auto_range', dtype=bool, initial=True)
        self.settings.New('auto_levels', dtype=bool, initial=True)
        self.settings.New('level_min', dtype=int, initial=60)
        self.settings.New('level_max', dtype=int, initial=4000)

        # link to the hardware: in the attribute self.image_gen we have placed the hardware
        # and so from the hardware we can go to the settings
        self.image_gen = self.app.hardware['NeoAndorHW']

    def setup_figure(self):
        """
        Runs once during App initialization, after setup()
        This is the place to make all graphical interface initializations,
        build plots, etc.
        """
        # connect ui widgets to measurement/hardware settings or functions
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
        self.settings.save_h5.connect_to_widget(self.ui.save_h5_checkBox)
        self.settings.auto_levels.connect_to_widget(self.ui.autoLevels_checkbox)
        self.settings.auto_range.connect_to_widget(self.ui.autoRange_checkbox)
        self.settings.level_min.connect_to_widget(self.ui.min_doubleSpinBox) 
        self.settings.level_max.connect_to_widget(self.ui.max_doubleSpinBox) 
                
        # Set up pyqtgraph graph_layout in the UI
        self.imv = pg.ImageView()
        self.ui.imageLayout.addWidget(self.imv)
        colors = [(0, 0, 0),
                  (45, 5, 61),
                  (84, 42, 55),
                  (150, 87, 60),
                  (208, 171, 141),
                  (255, 255, 255)
                  ]
        cmap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 6), color=colors)
        self.imv.setColorMap(cmap)
        
    def update_display(self):
        """
        Displays (plots) the numpy array self.buffer. 
        This function runs repeatedly and automatically during the measurement run.
        its update frequency is defined by self.display_update_period
        """
        self.display_update_period = self.settings['refresh_period'] 
       
        length = self.image_gen.frame_num.val
        self.settings['progress'] = (self.frame_index +1) * 100/length

        # if an image has been acquired
        if hasattr(self, 'img'):
            #show the image
            self.imv.setImage(self.img.T,
                                autoLevels = self.settings['auto_levels'],
                                autoRange = self.auto_range.val,
                                levelMode = 'mono'
                                )
            
            if self.settings['auto_levels']:
                lmin,lmax = self.imv.getHistogramWidget().getLevels()
                self.settings['level_min'] = lmin
                self.settings['level_max'] = lmax
            else:
                self.imv.setLevels( min= self.settings['level_min'],
                                    max= self.settings['level_max'])

    def measure(self):
        self.image_gen.read_from_hardware()

        first_frame_acquired = False

        self.length = frame_num = self.image_gen.frame_num.val
        self.image_gen.camera.acquisition_setup(frame_num)
        self.image_gen.camera.acquisition_start()

        for frame_idx in range(frame_num):
            self.frame_index = frame_idx

            self.image_gen.camera.image_wait()
            self.img = self.image_gen.camera.image_read()

            if not first_frame_acquired:
                self.create_h5_file()
                first_frame_acquired = True

            self.image_h5[frame_idx, :, :] = self.img
            self.h5file.flush()

            if self.interrupt_measurement_called:
                break

    def run(self):
        """
        Runs when measurement is started. Runs in a separate thread from GUI.
        It should not update the graphical interface directly, and should only
        focus on data acquisition.
        """
        self.image_gen.read_from_hardware()
        
        try:
            self.frame_index = -1

            self.image_gen.camera.acquisition_clear()
            self.image_gen.camera.acquisition_setup(self.image_gen.frame_num.value)
            self.image_gen.camera.acquisition_start()

            while not self.interrupt_measurement_called:

                # If measurement is called, stop the acquisition, call self.measure
                # and get out of run()
                if self.settings['save_h5']:
                    # measure is triggered by save_h5 button
                    self.image_gen.camera.acquisition_stop()
                    self.measure()
                    break

                self.image_gen.camera.image_wait()
                self.img = self.image_gen.camera.image_read()

                if self.interrupt_measurement_called:
                    break
                
        finally:            
            self.image_gen.camera.acquisition_stop()
            if self.settings['save_h5'] and hasattr(self, 'h5file'):
                # make sure to close the data file
                self.h5file.close()
                self.settings['save_h5'] = False

    def create_saving_directory(self):
        
        if not os.path.isdir(self.app.settings['save_dir']):
            os.makedirs(self.app.settings['save_dir'])

    def create_h5_file(self):                   
        self.create_saving_directory()
        # file name creation
        timestamp = time.strftime("%y%m%d_%H%M%S", time.localtime())
        sample = self.app.settings['sample']
        #sample_name = f'{timestamp}_{self.name}_{sample}.h5'
        if sample == '':
            sample_name = '_'.join([timestamp, self.name])
        else:
            sample_name = '_'.join([timestamp, self.name, sample])
        fname = os.path.join(self.app.settings['save_dir'], sample_name + '.h5')
        
        self.h5file = h5_io.h5_base_file(app=self.app, measurement=self, fname = fname)
        self.h5_group = h5_io.h5_create_measurement_group(measurement=self, h5group=self.h5file)
        
        img_size = self.img.shape
        dtype=self.img.dtype
        
        length = self.image_gen.frame_num.val
        self.image_h5 = self.h5_group.create_dataset(name  = 't0/c0/image', 
                                                  shape = [length, img_size[0], img_size[1]],
                                                  dtype = dtype)
        self.image_h5.attrs['element_size_um'] =  [self.settings['zsampling'],self.settings['ysampling'],self.settings['xsampling']]