import hashlib
from .dbconnector import *
import csv
import configparser

from subprocess import Popen, PIPE
import os


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
#print(env)
        self.projparams= ["+proj=utm","+zone="+self.req['UTMzone'][0]]
        print(self.projparams)
        config=configparser.ConfigParser()
        config.read('database.ini')
        self.proj=config['projection']['proj']
        print(self.proj)
        #print(self.finished)
        #print(req['VD1'][0])
        #print(req['VD2'][0])
    
    
    def importdata(self):
        env=os.environ.copy()
        env["PROJ_LIB"]="c:\\OSGeo4W64\\share\\proj"

        sql = "select id from datafile where filename=? and md5=?"
        self.db.cursor.execute(sql,[self.filename,self.md5])
        fileid=self.db.cursor.fetchall()[0][0]
        args=[self.proj]
        args.extend(self.projparams)

        with open(self.filename,'r') as csvfile:
            breaking = True
            breaking = False
            csvreader = csv.reader(csvfile,delimiter=",")
            i= 0
            header=[]
            insmeas="insert into detectormeasure (measurementid,vd,ndet, livetime, rawdose, dose,totcount,spectra) values(?,?,?,?,?,?,?,?) "
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
                    try:
                        specchs=spectrumstarts[1]-spectrumstarts[0]
                    except IndexError as error:
                        specchs=1025 # Must be one extra
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
                    if "ADC 1" in  header: # ADCs - for altitude measurement May or may not be exported
                        insert=insert+",adc1,adc2"
                        values=values+",?,?"
                        adcs=True
                    if "Pres" in header: # Pressure and temperature
                        insert=insert+",Pres,Temp"
                        values=values+",?,?"
                        pres=True
                    #insert=insert+",location,location_utm) "+values+",geometry::STGeomFromText('POINT ({} {})',4326),geometry::STGeomFromText('POINT ({})',32633)) "
                    insert=insert+",location_utm) "+values+",geometry::STGeomFromText('POINT ({})',32633)) "
                    # Analyze header to see that all that is needed is there...
                if i>3:
                    store=False
                    for vd in vds:
                        if self.req[vd][0]=='':
                            continue
                        vd=int(self.req[vd][0])
                        store=store or int(row[roistarts[vd-1]]) > 0
                    # no reason to store data where the detector not yet is up
                    if not store:
                        continue
                    lon=row[meashead["Long"]]
                    lat=row[meashead["Lat"]]
                    projcoord=lon+" "+lat+""
                    projcoord=projcoord.encode()
                    process = Popen(args,env=env,stdin=PIPE,stdout=PIPE)
                    utmcoord=process.communicate(input=projcoord)[0].decode()
                    if breaking:
                        print(projcoord)
                        print(utmcoord)
                    process.kill()
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
                    #self.db.cursor.execute(insert.format(lon,lat,utmcoord),params)
                    self.db.cursor.execute(insert.format(utmcoord),params) # Using format to insert coordinates in the Geom from text - normal parameters do not work here
                    self.db.cursor.execute("select IDENT_CURRENT('measurement')") # Get last id - may fail 
                    id=self.db.cursor.fetchall()
                    measid=id[0][0]
                    if i%100==0:
                        print(i,measid)
                    for vd in vds:
                        if self.req[vd][0]=='':
                            continue
                        vd=int(self.req[vd][0])
                        roi=roistarts[vd-1]
                        params=[measid,vd]
                        params.extend(row[roi:roi+5]) # DetCount, LiveTime, Raw Doserate, Doserate TotCount[cps]
                        specst=spectrumstarts[vd-1]
                        spectrum=":".join(row[specst:specst+specchs])
                        params.append(spectrum)
                        # print("VD"+str(vd))
                        self.db.cursor.execute(insmeas,params)
                        #break # Jumps out if no data for this VD
                if i > 10 and breaking:
                    break
            sql="update datafile set finished = 1 where id = ?"
            self.db.cursor.execute(sql,fileid)
            self.db.cursor.commit()
            message="Uploaded OK"
            return(message)
        # location="geometry::STGeomFromText('POINT ("+str(sample["LONGITUDE"])+" "+str(sample["LATITUDE"])+")',4326)"