import hashlib
from .dbconnector import *
import csv


class csvfile:


    def calcmd5sum(self, blocksize=65536):
        hash = hashlib.md5()
        with open(self.filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        self.md5=hash.hexdigest()

    def __init__(self,filename,req):
        self.db=dbconnector()
        self.db.connecttodb()
        self.req=req
        self.filename=filename
        self.calcmd5sum()
        print(req)
        print(self.md5)
        print(self.filename)
        sql="select finished from datafile where filename=? and md5=?"
        self.db.cursor.execute(sql,[self.filename,self.md5])
        res=self.db.cursor.fetchall()
        print(res)
        if len(res)==0:
            sql="insert into datafile (filename,md5,surveyid) values(?,?,?)"
            self.db.cursor.execute(sql,[self.filename,self.md5,req['survey'][0]])
            self.db.cursor.commit()
        self.finished= True in res
        #print(self.finished)
        #print(req['VD1'][0])
        #print(req['VD2'][0])
    
    
    def importdata(self):
        sql = "select id from datafile where filename=? and md5=?"
        self.db.cursor.execute(sql,[self.filename,self.md5])
        fileid=self.db.cursor.fetchall()[0][0]
        with open(self.filename,'r') as csvfile:
            breaking = True
            breaking = False
            csvreader = csv.reader(csvfile,delimiter=",")
            i= 0
            header=[]
            insert="insert into measurement(datafileid,seqnum,systemtime,aqutimeus,GPSSmplFlags,GpsError,GpsTime,PDOP,longitude,\
            latitude,GPSAltitude,LineNum,adc1,adc2,temp,press,location) \
            values(?,?,convert(datetime,?,103),?,?,?,convert(datetime,?,103),?,?,?,?,?,?,?,?,?,geometry::STGeomFromText('POINT ({} {})',4326))"
            vds=['VD1','VD2','VD3','VD4']
            for row in csvreader:
                i=i+1
                if i==2:
                    top=row
                    if not "GPS Sample" in top:
                        print(top)
                        print("No GPS data")
                        break # Makes no sense to continue if no GPS data
                    roistarts=[i for i, s in enumerate(top) if 'ROI for Virtual Detector' in s]
                    spectrumstarts = [i for i, s in enumerate(top) if 'Spectrum VD' in s]
                    vdstart = [idx for idx, s in enumerate(top) if '[1]' in s][0]
                    print(roistarts)
                    print(spectrumstarts)
                    print(vdstart)
                    print("===")
                if i==3:        
                    header=row
                    meashead=dict(zip(header[0:vdstart],range(0,vdstart)))
                    print(meashead)
                    insert="insert into measurement(datafileid,seqnum,systemtime,aqutimeus,GPSSmplFlags,GpsError,GpsTime,PDOP,longitude,latitude,GPSAltitude,LineNum"
                    values=" values(?,?,convert(datetime,?,103),?,?,?,convert(datetime,?,103),?,?,?,?,?"
                    adcs=False
                    pres=False
                    if "ADC 1" in  header:
                        insert=insert+",adc1,adc2"
                        values=values+",?,?"
                        adcs=True
                    if "Pres" in header:
                        insert=insert+",Pres,Temp"
                        values=values+",?,?"
                        pres=True
                    insert=insert+",location) "+values+",geometry::STGeomFromText('POINT ({} {})',4326)) "
                    # Analyze header to see that all that is needed is there...
                if i>3:
                    lon=row[meashead["Long"]]
                    lat=row[meashead["Lat"]]
                    
                    params=[fileid]
                    params.append(row[meashead["SeqNum"]]) 
                    params.append(row[meashead["UtcDate"]]+" "+row[meashead["UtcTime"]]) 
                    params.append(row[meashead["µs"]])
                    
                    # nothing in row[4]
                    params.append(row[meashead["SmplFlags"]])
                    params.append(row[meashead["GpsError"]]) 
                    params.append(row[meashead["GpsUtcDate"]]+" "+row[meashead["GpsUtcTime"]]) 
                    params.append(row[meashead["PDOP"]]) 
                    params.append(lon)
                    params.append(lat)
                    params.append(row[meashead["Alt[m]"]])
                    params.append(row[meashead["LineNum"]]) 
                    if adcs:
                        params.append(row[meashead["ADC 1"]])
                        params.append(row[meashead["ADC 2"]])
                    if pres:
                        params.append(row[meashead["Pres"]])
                        params.append(row[meashead["Temp"]])
                    
                    params = list(map(lambda x: 0 if x == '' else x, params))
                    self.db.cursor.execute(insert.format(lon,lat),params)
                    self.db.cursor.execute("select IDENT_CURRENT('measurement')")
                    id=self.db.cursor.fetchall()
                    measid=id[0][0]
                    print(measid)
                    for vd in vds:
                        if self.req[vd][0]=='':
                            continue
                        vd=int(self.req[vd][0])
                        roi=roistarts[vd-1]
                        params=[measid]
                        params.append(row)
                        break # Jumps out if no data for this VD
                if i > 10 and breaking:
                    break
            self.db.cursor.commit()        
        # location="geometry::STGeomFromText('POINT ("+str(sample["LONGITUDE"])+" "+str(sample["LATITUDE"])+")',4326)"