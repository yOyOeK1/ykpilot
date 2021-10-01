
import time
import os

print("dump dummy tcp sender...")

everySec = 1
ip = "localhost"
port = 19999
packs = [
    "{'adcNice':{'b 0 Gnd':  {'raw':507,'correct':509,'volts':-3.52},'b 0 +  ':  {'raw':535,'correct':531,'volts':22.27},'b 1 +':  {'raw':555,'correct':554,'volts':49.22},'outStage 1':  {'raw':530,'correct':531,'volts':22.27},'outStage 2':  {'raw':527,'correct':531,'volts':22.27}}}",
    "{'batMux':{'battery selected':0,'output relay':1,'b0g':507,'b01':535,'b1p':554}}"
    ]


print("got ",len(packs)," packages to send will send in ",everySec," sec.")
print("ip:",ip," port:",port)
iter = 0
while( True ):
    print('iter:',iter)
    iter+=1
    
    for p in packs:
        cmd = "echo 'du>yk:{0}' | nc -w1 {1} {2}".format(
            p.replace("'","\""),
            ip,
            port
            )
        #print("[[        ",cmd,"    ]]")
        os.system( cmd )
    time.sleep(everySec)