import threading
import time


class Tmr():
    elap=0
    def __init__(self):
        self.paused = False
        self.rset = False
        self.preset = 0
        self.remaining = 0
        return
    
    def run(self,value):
        self.preset = value
        self.paused = False
        self.rset = False
        print(f'Play timer started with {self.preset} seconds')
        t = threading.Thread(target=self.__run__)
        t.start()
        return
    
    def reset(self):
        self.rset = True
        return


    def pause(self):
        self.paused = True
        return
    
    def resume(self):
        self.paused = False
        return
        
    
    def __run__(self):
    
        while Tmr.elap < self.preset:
            time.sleep(1)
            if self.paused == False:
                Tmr.elap = Tmr.elap +1
                self.remaining = self.preset - Tmr.elap
            #print (Tmr.elap)
            if self.rset == True:
                self.paused = False
                self.preset = 0
                Tmr.elap = 0
                self.rset == False
                break

        if Tmr.elap >= self.preset:
            self.preset = 0
            Tmr.elap = 0
            print ('Song End')
    





