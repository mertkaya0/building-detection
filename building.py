#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import cv2
import psycopg2
import random
import os
import geopy.distance
import json
from shapely.geometry import shape, GeometryCollection, Point,Polygon



with open('neighbourhood.geojson', 'r', encoding="utf-8") as f1:
    neighbourhoods = json.load(f1)

with open('area.geojson', 'r', encoding="utf-8") as f2:
    bh_areas = json.load(f2)


# ------------------------------------------------------*---------------------------------------------------------------------------

def sql(LONG, LAT):


    global district_name, district_id, neighbourhood_id, province_id, province_name, insertBinaYuksekligi, b_length_area_id, b_length


    point = Point(LONG, LAT)

    neighbourhood_name = "Diğer"
    neighbourhood_id = 999
    district_name = " "
    district_id = 55999
    province_name = "Samsun"
    province_id = 55


    # Hesaplanan koordinatın hangi mahallede olduğu 
    # mahalle polygonlarının mevcut olduğu geojson formatından tespit edilir.
    for neighbourhood_feature in neighbourhoods["features"]:

        neighbourhood_polygon = shape(neighbourhood_feature['geometry'])

        if neighbourhood_polygon.contains(point) == True:

            neighbourhood_name = str(neighbourhood_feature['properties']['Name'])
            neighbourhood_id = int(neighbourhood_feature['properties']['id'])
            district_name = str(neighbourhood_feature['properties']['district_name'])
            district_id = int(neighbourhood_feature['properties']['district_id'])
            province_name = str(neighbourhood_feature['properties']['province_name'])
            province_id = int(neighbourhood_feature['properties']['province_id'])
            break

        else:
            pass


    # Tespit edilen binanın kaç katlı olduğu
    # geojson formatından tespit edilir.
    for bh_feature in bh_areas["features"]:

        bh_area_polygon = shape(bh_feature['geometry'])

        if bh_area_polygon.contains(point) == True:
            b_length_area_id = str(bh_feature['properties']['id'])
        else:
            pass


    # Tespit edilen bina hangi 'alan_id' 'ye sahipse ona göre bir kat yüksekliği alır.
    if b_length_area_id == "1":
        b_length = random.choice([2, 2, 2, 2, 2, 3, 3, 3, 3, 4]) * 10

    elif b_length_area_id == "2":
        b_length = random.choice([3, 3, 4, 4, 5]) * 10

    elif b_length_area_id == "3":
        b_length = random.choice([4, 5, 6]) * 10

    elif b_length_area_id == "4":
        b_length = random.choice([4, 4, 4, 5, 5, 5, 6, 7, 8]) * 10

    elif b_length_area_id == "5":
        b_length = random.choice([4, 5, 5, 6, 6, 7, 7, 8, 8]) * 10

    elif b_length_area_id == "6":
        b_length = random.choice([5, 6, 7, 8]) * 10

    elif b_length_area_id == "7":
        b_length = random.choice([7, 7, 8, 8, 9, 10, 11]) * 10

    elif b_length_area_id == "8":
        b_length = random.choice([8, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]) * 10

    elif b_length_area_id == "9":
        b_length = random.choice([8, 8, 8, 9, 9, 9, 10, 10, 11]) * 10

    elif b_length_area_id == "10":
        b_length = random.choice([5, 6, 6, 6, 7, 7, 7, 8, 8]) * 10

    elif b_length_area_id == "11":
        b_length = random.choice([2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 6, 7, 8]) * 10

    elif b_length_area_id == "12":
        b_length = random.choice([5,6,7,8,9]) * 10



    # VERİLERİN POSTGRESQL'E AKTARILMASI
    query_insert_bf = (
        f"INSERT INTO buildings2021 (neighbourhood_id,neighbourhood_name,district_id,district_name,"
        f"province_id,province_name,b_length_area_id,b_length,b_polygon_geom,b_point_geom) VALUES ("
        f"'{neighbourhood_id}',"

        f"'{neighbourhood_name}',"

        f"'{district_id}',"

        f"'{district_name}',"

        f"'{province_id}',"

        f"'{province_name}',"

        f"'{b_length_area_id}',"

        f"'{b_length}',"

        f"(SELECT ST_MakePolygon(ST_GeomFromText('LINESTRING"
        f"("f"{LONG} {LAT},"
        f"{LONG - (widthPxLong1 * katsayiWidth)} {LAT - (widthPxLat1 * katsayiWidth)},"
        f"{LONG - (widthPxLong1 * katsayiWidth) + (heightPxLong1 * katsayiHeight)} {LAT + (heightPxLat1 * katsayiHeight) - (widthPxLat1 * katsayiWidth)},"
        f" {LONG + (heightPxLong1 * katsayiHeight)} {LAT + (heightPxLat1 * katsayiHeight)},"
        f"{LONG} {LAT})', 4326))),"

        f"(SELECT ST_GeomFromText"
        f"('POINT ({LONG - ((widthPxLong1 * katsayiWidth) / 2) + ((heightPxLong1 * katsayiHeight) / 2)} "
        f"{LAT - ((widthPxLat1 * katsayiWidth) / 2) + ((heightPxLat1 * katsayiHeight) / 2)})',4326)))"

    )

    cursor.execute(query_insert_bf)

