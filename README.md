FishTank
========

FishTank Core

**What is it?**

A quickly built Python script intended to run on a Rasberry Pi with the mission of controlling a fish tank (Mostly works! About that messy code...). FishTank Core enables the user to build and manage seperate modules for each part of the tank (Pumps, thermometers, lights etc.). FishTank Core provides a plethora of convinient functions for talking to an Arduino board, sending SMS messages (Fancy emails) and reporting data.

**Module API**

- sendArduinoMessage(moduleName, mssg) - Sends a message to the connected Arduino board.
- addMetric(key, value, mod) -  Adds a metric to the FishTank, accessable to all modules.
- getMetric(key, value, mod) - Gets a metric from the FishTank about the module <mod>
- sendError(error, level, mod) - Reports an error that occured in the module. 
- log(mod, mssg) - Prints a message to the main console
- registerSMSCommand(cmd, func) - Adds an SMS command to the list. 'cmd' is the command string and 'func' is a function

Error Levels:
   - error["eWarning"] - An error that causes little to no harm
   - error["eStandard"] - An error that will likely cause harm if left unchecked for a long period of time
   - error["eCritical"] - An error that will trigger an SMS message, an error that must be corrected immediatly


**Example**

See TestModule.py for a quick example module
