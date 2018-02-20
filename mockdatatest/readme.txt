SYMANTEC VIP REAL-TIME TRANSACTION REPORTING SERVICE (BETA) REFERENCE CLIENT README
---------------------------------------------------------------------

The VIP Real-time Transaction Reporting Service reference client 
provides an out-of-the-box means for capturing events logged by the 
VIP Service. The reference client periodically polls the VIP Service 
for event logs, writes them to a location where your logging service 
can access them.


CONTENTS
--------

This package contains the following files and structure:

+ referenceclient.jar (executable .jar file)
+ client.properties (configuration file)
+ TailEvents.class (wrapper script)
+ TailEvents.java
+ Readme.txt (this document)


PREREQUISITES
-------------

The VIP Real-time Transaction Reporting Service reference client 
requires the following:

+ Oracle JRE 1.8. You must have JAVA in your path.
+ Internet access (to access the reporting server)
+ Ability to access your file system (to write logs)

While we expect that the reference client will run on any machine that 
meets these requirements, Symantec has tested the reference client on 
the following platforms: 

+ Windows 7 and Windows 10 running Splunk version XYZ on a VM instance
+ macOS X El Capitan (10.11) and Sierra (10.12) running Splunk version 
XYZ on a VM instance

Note that your logging service may impose additional requirements. 
Refer to the documentation provided with your service for details.

INSTALLING AND USING THE REFERENCE CLIENT
-----------------------------------------

Full instructions for installing and using the VIP Real-time 
Transaction Reporting Service reference client are available at 
http://help.symantec.com/home/VIP_Reporting_Service_Beta?locale=EN_US.


KNOWN ISSUES AND WORKAROUNDS
----------------------------

None at this time.