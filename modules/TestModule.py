import sys
import os
import Queue
import time

##API##
#Note: All functions must be implimented and must retain standard arguments.
#If a module fails to do this, it will not be loaded.
#
#sendArduinoMessage(moduleName, mssg) - Sends a message to the connected Arduino board.
#addMetric(key, value, mod) -  Adds a metric to the FishTank, accessable to all modules.
#getMetric(key, value, mod) - Gets a metric from the FishTank about the module <mod>
#sendError(error, level, mod) - Reports an error that occured in the module. 
#log(mod, mssg) - Prints a message to the main console
#registerSMSCommand(cmd, func) - Adds an SMS command to the list. 'cmd' is the command string and 'func' is the function
#
#Error Levels:
#   error["eWarning"] - An error that causes little to no harm
#   error["eStandard"] - An error that will likely cause harm if left unchecked for a long period of time
#   error["eCritical"] - An error that will trigger an SMS message, an error that must be corrected immediatly

#Example module below says hello to the arduino ane expects it to say hi back

addMetric = None
getMetric = None
sendError = None
sendArduinoMessage = None
error = None
log = None
registerSMSCommand = None
incomingQueue = Queue.Queue()

#Initialize the module, must not cause a lock
def moduleInit(am, gm, se, sam, lg, rc, errs): 
    #Do not modify below#
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    registerSMSCommand = rc
    #Do not modify above#
    
    log(moduleName(), "Test init completed")
    registerSMSCommand("yum", eatPie)

#Run the module, usually a loop  
def moduleRun(am, gm, se, sam, lg, rc, errs):
    #Do not modify below#
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    registerSMSCommand = rc
    #Do not modify above#
    
    log(moduleName(), "Test run started")
    
    #Test for WebUI
    addMetric("TestMetric", "TestValue", moduleName())
    sendError("Something bad happened!", error["eCritical"], moduleName())
    
    #Add your main loop code below
    while True:
        i = 0
        while i < incomingQueue.qsize():
           mssg = incomingQueue.get()
           if (mssg == "hi"):
               log(moduleName(), "Yay the arduino says hi!")
           incomingQueue.task_done()
       
        time.sleep(10)
        sendArduinoMessage(moduleName(), "sayHiArduino")
       
    
#Returns the author of the module    
def moduleAuthor():
    return "John Smith"
    
#Returns the name of the module    
def moduleName():
    return "TestModule"
    
#Returns the module verison
def moduleVersion():
    return "0.1"

#Returns a descripton of the module    
def moduleDescription():
    return "A test module"

#Called when the module is stopped
def stopModule(log):
    sendArduinoMessage(moduleName(), "sayByeToArduino")
    log(moduleName(), "Module Stopped")
    
def eatPie():
    return "Eat pie!"