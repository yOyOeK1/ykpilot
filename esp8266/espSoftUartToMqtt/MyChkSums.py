
def getChkSum(msg):
    value = 0
    for c in msg:
        value ^= ord(c)
    return str(hex( value & 255 ))[2:]

def chkSumChk(msg):
    mi = msg.rfind('*')
    lChkSumOk = False
    lGotChkSum = False
    chkSum = None
    if mi != -1:
        try:
            chkSumStr = msg[mi+1:]
            if len(chkSumStr)>0:
                lGotChkSum = True
            
            chkSum =  getChkSum(msg[:mi])
            if lGotChkSum and chkSumStr == chkSum:
                #print("chkTest",chkSumStr," <=> ",chkSum," OK")
                lChkSumOk = True
            else:
                print("chkSumEr ",chkSumStr,"!=",chkSum)#msg)
                return [False,msg]
        except:
            pass
        
        if lChkSumOk:
            return [True,msg[:mi]]
        #elif lGotNo and self.lGotChkSum:
        #    self.nChkEr+=1
            
    
    return [False,msg]
