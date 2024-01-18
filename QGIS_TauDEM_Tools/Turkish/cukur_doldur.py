"""

Bu araç Terrain Analysis Using Digital Elevation Models (TauDEM) Pit Remove
aracını kullanarak yükseklik haritasındaki çukurları Doldurmaktadır.

Author: Mehmet B. Ercan
Date Created: 01.17.2024

"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProject
from qgis.core import QgsProcessingParameterNumber
# from qgis.core import QgsLayerTreeGroup
# from qgis.core import QgsProcessingOutputLayerDefinition
from qgis.core import QgsProcessingParameterFile
import processing


from subprocess import PIPE, Popen

import os

import logging


class FillRaster(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('dem', 'Yükseklik Haritası', 
                        defaultValue=None, types=[QgsProcessing.TypeRaster]))
        self.addParameter(QgsProcessingParameterNumber('number_of_processors', 
                        'İşlemci Sayısı', 
                        type=QgsProcessingParameterNumber.Integer, 
                        minValue=1, defaultValue=8))
        self.addParameter(QgsProcessingParameterFile('output_dir', 
                        'Çıktı Klasörü', 
                        behavior=QgsProcessingParameterFile.Folder, 
                        fileFilter='Tüm dosyalar (*.*)', 
                        defaultValue='D:\SCRATCH\GIS\d11\cikti'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress 
        # reports are adjusted for the overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(0, model_feedback)
        results = {}
        outputs = {}
        
        # get absolute paths
        dem_abs_path = get_abs_path_4_parameters_item(parameters['dem'])
        dem_name = os.path.basename(dem_abs_path)
        filled_dem_abs_path = os.path.join(parameters['output_dir'], 'f_'+dem_name)
        # define logging
        mylogs = logging.getLogger(__name__)
        file = logging.FileHandler(os.path.join(parameters['output_dir'], "raster_fill.log"))
        fileformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        mylogs.addHandler(file)
        mylogs.setLevel(logging.INFO)
        mylogs.info("dem_abs_path:{} \n filled_dem_abs_path:{}".format(dem_abs_path, filled_dem_abs_path))

        # TauDEM fill dem
        taudem = TauDEM(n_core=parameters['number_of_processors'], logs=mylogs)   
        taudem.pit_remove(dem_abs_path, filled_dem_abs_path)
        
        
        results['filled_dem'] = filled_dem_abs_path
        return results

    def name(self):
        return 'FillRaster'

    def displayName(self):
        return 'TauDEM Çukur Doldurma Aracı'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def shortHelpString(self):
        html_string = '''
			<!--.................. ACIKLAMA .......................-->
			Bu araç Terrain Analysis Using Digital Elevation Models (TauDEM) <a href="https://hydrology.usu.edu/taudem/taudem5/help53/PitRemove.html">Pit Remove</a> aracını kullanarak yükseklik haritasındaki çukurları Doldurmaktadır. 

			<!--.........................................-->


			<!--.................. GİRDİ PARAMETRELERİ .......................-->
			<h2>Girdi parametreleri</h2>
			<h3>Yüksekik Haritası</h3>
			Her hücre için yükseklik bilgileri bulunan raster katmanı. 
			<h3>İşlemci Sayısı</h3>
			Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.
			<h3>Çıktı Klasörü</h3>
			Çukurları doldurulmuş yükseklik haritasının kaydedileceği klasör.
			<!--.........................................-->


			<!--................... ÇIKTI PARAMETRELERİ ......................-->
			<h2>Çıktı parametreleri</h2>
			Çıktılar QGIS'de otomatik açılmamaktadır. Araç çalıştıktan sonra (girdi parametrelerinde tanımlanan) çıktı klasöründe oluşan tif dosyasını QGIS'de açabilirsiniz.
			<h3>Çukurları Doldurulmuş Yükseklik Haritası</h3>
			Akışın etki alanından yönlendirilmesi için çukurların kaldırıldığı bir yükseklik değerleri rasterı. Çukurlar, dijital yükseklik modellerinde (DEM'ler) daha yüksek arazilerle tamamen çevrili olan düşük yükseklikli alanlardır. Genellikle DEM'ler boyunca akışın işlenmesini engelleyen çukurlar olarak kabul edilirler. Bu nedenle, yükseklikleri sadece drenaj yaptıkları noktaya yükseltilerek kaldırılırlar.
			<!--.........................................-->
        '''
        return html_string

    def createInstance(self):
        return FillRaster()


 
def get_abs_path_4_parameters_item(parameters_item):
    # Get info for Layer's absulute file path
    root = QgsProject.instance().layerTreeRoot()
    layers_ids = []; layers_names = []
    for layer in QgsProject.instance().mapLayers().values():
        layers_names.append(layer)
        layers_ids.append(root.findLayer(layer.id()))
    # Get Layer's absulute file path
    abs_path = ''
    if root.findLayer(parameters_item) in layers_ids:
        # if layer selected from dropdown menu select from map layers
        layer = layers_names[layers_ids.index(root.findLayer(parameters_item))]
        abs_path = layer.source()
    else:
        # otherwise parameters[key] is already absolute path of the layer
        abs_path = parameters_item
    return abs_path

# ============================ HELPER CLASS =======================
class TauDEM(object):
    
    def __init__(self, n_core=1, mpiexec_path="mpiexec", logs=None):
        self.logs = logs
        self.n_core = n_core
        self.mpiexec_path = mpiexec_path

    def run_commandline(self, cmd):
        # complete the taudem command line
        cmd = ["mpiexec", '-n', str(self.n_core)] + cmd
        if self.logs != None:
            self.logs.info("-------------- COMMAND  --------------\n")
            self.logs.info(cmd)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        output, error = process.communicate()
        if output:
            if self.logs != None:
                self.logs.info("-------------- COMMAND LINE OUTPUT --------------\n")
                for line in output.split(b'\n'):
                   self. logs.info(line)
        if error:
            if self.logs != None:
                self.logs.info("xxxxxxxxxxxxxx COMMAND LINE ERROR xxxxxxxxxxxxxx\n")
                self.logs.info(error)

    def pit_remove(self, dem, filled_dem, depression_mask_raster=None, 
                   consider4way=False,):
        if self.logs != None:
            self.logs.info("Running TauDEM pitremove command...")
        
        # create the taudem command line
        cmd = ['pitremove', '-z', dem, '-fel', filled_dem]
        # add optional parameters to the command line
        if depression_mask_raster:
            cmd += ['-depmask', depression_mask_raster]
        if consider4way:
            cmd += ['-4way']

        self.run_commandline(cmd)

    def flowdir_slope(self, filled_dem, out_flowdir, out_slope):
        if self.logs != None:
            self.logs.info("Running TauDEM d8flowdir command...")
        
        # create the taudem command line
        cmd = ['d8flowdir', '-fel', filled_dem, '-p', out_flowdir, '-sd8', out_slope]

        self.run_commandline(cmd)

    def flowacc_watershed(self, fd_abs_path, wtrshd_abs_path, outletshp_abs_path=None, 
                   weight_abs_path=None, edge_contamination=True):
        if self.logs != None:
            self.logs.info("Running TauDEM AreaD8 command...")
        
        # create the taudem command line
        cmd = ['aread8', '-p', fd_abs_path, '-ad8', wtrshd_abs_path]
        if outletshp_abs_path:
            cmd += ['-o', outletshp_abs_path]
        if weight_abs_path:
            cmd += ['-wg', weight_abs_path]
        if not edge_contamination:
            cmd = cmd + ['-nc']
        
        self.run_commandline(cmd)