# ------------------------------------------------------*---------------------------------------------------------------------------


def detectFromImage(image):
    building_cascade = cv2.CascadeClassifier("Train/train/classifier/cascade.xml")

    img = cv2.imread(image)
    grayScale = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    building = building_cascade.detectMultiScale(grayScale, 1.1358, 20)


    coordinates = []

    for (x, y, w, h) in building:

        if w >= 150:
            pass
        elif w <= 3:
            pass
        else:
            coordinates.append(([x + ((5*w)/7), y + ((7*h)/9)]))
            cv2.rectangle(img,
                          (x, y),
                          (x + w, y + h),
                          (0, 0, 225),
                          2)

    # cv2.imshow("img", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    return coordinates


# -----------------------------------------------------------*-------------------------------------------------------------------------



# POSTGRESQL BAĞLANTISI (POSTGRESQL CONNECTION) ----
connect = psycopg2.connect(database="buildingsDB",
                           user="postgres",
                           password="mert55",
                           host="localhost",
                           port="5432")

connect.autocommit = True
cursor = connect.cursor()
# POSTGRESQL BAĞLANTISI (POSTGRESQL CONNECTION) ----

# ------------------------------------------------------*---------------------------------------------------------------------------

#İncelenen bütün fotoğraflardan elde edilen bina sayısı değişkeni
total_building = 0

filesInImages = set()

for x in os.listdir("images"):
    target = int(x.split(".")[0])
    filesInImages.add(target)



