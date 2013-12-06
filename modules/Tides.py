import sys
import os
import Queue
import time
import datetime
import urllib2
import re

addMetric = None
getMetric = None
sendError = None
sendArduinoMessage = None
error = None
log = None
registerSMSCommand = None
incomingQueue = Queue.Queue()

def nextTide(id):
    req = urllib2.Request('http://tidesnear.me/tide_stations/' + id)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36')
    
    _forecast = urllib2.urlopen(req)
    forecast = _forecast.read()
    forecast = forecast.replace("\n", "")
    fetchedData = re.compile("<h3>Next Tide:.*?</div>").search(forecast).group()
    
    nextTide = re.compile("<h3>Next Tide: .*</h3>").search(fetchedData).group().replace("<h3>Next Tide: ", "").replace("</h3>", "")
    timeTo = re.compile("'from-now'>.*</p>").search(fetchedData).group().replace("'from-now'>", "").replace("</p>", "").replace("  hours, ", ":").replace(" minutes from now", "").replace("  hour, ", ":")
    
    return [nextTide, timeTo]

def ts2s(ts):
    s = 0
    s = s + int(ts.split(":")[0]) * 60 * 60
    s = s + int(ts.split(":")[1]) * 60
    return int(s)
    
def moduleInit(am, gm, se, sam, lg, rc, errs): 
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    registerSMSCommand = rc
    
    log(moduleName(), "Tides init completed")

def moduleRun(am, gm, se, sam, lg, rc, errs):
    addMetric = am
    getMetric = gm
    sendError = se
    sendArduinoMessage = sam
    error = errs
    log = lg
    registerSMSCommand = rc
    
    while True:
        i = 0
        while i < incomingQueue.qsize():
           mssg = incomingQueue.get()
           incomingQueue.task_done()
           
        tide = nextTide("1799")
            
        if tide[0] == "Low":
            sendArduinoMessage(moduleName(), "tideslow")
            addMetric("Tide", "Low", moduleName())
        elif tide[0] == "High":
            sendArduinoMessage(moduleName(), "tideshigh")
            addMetric("Tide", "High", moduleName())
        
        log(moduleName(), "Sleeping for " + str(ts2s(tide[1]) + 80) + " seconds until next tide.")    
        time.sleep(ts2s(tide[1]) + 80)
       
        
def moduleAuthor():
    return "nosedive25"
    
def moduleName():
    return "Tides"
    
def moduleVersion():
    return "0.1"

def moduleDescription():
    return "Simulates tides on a Fiji schedule"

def stopModule(log):
    log(moduleName(), "Module Stopped")