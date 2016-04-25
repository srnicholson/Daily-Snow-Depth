from PyQt4.QtGui import *
from PyQt4.QtCore import *
import glob, os, shutil, processing, time, threading

#set Github repo directory path
repo_path = 'E:/Scott/Documents/GitHub/Daily-Snow-Depth/'

def kill_saga_cmd():
#function to kill saga_cmd.exe after a certain amount of time if it stops responding
    os.system("taskkill /im saga_cmd.exe")
    print "ALERT: killed unresponsive saga_cmd.exe process."

#Load North American Satellite Raster Layer 1
NA_sat_1_path=os.path.join(repo_path,'QGIS_Python/Satellite','N1_A.jpg')
NA_sat_1 = iface.addRasterLayer(NA_sat_1_path, "NA Sat 1")
if not NA_sat_1:
  print "NA_sat_1 failed to load!"

#Load North American Satellite Raster Layer 2
NA_sat_2_path=os.path.join(repo_path,'QGIS_Python/Satellite','N2_A.jpg')
NA_sat_2 = iface.addRasterLayer(NA_sat_2_path, "NA Sat 2")
if not NA_sat_2:
  print "NA_sat_2 failed to load!"

#Begin Looping through csv files

#Path to CSV files
path_to_csvs=os.path.join(repo_path,'Data_Processing/csv/')
list_of_csvs=glob.glob(path_to_csvs + '*.csv')
t0=time.time()
count = 0
for file in list_of_csvs:
    date=file[-12:-4]
    print date
    count += 1
    print '------------------Creating snow depth visualization for ' + date + '. Day ' + str(count) + ' of ' + str(len(list_of_csvs)) + '.------------------'
    #load Lower 48 States Shapefile
    lower_48_shapefile_path=os.path.join(repo_path,'QGIS_Python/Shapefiles/cb_2014_us_state_500k.shp')
    lower_48_shapefile = iface.addVectorLayer(lower_48_shapefile_path, "lower48shapefile", "ogr")
    if not lower_48_shapefile:
      print "lower_48_shapefile failed to load!"
    
    #Load Snow Depth Data Layer
    SNWD_data_uri = "file:///" + file + "?delimiter=%s&xField=%s&yField=%s" % (",", "Longitude", "Latitude")
    SNWD_data_layer=iface.addVectorLayer(SNWD_data_uri,date,"delimitedtext")
    
    #multi-level b-spline interpolation using SAGA
    t_spline_start=time.time()
    t = threading.Timer(30.0, kill_saga_cmd) #kills unresponsive saga_cmd.exe after 30 seconds, which is about double the amount of time this step usually takes when it doesn't become unresponsive
    t.start()
    print "interpolating " + date
    outputs_1=processing.runalg("saga:multilevelbsplineinterpolation",SNWD_data_uri,"Value",1,0.0001,50,"-124.763068,-66.949895,24.523096,49.384358",0.025,None)
    t.cancel()
    print "b-spline interpolation took " + str(time.time()-t_spline_start) + " seconds."
    
    #clip to state shapefile
    print "masking " + date
    outputs_2=processing.runalg("gdalogr:cliprasterbymasklayer",outputs_1['USER_GRID'],lower_48_shapefile,"-9999",False,False,"",None)
    
    #Gaussian filter to reduce "holes"
    t = threading.Timer(20.0, kill_saga_cmd) #ends unresponsive saga_cmd.exe after 20 seconds, which is about double the amount of time this step usually takes
    t.start()
    t_filter_start=time.time()
    print "filtering " + date
    outputs_3=processing.runandload("saga:gaussianfilter",outputs_2['OUTPUT'], 5, 1, 10,None)
    t.cancel()
    print "gaussian filter took " + str(time.time()-t_filter_start) + " seconds."
    
    #identify raster layer
    layers = iface.legendInterface().layers()
    for layer in layers:
        if 'Filtered Grid' in layer.name():
            #render
            fcn = QgsColorRampShader()
            fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
			#Snow Depth Color Gradient (same as that used by http://www.instantweathermaps.com/ )
            colormap = []
            colormap.append(QgsColorRampShader.ColorRampItem(0,QColor(255,255,255,0),'0 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2.5399,QColor(255,255,255,0),'0.099 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2.54,QColor(230,255,225,76.5),'0.1 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(12.6999,QColor(230,255,225,76.5),'0.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(12.7,QColor(180,250,170,102),'0.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(25.3999,QColor(180,250,170,102),'0.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(25.4,QColor(120,245,115,127.5),'1 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(38.0999,QColor(120,245,115,127.5),'1.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(38.1,QColor(55,210,60,153),'1.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(50.7999,QColor(55,210,60,153),'1.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(50.8,QColor(30,180,30,178.5),'2 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(63.4999,QColor(30,180,30,178.5),'2.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(63.5,QColor(5,150,5,204),'2.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(76.1999,QColor(5,150,5,204),'2.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(76.2,QColor(225,255,255,229.5),'3 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(88.8999,QColor(225,255,255,229.5),'3.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(88.9,QColor(180,240,250,255),'3.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(101.5999,QColor(180,240,250,255),'3.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(101.6,QColor(120,185,250,255),'4 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(114.2999,QColor(120,185,250,255),'4.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(114.3,QColor(80,165,245,255),'4.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(126.9999,QColor(80,165,245,255),'4.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(127,QColor(40,130,240,255),'5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(139.6999,QColor(40,130,240,255),'5.499 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(139.7,QColor(20,100,210,255),'5.5 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(152.3999,QColor(20,100,210,255),'5.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(152.4,QColor(255,230,230,255),'6 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(177.7999,QColor(255,230,230,255),'6.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(177.8,QColor(255,200,200,255),'7 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(203.1999,QColor(255,200,200,255),'7.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(203.2,QColor(230,140,140,255),'8 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(228.5999,QColor(230,140,140,255),'8.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(228.6,QColor(230,112,112,255),'9 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(253.9999,QColor(230,112,112,255),'9.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(254,QColor(200,60,60,255),'10 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(279.3999,QColor(200,60,60,255),'10.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(279.4,QColor(164,32,32,255),'11 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(304.7999,QColor(164,32,32,255),'11.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(304.8,QColor(255,250,170,255),'12 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(355.5999,QColor(255,250,170,255),'13.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(355.6,QColor(255,232,120,255),'14 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(406.3999,QColor(255,232,120,255),'15.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(406.4,QColor(255,160,0,255),'16 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(457.1999,QColor(255,160,0,255),'17.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(457.2,QColor(255,96,0,255),'18 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(507.9999,QColor(255,96,0,255),'19.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(508,QColor(225,20,0,255),'20 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(558.7999,QColor(225,20,0,255),'21.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(558.8,QColor(165,0,0,255),'22 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(609.5999,QColor(165,0,0,255),'23.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(609.6,QColor(220,220,255,255),'24 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(685.7999,QColor(220,220,255,255),'26.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(685.8,QColor(192,180,255,255),'27 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(761.9999,QColor(192,180,255,255),'29.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(762,QColor(160,140,255,255),'30 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(838.1999,QColor(160,140,255,255),'32.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(838.2,QColor(128,112,235,255),'33 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(914.3999,QColor(128,112,235,255),'35.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(914.4,QColor(72,60,200,255),'36 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(990.5999,QColor(72,60,200,255),'38.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(990.6,QColor(60,40,180,255),'39 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1066.7999,QColor(60,40,180,255),'41.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1066.8,QColor(45,30,165,255),'42 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1142.9999,QColor(45,30,165,255),'44.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1143,QColor(40,0,160,255),'45 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1219.1999,QColor(40,0,160,255),'47.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1219.2,QColor(250,240,230,255),'48 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1523.9999,QColor(250,240,230,255),'59.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1524,QColor(240,220,210,255),'60 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1828.7999,QColor(240,220,210,255),'71.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(1828.8,QColor(225,190,180,255),'72 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2133.5999,QColor(225,190,180,255),'83.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2133.6,QColor(180,140,130,255),'84 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2438.3999,QColor(180,140,130,255),'95.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2438.4,QColor(160,120,110,255),'96 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2743.1999,QColor(160,120,110,255),'107.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(2743.2,QColor(140,100,90,255),'108 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(3047.9999,QColor(140,100,90,255),'119.999 Inches'))
            colormap.append(QgsColorRampShader.ColorRampItem(3048,QColor(100,60,50,255),'>=120 Inches'))
            fcn.setColorRampItemList(colormap)
            shader = QgsRasterShader()
            shader.setRasterShaderFunction(fcn)
            renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
            layer.setRenderer(renderer)
        elif layer.name()=='lower48shapefile':
            QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
        elif layer.name()==date: #remove snow depth data layer
            QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
    
    #load Lower 48 States Shapefile Again (to put it on top-- could probably be done more cleanly)
    lower_48_shapefile = iface.addVectorLayer(lower_48_shapefile_path, "lower48shapefile", "ogr")
    if not lower_48_shapefile:
      print "lower_48_shapefile failed to load!"
    #set states shapefile to transparent color if it isn't already
    symbol = QgsFillSymbolV2.createSimple({'color' : 'transparent', 'width_border' : '0.1'})
    lower_48_shapefile.rendererV2().setSymbol(symbol)
    #export image
    print "exporting " + date
    mapRenderer=QgsMapRenderer()
    #get current layers (may be redundant)
    lst = []
    layers = iface.legendInterface().layers()
    second_lower48shapefile=False
    for layer in layers:
        lst.append(layer.id())
    mapRenderer.setLayerSet(lst)
    c = QgsComposition(mapRenderer)
    c.setPlotStyle(QgsComposition.Print)
    
    #create and add map
    x, y = 0, 0
    c.setPaperSize(162.56, 91.44)
    w, h = c.paperWidth(), c.paperHeight()
    #For some reason, the offsets below were necessary to remove whitespace around map
    composerMap = QgsComposerMap(c, x-0.25, y, w+1.75, h+1)
    rect=QgsRectangle(-126.5,20,-65,54.59375)
    #composerMap.setFrameEnabled(True)
    composerMap.setNewExtent(rect)
    c.addItem(composerMap)

    #create and add title background
    title_back=QgsComposerShape(0,0,w,10,c)
    title_back.setShapeType(1)
    title_back.setFrameEnabled(False)
    title_back.setBackgroundColor(QColor(255,255,255,167)) #same as snow depth scale background
    c.addItem(title_back)

    #create and add title text
    title=QgsComposerLabel(c)
    date_nice=time.strptime(date,"%Y%m%d")
    date_nice=time.strftime("%B %d, %Y",date_nice)
    title.setText("U.S. Snow Depth on %s" % date_nice)
    title.setFont(QFont("Cambria Math",18))
    title.adjustSizeToText()
    title.setItemPosition(w/2,10/2,itemPoint=QgsComposerItem.Middle)
    c.addItem(title)

    #add snow depth scale image
    scale_pic=QgsComposerPicture(c)
    scale_pic.setPictureFile(os.path.join(repo_path,'QGIS_Python/SNWD_scale.svg'))
    scale_pic_rect=QRectF(0,0,110,110)
    scale_pic.setSceneRect(scale_pic_rect)
    scale_pic.setPos(QPointF(0,h-12))
    c.addItem(scale_pic)

    #set resolution
    dpi = c.printResolution()
    dpmm = dpi / 25.4
    width = int(dpmm * c.paperWidth())
    height = int(dpmm * c.paperHeight())

    # create output image and initialize it
    image = QImage(QSize(width, height), QImage.Format_ARGB32)
    image.setDotsPerMeterX(dpmm * 1000)
    image.setDotsPerMeterY(dpmm * 1000)
    image.fill(0)

    # render the composition
    imagePainter = QPainter(image)
    sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
    targetArea = QRectF(0, 0, width, height)
    c.render(imagePainter, targetArea, sourceArea)
    imagePainter.end()
    
    #save the image
    directory=os.path.join(repo_path,'QGIS_Python','Rendered_Frames/') + str(date)[:4] + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    image.save(directory + date + ".png", "png")
    print "%s image saved." %date
    layers = iface.legendInterface().layers()
    #end of image export
    
    #remove old layers
    for layer in layers:
        if 'Filtered Grid' in layer.name():
            #remove filtered layer
            QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
        elif 'lower48shapefile' in layer.name():
            #remove lower_48_shapefile layer(s)
            QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])
    
    #display timer and reset
    t1=time.time()
    print date + " image took " + str(t1-t0) + " seconds to generate."
    t0=t1
#remove satellite layers
layers = iface.legendInterface().layers()
for layer in layers:
    if 'NA Sat ' in layer.name():
        #remove filtered layer
        QgsMapLayerRegistry.instance().removeMapLayers([layer.id()])

print "Finished."