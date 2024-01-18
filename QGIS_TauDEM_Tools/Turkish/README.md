# QGIS TauDEM Araçları

Bu araç Terrain Analysis Using Digital Elevation Models (TauDEM) <a href="https://hydrology.usu.edu/taudem/taudem5/help53/D8ContributingArea.html">D8 Contributing Area</a> aracını kullanarak akış toplamayı hesaplamaktadır. 

### Bu araçların çalışabilmesi için aşağıdaki işlemlerin yapılması gerekmektedir: 
- #### <a href="https://hydrology.usu.edu/taudem/taudem5/downloads.html">TauDEM İndirme Sitesinden</a> TauDEM'in indirilip kurulması gerekmektedir

- #### QGIS Ortam değişkenlerine TauDEM ile kurulan araçlar eklenmelidir. 
    * <b>QGIS Ortam Değişkenlerinin Ayarlanması:</b> QGIS <b>Ayarlar</b> menüsünden <b>Seçenekleri</b> seçiniz. Açılan pencereden soldaki <b>Sistem</b>i seçiniz ve en alta inderek <b>Current environment variables</b> ayarını bulunuz. Buradan <b>PATH</b> değişkeninin karşısındaki <b>Değer</b>i (C:\PROGRA~1\QGIS33~1.0\apps\qgis\bin;C:\PR... gibi) kopyalayıp notepad'a daha sonra GDAL, TauDEM ve MPIEXEC klasör konumlarını eklemek için yapıştırınız. GDAL, TauDEM ve MPIEXEC exe uzantılı araçlarının klasör yerlerini bilmiyorsanız, bilgisayarınızın ortam değişkenlerinden kontrol edebilirsiniz. Bunlar genelde şu konumdadırlar: C:\Program Files\GDAL, C:\GDAL, C:\Program Files\Microsoft MPI\Bin, C:\Program Files\TauDEM\TauDEM5Exe. Bunlar notepad'e yapıştırdığınız değişkene eklenince şunun gibi bir değişken oluşacak: [C:\Program Files\GDAL;C:\GDAL;C:\Program Files\Microsoft MPI\Bin;C:\Program Files\TauDEM\TauDEM5Exe;C:\PROGRA~1\QGIS33~1.0\apps\qgis\bin;C:\PROGRA~1\QGIS33~...]. Notepad'de oluşturduğunuz bu değişkeni <b>Çevre</b>nin altında <b>Use custom variables</b>ı işaretleyerek ve <b>artı</b> tuşuna basarak, eklenen satırda <b>Değer</b>in altına yapıştırınız. <b>Değişken</b> kısmına PATH yazınız ve <b>Uygula</b> kısmında Üzerine yaz seçeneğini seçiniz. Daha sonra <b>Tamam</b> tuşuna basarak işlemi bitiriniz. Bunun aktivleşmesi için QGIS'i kapatıp tekrar açınız.

Bu araç Windows için <b>TauDEM 5.3.7 Complete Windows installer</b> ile <b>QGIS 3.34.0-Prizren</b> üzerinde test edilmiştir.


Çıktılar QGIS'de otomatik açılmamaktadır. Araç çalıştıktan sonra (girdi parametrelerinde tanımlanan) çıktı klasöründe oluşan yeni tif dosyasını QGIS'de açabilirsiniz. 

<!--......................................................-->
## Çukur Doldurma
###  Aracın Çalışması İçin Gerekli Girdiler
- <b>Yüksekik Haritası:</b> Her hücre için yükseklik bilgileri bulunan raster katmanı. 

- <b>İşlemci Sayısı:</b> Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.

- <b>Çıktı Klasörü:</b> Akış toplanma haritalarının kaydedileceği klasör.


