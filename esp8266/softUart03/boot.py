from machine import Pin,SOFTUART;   
import time

print('-')
print("delay start of softuart to flash ardiuno with connected wires")
time.sleep(10)
print("softuart...")

pLed = Pin(2,Pin.OUT);
pLed.off()
time.sleep(1)
pLed.on()

s = SOFTUART(tx=12,rx=14,baudrate=115200)   # default tx=14,rx=12,baudrate=115200
print("DONE")



dir(s)
iter = 0
buf = ""
while True:
    
    if iter > 40000:
        print(">")
        s.write('nodeMCU say hello :)\n')
        iter = 0
    
    
    c = s.getcount()    
    if c > 0:
        while True:
            res = s.get()
            if res == 0:
                break
            else:
                buf+= chr(res)
                if len(buf)>=64:
                    buf = ""
        if buf[-1] == "\n":
            buf = buf[:-1]
            print("buf",buf)
            
            buf = ""
           
    iter+=1   
