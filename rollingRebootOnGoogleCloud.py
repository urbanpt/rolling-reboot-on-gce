#! /usr/bin/env python
"""rollingRebootsOnGooGleCloud.py: reboots one instance at a time in an 
instance Group on Google Compute Engine and waits for HTTP 200 response before rebooting the next instance """

__author__ = "Samuel Martins"

__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Samuel Martins"

import json
import re
import time
import sys
from httplib2 import Http
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.discovery import build

credential_email=""
privateKeyPath=""
instanceGroup=""
project=""
zone=""
minInstanceUpdateTimeSec=200
instanceStartupTimeoutSec=100

def waitForHealthCheck( ip ):
   h = Http()
   respok = False
   i=0
   maxRetries=instanceStartupTimeoutSec/10 
   print "Waiting for app wakeup"
   while (respok == False and i < maxRetries):
      try:
          resp, content = h.request("http://"+ip+"/login", "GET")
          respok = resp.get('status')
      except:
          respok = False

      if respok == '200':
	 print "got good response ("+respok+")"
         return True
      else:
         i+=1
      sys.stdout.write("\rRetrying (%d)" % i)
      sys.stdout.flush()
      time.sleep(10)
   return False


with open(privateKeyPath) as f:
  private_key = f.read()

scope = ['https://www.googleapis.com/auth/replicapool','https://www.googleapis.com/auth/cloud-platform']
credentials = SignedJwtAssertionCredentials(credential_email, private_key, scope)

http = Http()
credentials.authorize(http)
instanceGroups = build('resourceviews','v1beta2',http=http)
response = instanceGroups.zoneViews().get(project=project,zone=zone,resourceView=instanceGroup).execute()

machines = response.get('resources')
for machine in machines:
   machineUpdating = re.sub(r"^.*/","",machine)
   print "Updating "+machineUpdating+"..."
   compute = build('compute','v1',http=http)
   response = compute.instances().reset(project=project,zone=zone,instance=machineUpdating).execute()
   response = compute.instances().get(project=project,zone=zone,instance=machineUpdating).execute()
   ip=response.get('networkInterfaces')[0].get('accessConfigs')[0].get('natIP')
   j=instanceStartupTimeoutSec
   while (j>0):
     sys.stdout.write("\rWaiting %d seconds while it's rebooting   " % j)
     sys.stdout.flush()
     time.sleep(1)
     j-=1
   sys.stdout.write("\r\n")
   sys.stdout.flush()
   result=waitForHealthCheck(ip)
   if(result == False):
     print("Rolling update stopped: "+machineUpdating+" did not wakeup")
     sys.exit(1)

print("Rolling update succeeded")
sys.exit(0)
