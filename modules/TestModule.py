import sys
import os
import Queue

##API##
#Note: All functions must be implimented and must retain standard arguments.
#If a module fails to do this, it will not be loaded.
#
#sendArduinoMessage(mssg) - Sends a message to the connected Arduino board. You MUST impliment the writeLock to prevent concurrent usage of this function!
#addMetric(key, value, mod) -  Adds a metric to the FishTank, accessable to all modules.
#getMetric(key, value, mod) - Gets a metric from the FishTank about the module <mod>
#sendError(error, level, mod) - Reports an error that occured in the module. 
#log(mod, mssg) - Prints a message to the main console
#
#Error Levels:
#   error[eWarning] - An error that causes little to no harm
#   error[eStandard] - An error that will likely cause harm if left unchecked for a long period of time
#   error[eCritical] - An error that will trigger an SMS message, an error that must be corrected immediatly

addMetric = None
getMetric = None
sendError = None
sendArduinoMessage = None
error = None
log = None
incomingQueue = Queue.Queue()

#Initialize the module, must not cause a lock
def moduleInit(am, gm, se, sam, lg, errs): 
    #Do not modify below#
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    #Do not modify above#
    
    log(moduleName(), "Test init completed")

#Run the module, usually a loop  
def moduleRun(am, gm, se, sam, lg, errs):
    #Do not modify below#
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    #Do not modify above#
    
    log(moduleName(), "Test run started")
    
    #Add your main loop code below
    while True:
        pass
    
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
def stopModule():
    pass