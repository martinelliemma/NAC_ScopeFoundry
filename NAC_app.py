'''
Neo Andor Camera App
*******************
@authors: Emma Martinelli, Andrea Bassi. Politecnico di Milano

'''
from ScopeFoundry import BaseMicroscopeApp

class NeoAndor_app(BaseMicroscopeApp):
    name = 'NeoAndorApp'
    
    def setup(self):
        
        #Add hardware components
        print("Adding Camera Hardware Components")
        from NAC_hw import NeoAndorHW
        self.add_hardware(NeoAndorHW(self))

         
        # Add measurement components
        print("Create Measurement objects")
        from NAC_measure import NeoAndorMeasure
        self.add_measurement(NeoAndorMeasure(self))


if __name__ == '__main__':
    import sys

    app = NeoAndor_app(sys.argv)

    # connect all the hardwares
    # for hc_name, hc in app.hardware.items():
    #    hc.settings['connected'] = True

    sys.exit(app.exec_())