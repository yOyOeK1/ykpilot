from machine import SOFTUART;   
import time

print('-')
time.sleep(2)
print("softuart...")
s = SOFTUART(tx=12,rx=14,baudrate=115200)   # default tx=14,rx=12,baudrate=115200
print("DONE")



dir(s)
iter = 0
buf = ""
while True:
    
    if iter > 40000:
        print(">")
        s.write('nodeMCU say hello :)\n')
        #s.wait(10000)      # wait rx for 10000us,default is 10000us 
        #time.sleep(0.1)
        iter = 0
    iter+=1   
    #s.isoverflow()     # rx buf is overflow?
    c = s.getcount()      # rx buf available number   
    #print("c",c," s",s.get())          # pop a byte from rx buf, if none return 0
    if c > 0:
        while True:
            res = s.get()
            if res == 0:
                break
            else:
                buf+= chr(res)
                if len(buf)>=64:
                    buf = ""
        #print(str(res))
        if buf[-1] == "\n":
            buf = buf[:-1]
            print("buf",buf)
            
            buf = ""
           
    #s.getall()
    
    #time.sleep(.001)  