import os
import sys
import threading

sys.path.insert(0, "modules/")

dir = os.listdir("modules/")
for mod in dir:
    if mod != ".DS_Store" and ".pyc" not in mod:
        _mod = __import__(mod.replace(".py", ""))
        print "Loaded " + mod.replace(".py", "")  + ", version " + _mod.moduleVersion() + " by " +  _mod.moduleAuthor()
        _mod.moduleInit()
        
        modThread = threading.Thread(target=_mod.moduleRun())
        modThread.start()
        
def sendArduinoMessage(mssg):
    print "Function not implimented!"