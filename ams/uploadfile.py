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
        print(self.finished)
    
    
    def importdata(self):
        with open(self.filename,'r') as csvfile:
            csvreader = csv.reader(csvfile,delimiter=",")
            i= 0
            header=[]
            for row in csvreader:
                i=i+1
                print(i,":","_".join(row))
                if i==3:
                    header=row
                    # Analyze header to see that all that is needed is there...
                if i>3:
                    pass
                    # insert data...
                    
        # location="geometry::STGeomFromText('POINT ("+str(sample["LONGITUDE"])+" "+str(sample["LATITUDE"])+")',4326)"