###  Çıktılar
- <b>Çukurları Doldurulmuş Yükseklik Haritası:</b> Akışın etki alanından yönlendirilmesi için çukurların kaldırıldığı bir yükseklik değerleri rasterı. Çukurlar, dijital yükseklik modellerinde (DEM'ler) daha yüksek arazilerle tamamen çevrili olan düşük yükseklikli alanlardır. Genellikle DEM'ler boyunca akışın işlenmesini engelleyen çukurlar olarak kabul edilirler. Bu nedenle, yükseklikleri sadece drenaj yaptıkları noktaya yükseltilerek kaldırılırlar.


<!--......................................................-->


## Akış Yönü ve Eğim
###  Aracın Çalışması İçin Gerekli Girdiler
- <b>Akış Yönü Haritası:</b> Her hücre için, sekiz bitişik veya çapraz komşusundan en dik aşağı doğru eğime sahip olanın yönü olarak tanımlanan D8 akış yönleri rasterı. Akış Yönü Kodlaması: 1 -Doğu, 2 - Kuzeydoğu, 3 - Kuzey, 4 - Kuzeybatı, 5 - Batı, 6 - Güneybatı, 7 - Güney, 8 - Güneydoğu.

- <b>İşlemci Sayısı:</b> Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.

- <b>Çıktı Klasörü:</b> Akış toplanma haritalarının kaydedileceği klasör.


###  Çıktılar
- <b>Akış Toplanma Haritası:</b> Hücrelerde tamsayı değerleri vardır. Bu değerler her hücrenin kendisi artı kendisine drene olan yukarı yamaç komşularının toplam sayısı olarak hesaplanır. 


<!--......................................................-->



## Akış Toplanması
###  Aracın Çalışması İçin Gerekli Girdiler
- <b>Akış Yönü Haritası:</b> Her hücre için, sekiz bitişik veya çapraz komşusundan en dik aşağı doğru eğime sahip olanın yönü olarak tanımlanan D8 akış yönleri rasterı. Akış Yönü Kodlaması: 1 -Doğu, 2 - Kuzeydoğu, 3 - Kuzey, 4 - Kuzeybatı, 5 - Batı, 6 - Güneybatı, 7 - Güney, 8 - Güneydoğu.

- <b>İşlemci Sayısı:</b> Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.

- <b>Çıktı Klasörü:</b> Akış toplanma haritalarının kaydedileceği klasör.


###  Çıktılar
- <b>Akış Toplanma Haritası:</b> Hücrelerde tamsayı değerleri vardır. Bu değerler her hücrenin kendisi artı kendisine drene olan yukarı yamaç komşularının toplam sayısı olarak hesaplanır. 



<!--......................................................-->



## Havza Oluşturma
###  Aracın Çalışması İçin Gerekli Girdiler
- <b>Akış Yönü Haritası:</b> Her hücre için, sekiz bitişik veya çapraz komşusundan en dik aşağı doğru eğime sahip olanın yönü olarak tanımlanan D8 akış yönleri rasterı. Akış Yönü Kodlaması: 1 -Doğu, 2 - Kuzeydoğu, 3 - Kuzey, 4 - Kuzeybatı, 5 - Batı, 6 - Güneybatı, 7 - Güney, 8 - Güneydoğu.

- <b>Havza Çıkışı Noktası:</b> Havzanın çıkışında akarsu üzerinde bir nokta şekil dosyası. Yalnızca bu çıkış noktalasının yukarı eğimindeki hücrelerden oluşan havza alanı hesaplanır.

- <b>İşlemci Sayısı:</b> Bilgisayarınızdaki işlemcilerden kullanmak istediğiniz miktarı giriniz. Varsayılan değer olarak 8 işlemci kullanılmaktadır. Bilgisayarınızı dondurmuyorsa ve bunun ne olduğunu bilmiyorsanız varsayılan değeri değiştirmeyiniz.

- <b>Çıktı Klasörü:</b> Akış toplanma haritalarının kaydedileceği klasör.


###  Çıktılar
- <b>Havza Alanı Haritası:</b> Havza alanı haritası. Bu haritanın hücrelerinde akış toplama tam sayı değerleri vardır. 
<!--.........................................-->


