"""

Bu araç Terrain Analysis Using Digital Elevation Models (TauDEM) D8 Flow 
Directions aracını kullanarak akış yönü ve eğim hesaplamaktadır.

Author: Mehmet B. Ercan
Date Created: 01.17.2024

"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProject
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFile
import processing


from subprocess import PIPE, Popen

import os

import logging


class FlowDirSlope(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('fdem', 'Çukurları Doldurulmuş Yükseklik Haritası', 
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
        fdem_abs_path = get_abs_path_4_parameters_item(parameters['fdem'])
        fdem_name = os.path.basename(fdem_abs_path)
        fd_dem_abs_path = os.path.join(parameters['output_dir'], 'fd_'+fdem_name)
        s_dem_abs_path = os.path.join(parameters['output_dir'], 's_'+fdem_name)
        
        # define logging
        mylogs = logging.getLogger(__name__)
        file = logging.FileHandler(os.path.join(parameters['output_dir'], "akisyonu_egim.log"))
        fileformat = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s",datefmt="%H:%M:%S")
        file.setFormatter(fileformat)
        mylogs.addHandler(file)
        mylogs.setLevel(logging.INFO)
        mylogs.info("\n  fdem_abs_path:{} \n  flowdır_fdem_abs_path:{} \n  slope_fdem_abs_path:{}".format(
            fdem_abs_path, fd_dem_abs_path, s_dem_abs_path))

        # TauDEM D8Flowdir
        taudem = TauDEM(n_core=parameters['number_of_processors'], logs=mylogs)   
        taudem.flowdir_slope(fdem_abs_path, fd_dem_abs_path, s_dem_abs_path)
        
        # return results
        results['fd_dem_abs_path'] = fd_dem_abs_path
        results['s_dem_abs_path'] = s_dem_abs_path
        return results

    def name(self):
        return 'FlowDirSlope'

    def displayName(self):
        return 'TauDEM Akış Yönü ve Eğim Aracı'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def shortHelpString(self):
        html_string = '''
			<!--.................. ACIKLAMA .......................-->
			Bu araç Terrain Analysis Using Digital Elevation Models (TauDEM) <a href="https://hydrology.usu.edu/taudem/taudem5/help53/D8FlowDirections.html">D8 Flow Directions</a> aracını kullanarak akış yönü ve eğim hesaplamaktadır. 

			<h4>Bu aracın çalışabilmesi için aşağıdaki işlemlerin yapılması gerekmektedir:</h4>  
			<a href="https://hydrology.usu.edu/taudem/taudem5/downloads.html">TauDEM İndirme Sitesinden</a> TauDEM'in indirilip kurulması gerekmektedir

			QGIS Ortam değişkenlerine TauDEM ile kurulan araçlar eklenmelidir. QGIS Ortam Değişkenlerinin Ayarlanması:
				QGIS <b>Ayarlar</b> menüsünden <b>Seçenekleri</b> seçiniz. Açılan pencereden soldaki <b>Sistem</b>i seçiniz ve en alta inderek <b>Current environment variables</b> ayarını bulunuz. Buradan <b>PATH</b> değişkeninin karşısındaki <b>Değer</b>i (C:\PROGRA~1\QGIS33~1.0\apps\qgis\bin;C:\PR... gibi) kopyalayıp notepad'a daha sonra GDAL, TauDEM ve MPIEXEC klasör konumlarını eklemek için yapıştırınız. GDAL, TauDEM ve MPIEXEC exe uzantılı araçlarının klasör yerlerini bilmiyorsanız, bilgisayarınızın ortam değişkenlerinden kontrol edebilirsiniz. Bunlar genelde şu konumdadırlar: C:\Program Files\GDAL, C:\GDAL, C:\Program Files\Microsoft MPI\Bin, C:\Program Files\TauDEM\TauDEM5Exe. Bunlar notepad'e yapıştırdığınız değişkene eklenince şunun gibi bir değişken oluşacak: [C:\Program Files\GDAL;C:\GDAL;C:\Program Files\Microsoft MPI\Bin;C:\Program Files\TauDEM\TauDEM5Exe;C:\PROGRA~1\QGIS33~1.0\apps\qgis\bin;C:\PROGRA~1\QGIS33~...]. Notepad'de oluşturduğunuz bu değişkeni <b>Çevre</b>nin altında <b>Use custom variables</b>ı işaretleyerek ve <b>artı</b> tuşuna basarak, eklenen satırda <b>Değer</b>in altına yapıştırınız. <b>Değişken</b> kısmına PATH yazınız ve <b>Uygula</b> kısmında Üzerine yaz seçeneğini seçiniz. Daha sonra <b>Tamam</b> tuşuna basarak işlemi bitiriniz. Bunun aktivleşmesi için QGIS'i kapatıp tekrar açınız.
			Bu araç Windows için <b>TauDEM 5.3.7 Complete Windows installer</b> ile <b>QGIS 3.34.0-Prizren</b> üzerinde test edilmiştir.
			<!--.........................................-->


			<!--.................. GİRDİ PARAMETRELERİ .......................-->
			<h2>Girdi parametreleri</h2>
			<h3>Çukurları Doldurulmuş Yükseklik Haritası</h3>
			Her hücre için yükseklik bilgileri bulunan raster katmanı. Bu katmandaki akarsuların güzergahı üzerinde çukur olmamalıdır. Eğer bu çukurlar kaldırılmazsa, daha sonraki adımlarda havza alanının yanlış oluşmasına sebeb olabilir.
			<h3>İşlemci Sayısı</h3>
			Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.
			<h3>Çıktı Klasörü</h3>
			Akış yönü ve eğim haritalarının kaydedileceği klasör.
			<!--.........................................-->


			<!--................... ÇIKTI PARAMETRELERİ ......................-->
			<h2>Çıktı parametreleri</h2>
			Çıktılar QGIS'de otomatik açılmamaktadır. Araç çalıştıktan sonra (girdi parametrelerinde tanımlanan) çıktı klasöründe oluşan tif dosyalarını QGIS'de açabilirsiniz.
			<h3>Akış Yönü Haritası</h3>
			Her hücre için, sekiz bitişik veya çapraz komşusundan en dik aşağı doğru eğime sahip olanın yönü olarak tanımlanan D8 akış yönleri rasterı. Akış Yönü Kodlaması: 1 -Doğu, 2 - Kuzeydoğu, 3 - Kuzey, 4 - Kuzeybatı, 5 - Batı, 6 - Güneybatı, 7 - Güney, 8 - Güneydoğu.
			<h3>Eğim Haritası</h3>
			D8 akış yönünde eğim veren bir ızgara. Bu, düşü/mesafe olarak hesaplanır.
			<!--.........................................-->
        '''
        return html_string

    def createInstance(self):
        return FlowDirSlope()



 
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

