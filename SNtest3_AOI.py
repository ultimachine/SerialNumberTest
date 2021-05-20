#!/usr/bin/env python

# test if barcode in correct production run and passed testing
# tell with how many boards found total and by user


import os
import sys
import traceback
import string
import subprocess
import psycopg2
from colorama import init
from termcolor import colored, cprint
import winsound
import pyttsx3

# terminal init for windows
init()
goodfrequency = 2500
goodduration = 1000

say = pyttsx3.init()
say.setProperty('rate', 100) #250
voices = say.getProperty('voices')
say.setProperty('voice', voices[1].id)

print ("Test serial for run")
directory = os.path.split(os.path.realpath(__file__))[0]


print ("Connecting to database...")
dbfile = open(directory+'/postgres_info.txt', 'r')
postgresInfo = dbfile.read()
dbfile.close()
try:
  testStorage = psycopg2.connect(postgresInfo)
  print ("Connect success.")
except:
  print ("Could not connect!")
  sys.exit(0)


state = "testing"
runId = '-1'
pcbFab = 'fineline'
tstuser = '1'

# get user name from terminal --commented to hard code single user for now
#tstuser= '-1'
#while tstuser == '-1':
#  print ("\nEnter User ID : ")
#  tstuser = input()
#  if tstuser == 'exit':
#    sys.exit(0)
  

# get runId number from terminal
while runId == '-1':
  print ("\nEnter Run ID : ")
  runId = input()
  if runId == 'exit':
    sys.exit(0)
  print ("\nEnter PCB Fab Name")
  pcbFab = input()

  print ("\nEnter already shipped")
  shipped = input()

while (state == 'testing'):
  #setup database
  conn = psycopg2.connect(postgresInfo)
  cur = conn.cursor()
  
  #output run quantity
  cur.execute("""SELECT COUNT(*) FROM tempserialtest WHERE runid = %s""",(runId,))
  cnt = cur.fetchone()
  countint = cnt[0]
  count = str(countint)
  print("RunCount " + count + " - Run: " + runId + " - User: " + tstuser)  
  boxcount = str( int(count) - int(shipped) )
  print("BoxedCount " + boxcount )
  say.say(boxcount)
  
  f = open("boxedcount.txt", "r+")
  f.seek(0)
  f.write(boxcount)
  f.truncate()
  f.close()
  
  '''
  tens = count[-2:]
  if tens[-1:] == "0":
    if tens == "00":
      say.say(count)
    else:
      say.say(tens)
  '''
  say.runAndWait()
  conn.commit()
  
  
  # get serial number from terminal
  print ("\nEnter serial number : ")
  serialNumber = input()
  if serialNumber == 'exit':
    sys.exit(0)
	
  # get count of matching serial numbers from test database
  cur.execute("""SELECT serial FROM testdata WHERE productionrunid = %s AND testresults LIKE 'Passed' AND serial = %s""",(runId,serialNumber))
  rows = cur.fetchall()
  runcount = len(rows)
  
  # print results
  if runcount > 0:
    # check for found in already found boards
    cur.execute("""SELECT time FROM tempserialtest WHERE serialnumber = %s""",(serialNumber,))
    rows = cur.fetchall()
    foundcount = len(rows)
	
	
    if foundcount > 0:
      # board already in added to this shipment
      print (colored("Error! " + serialNumber + " Already Found and in shipment table!!!!",'white','on_yellow'))
      winsound.Beep(500, 1500)
      winsound.Beep(800, 1000)
      for row in rows:
        print(str(row[0]))
      conn.commit()
      cur.close()
	
    else:
    # write found board serial number to temp table
      insertquery = """INSERT INTO tempserialtest (serialnumber, tstuser,runid, pcbfab) VALUES (%s, %s, %s, %s)"""
      cur.execute(insertquery,(serialNumber,tstuser,runId,pcbFab))
      conn.commit()
      cur.close()

      print (colored("Found "+ serialNumber,'white','on_green'))
      newcount = countint + 1
      if str(newcount)[-1:] == "0":
        winsound.Beep(3000, 800)
      else:
        winsound.Beep(2100, 800)

      
  # No test results found
  else:
    print (colored("Not Found!!!! "+ serialNumber,'white','on_red'))
    winsound.Beep(800, 1500)
    winsound.Beep(500, 1000)
    conn.commit()
    cur.close()

  