for z in filesInImages:


    print(f"Şuan {z}.Fotoğraf İnceleniyor.....")
    time.sleep(0.3)

    try:
        coordinate_txt = open(f"images/{z}.txt", "r", encoding="utf-8")
    except:
        print(f"Koordinatları içeren {z}.txt uzantılı dosyaya ulaşılamadı...")
        continue

    row = 1
    for crdnt in coordinate_txt:

        coordinates = crdnt.replace(" ", "").replace("(", "").replace(")\n", "").replace(")", "").split(",")
        txtLat = float(coordinates[0])
        txtLong = float(coordinates[1])

        if row == 1:
            firstLatPoint = txtLat
            firstLongPoint = txtLong

        elif row == 2:
            secondLatPoint = txtLat
            secondLongPoint = txtLong
        else:
            thirdLatPoint = txtLat
            thirdLongPoint = txtLong

        row += 1


    fourthLatPoint = float((firstLatPoint - secondLatPoint) + thirdLatPoint)
    fourthLongPoint = float((firstLongPoint - secondLongPoint) + thirdLongPoint)

    try:
        img = cv2.imread(f"images/{z}.jpg")
        imgyedek = cv2.imread(f"images/{z}.jpg")
        resized_up_imgf = cv2.resize(imgyedek, (750, (int((750 * img.shape[0]) / img.shape[1]))), interpolation=cv2.INTER_LINEAR)
        cv2.imshow("showimg", resized_up_imgf)
        cv2.waitKey(100)
    except:
        print(f"{z}.jpg uzantılı dosyaya ulaşılamadı...")
        continue


    print("------------------------------------------------------------------")
    print("1.NOKTANIN KOORDİNATI------>", firstLatPoint, firstLongPoint)
    time.sleep(1)
    print("2.NOKTANIN KOORDİNATI------>", secondLatPoint, secondLongPoint)
    time.sleep(1)
    print("3.NOKTANIN KOORDİNATI------>", thirdLatPoint, thirdLongPoint)
    time.sleep(1)
    print("4.NOKTANIN KOORDİNATI------>",fourthLatPoint,fourthLongPoint)
    time.sleep(1)





    lengthFirstFourth = (geopy.distance.geodesic((firstLatPoint, firstLongPoint), (fourthLatPoint, fourthLongPoint)).m)

    lengthFirstSecond = (geopy.distance.geodesic((firstLatPoint, firstLongPoint), (secondLatPoint, secondLongPoint)).m)


    # İncelenen fotoğrafın 1. ve 4. nokta uzaklıkları, 1. ve 2. nokta uzaklıkları 125 metrelere bölünmektedir.
    dividedPiecesWidth = int(lengthFirstFourth / 125)
    dividedPiecesHeight = int(lengthFirstSecond / 125)



    print(f"{z}.FOTOĞRAFINIZ, GENİŞLİĞİ {dividedPiecesWidth} ADET PARÇA ve YÜKSELİĞİ {dividedPiecesHeight} ADET PARÇA OLMAK ÜZERE \n "
          f"TOPLAMDA {dividedPiecesWidth * dividedPiecesHeight} ADET KAREYE (125M * 125M) BÖLÜNMÜŞTÜR...")

    time.sleep(2)


    # İncelenecek olan fotoğraf parçalarının (125m kenar uzunluklarına sahip) genişlik ve yükseklik pikselleri
    width = int(img.shape[1] / dividedPiecesWidth)
    height = int(img.shape[0] / dividedPiecesHeight)



    print("------------------------------------------------------------------")
    print(f"FOTOĞRAFINIZ GENİŞİĞİ {img.shape[1]} PİKSEL \n"
          f"YÜKSEKLİĞİ {img.shape[0]} PİKSELDİR...")
    time.sleep(1)

    #Fotoğraftaki 1. 2. 3. Ve 4. noktaların koordinatlarını sqle aktarılması
    queryInsertCPoint = (
        f"INSERT INTO buildings2021(control_point) SELECT (st_geomfromtext('POINT({firstLongPoint} {firstLatPoint})',4326)) "
        f"UNION SELECT st_geomfromtext('POINT({secondLongPoint} {secondLatPoint})',4326) "
        f"UNION SELECT st_geomfromtext('POINT({thirdLongPoint} {thirdLatPoint})', 4326) "
        f"UNION SELECT st_geomfromtext('POINT({fourthLongPoint} {fourthLatPoint})', 4326)"
        )

    cursor.execute(queryInsertCPoint)

    #İncelenen fotoğrafın toplamında bulunan bina sayısı değişkeni
    number_OfBuilding = 0

    # Fotoğrafın yüksekiği 5 genişliği 10 parçaya bölünmüşse
    # i = Bize hangi satırda olduğumuz bilgisini verir.
    # x = Bize hangi kolonda olduğumuzu verir.
    # i = 3  , x = 5 ---> Şuanki incelenen fotoğraf parçası 3. satır 5. kolonda.

    for i in range(0, dividedPiecesHeight):

        for x in range(0, dividedPiecesWidth):

            # Fotoğrafımızı parçalara bölme kısımı:
            # i = 3, x = 5 ---> Fotoğrafın 3.satırı ve 5.kolon fotoğrafın hangi pikselleri arasında kaldığını hesaplar.
            # Hesaplanan bu değerlerle fotoğrafın sadece incelenecek kısımı kırpılır.
            imgCrop = img[(i * height):(i + 1) * height, (x * width):(x + 1) * width]

            # Kırpılan kısım trash dosyasına satır ve kolon sayısı şeklinde kaydedilir.
            cv2.imwrite("trash/img{}-{}.jpg".format((i + 1), (x + 1)), imgCrop)

            # Bu kaydedilen kısım tekrardan bir değişkene aktarılır.
            image = cv2.imread("trash/img{}-{}.jpg".format((i + 1), (x + 1)))

            print(("img{}-{}.jpg".format((i + 1), (x + 1)))," FOTOĞRAF PARÇASI İNCELENİYOR.")


            show_width = int(img.shape[1] / dividedPiecesWidth)
            show_height = int(img.shape[0] / dividedPiecesHeight)

            showimg = cv2.rectangle(imgyedek, (((x)*show_width), ((i)*show_height)),(((x+1)*show_width), ((i+1)*show_height)), (0, 0, 255), 25)
            showimg_resized_up = cv2.resize(showimg, (750, (int((750*img.shape[0])/img.shape[1]))), interpolation=cv2.INTER_LINEAR)
            cv2.imshow("showimg", showimg_resized_up)
            cv2.waitKey(1)

            # Fotoğraflarımızın pikselleri farklı olabilir. Bu yüzden fotoğraf parçalarının pikselleri değişsede
            # Tüm fotoğraf parçaları 600e 6xx şeklinde incelenir.
            up_width = 600
            up_height = int((up_width * height) / width)
            up_points = (up_width, up_height)
            resized_up = cv2.resize(image, up_points, interpolation=cv2.INTER_LINEAR)

            # Tekrardan boyutlandırılan fotoğraf parçası  önceden kaydedilen fotoğrafın üstüne kaydedilir.
            cv2.imwrite("trash/img{}-{}.jpg".format((i + 1), (x + 1)), resized_up)



            # Kaydedilen bu fotoğraf detectFromImage fonksiyonuna yollanır.
            coordinates = detectFromImage(("trash/img{}-{}.jpg".format((i + 1), (x + 1))))

            #  Fotoğraf parçası kaydedildikten sonra siliniyor.
            time.sleep(0.2)

            try:
                os.remove("trash/img{}-{}.jpg".format((i+1), (x+1)))
            except:
                pass

            # İncelenen fotoğraf PARÇASININ bulunan bina sayısı değişkeni
            current_NOfBuilding = 0


            # Fonksiyondan dönen listedeki, fotoğraf koordinatlarını tek tek incelenmesi.
            for coordinate in coordinates:

                current_NOfBuilding += 1
                number_OfBuilding += 1
                total_building += 1


                # Tespit edilen binaların fotoğraf koordinatları 600px'lik karelere göredir.
                # Burada ise 600px'lik karelerde tespit edilen fotoğraf koordinatlarını,
                # yeniden boyutlandırılmadan önceki fotoğraf parçamızda hangi piksellere denk geldiğini buluruz.
                xa = float(((img.shape[1] / dividedPiecesWidth) * coordinate[0]) / up_width)
                ya = float(((img.shape[0] / dividedPiecesHeight) * coordinate[1]) / ((up_height * height) / width))


                # Tespit edilen binaların kaçıncı satırda ve kaçıncı kolonda olduğuna göre ANA fotoğrafımızda
                # yer tespiti yapmamıza yarar.
                # (Eğer 3.satır 5. kolondaysak ve her bir fotoğraf parçamızın pikseli 250px ise
                #  a+(5*250) , b+(3*250) eşitliklerini yaparak yapılarımızın ANA fotoğraftaki
                #  koordinatını(hangi pikselde olduğunu) tespit ederiz.)
                xc = xa + (x * width)
                yc = ya + (i * height)


                # HEİGHT İÇİN
                FS_long = firstLongPoint - secondLongPoint  # 1. ve 2. Koordinatların BOYLAM farkını bulmak
                FS_lat = firstLatPoint - secondLatPoint  # 1. ve 2. Koordinatların ENLEM farkını bulmak

                # 1. Kısım fotoğrafta 1 piksel yukarı ve aşağı hareket edersek BOYLAMDA ne kadar değişlik olduğunun hesabı
                # 2. Kısım ise fotoğraf parçasında tespit edilen binaların y koordinatı(Fotoğraf koordinatı)
                #               1.KISIM               2. KISIM
                heightPxLong = (FS_long / img.shape[0]) * yc

                # 1. Kısım fotoğrafta 1 piksel yukarı ve aşağı hareket edersek ENLEMDE ne kadar değişlik olduğunun hesabı
                # 2. Kısım ise fotoğraf parçasında tespit edilen binaların y koordinatı(Fotoğraf koordinatı)
                 #               1.KISIM              2. KISIM
                heightPxLat = (FS_lat / img.shape[0]) * yc


                heightPxLong1 = (FS_long / img.shape[0])
                heightPxLat1 = (FS_lat / img.shape[0])


                # WİDTH İÇİN
                FF_long = firstLongPoint - fourthLongPoint  # 1. VE 4. KOORDİNATLARIN BOYLAM FARKINI BULMAK
                FF_lat = firstLatPoint - fourthLatPoint  # 1. VE 4. KOORDİNATLARIN ENLEM FARKINI BULMAK

                # 1. Kısım fotoğrafta 1 piksel sağa ve sola hareket edersek BOYLAMDA ne kadar değişlik olduğunun hesabı
                # 2. Kısım ise fotoğraf parçasında tespit edilen binaların x koordinatı(Fotoğraf koordinatı)
                #               1.KISIM               2. KISIM
                widthPxLong = (FF_long / img.shape[1]) * xc

                # 1. Kısım fotoğrafta 1 piksel sağa ve sola hareket edersek ENLEMDE ne kadar değişlik olduğunun hesabı
                # 2. Kısım ise fotoğraf parçasında tespit edilen binaların x koordinatı(Fotoğraf koordinatı)
                #               1.KISIM               2. KISIM
                widthPxLat = (FF_lat / img.shape[1]) * xc


                widthPxLong1 = (FF_long / img.shape[1])
                widthPxLat1 = (FF_lat / img.shape[1])


                # BİNA GENİŞLİĞİ (X METRE * img.shape[1]) / lengthFirstFourth)
                katsayiWidth = (12 * img.shape[1]) / lengthFirstFourth

                # BİNA BOYU (X METRE * img.shape[0]) / lengthFirstSecond)
                katsayiHeight = (12 * img.shape[0]) / lengthFirstSecond


                # Tespit edilen binanın Boylamının hesaplanması
                LONG = (firstLongPoint - heightPxLong - widthPxLong)

                # Tespit edilen binanın Enleminin hesaplanması
                LAT = (firstLatPoint - heightPxLat - widthPxLat)


                # Hesaplanan koordinatlar 'sql' fonksiyonumuza gönderilir.

                # sql(LONG, LAT)


            print(f"BU PARÇADA TOPLAM {current_NOfBuilding} ADET YAPI TESPİT EDİLMİŞTİR.")
            print("------------------------------------------------------------------")
            time.sleep(0.1)



    print(f" {z}. Fotoğrafta Toplam {number_OfBuilding} Adet Yapı Tespit Edilmiştir...")
    print("------------------------------------------------------------------")
    print(f"Toplam {total_building} Adet Yapı Tespit Edilmiştir...")
    time.sleep(4)
    print("------------------------------------------------------------------")

