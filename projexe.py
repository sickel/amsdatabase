proj="c:\\program files\\qgis 2.18\\bin\\proj.exe"
#proj="c:\\windows\\notepad.exe"
from subprocess import Popen, PIPE
import shlex,subprocess
import os

env=os.environ.copy()
env["PROJ_LIB"]="c:\\OSGeo4W64\\share\\proj"
#print(env)
params= ["+proj=utm","+zone=11"]
args=[proj]
args.extend(params)
print(args)
process = Popen(args,shell=True,env=env,stdin=PIPE,stdout=PIPE)
coords=['-116 30','-116.5 30.2']
for c in coords:
    print(c)
    out=process.communicate(input=c.encode())[0]
    print(out.decode())
#(output, err) = process.communicate()
#exit_code = process.wait()
#print(exit_code)

#subprocess.call(call)