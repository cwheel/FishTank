import sys
import os

#Initialize the module, must not cause a thread lock
def moduleInit(): 
    print "Test init completed"

#Run the module, usually a loop  
def moduleRun():
    sendArduinoMessage("hello")
    print "Test run started"
    
#Returns the author of the module    
def moduleAuthor():
    return "Test"
    
#Returns the module verison
def moduleVersion():
    return "0.1"

#Returns a descripton of the module    
def moduleDescription():
    return "A test module"
    
#Called when a connected Arduino board delivers serial data with to the module
def incomingArduinoMessage(mssg):
    print "Serial message recived: " + mssg