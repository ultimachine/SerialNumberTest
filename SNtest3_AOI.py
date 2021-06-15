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
import pytds #python-tds
import inspect

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
 

# AOI - Get list of weekly databases
aoi_servers = {}
smt_aoi_server = ('168.254.0.60')
tht_aoi_server = ('168.254.0.53')
aoi_user = 'ro'
aoi_password = 'password'

def checkAOI(serialNumber, aoi_server, server_name):
  returnValue = None

  print ("Connecting to AOI database...")
  try: 
    cnx = pytds.connect(server=aoi_server, user=aoi_user, password=aoi_password, autocommit=True, timeout=4, login_timeout=4)
    #print ("Connect to AOI success.")
  except Exception as e:
    print(e)
    print ("Failed AOI connection.")
    sys.exit(0)
  aoi_cursor = cnx.cursor()
  aoi_cursor.execute('SELECT TOP 20 [ResultDBName] FROM [KY_AOI].[dbo].[TB_ResultDB] order by [ResultDBName] DESC')
  databases = aoi_cursor.fetchall()

  if(len(serialNumber) == 0):
    print(colored("Zero Length Serial Number",'white','on_red'))
    winsound.Beep(500, 200)
    winsound.Beep(500, 200)
    print("Return Value: ", returnValue)
    return False
  for weekly_db in databases:
    #print(weekly_db[0])
    aoi_cursor.execute("SELECT [PanelResultAfter] FROM [" + weekly_db[0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '" + serialNumber + "' " )
    boards = aoi_cursor.fetchall()
    if( len(boards) == 0 ):
      continue

    results = [board[0] for board in boards]
    #print(results)
    for result in results:
      #result = board[0]
      print("Found result: " + str(result) + "  ",end='')
      if( result == 12000000 or result == 11000000 ):
        print(colored("Passed " + server_name + " AOI",'white','on_green'))
        #winsound.Beep(3000, 200)
        if( returnValue is None ):
          returnValue = True
      elif( result == 13000000 ):
        #returnValue = False
        print(colored("Failed " + server_name + " AOI",'white','on_red'))
        winsound.Beep(500, 200)
        winsound.Beep(500, 200)
      else:
        #returnValue = False
        print(colored("Unknown " + server_name + " AOI",'white','on_red'))
        winsound.Beep(500, 200)
        winsound.Beep(500, 200)

    if( returnValue is None):
      returnValue = False
    break

  if( returnValue is None ):
    returnValue = False
    print(colored("Not Found in " + server_name + " AOI!",'yellow'))
    winsound.Beep(500, 200)
    winsound.Beep(500, 200)

  print("Return Value: ", returnValue)
  return returnValue

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
  boxedcount = str( int(count) - int(shipped) )
  print("BoxedCount " + boxedcount )
  say.say(boxedcount)
  
  f = open("boxedcount.txt", "r+")
  f.seek(0)
  f.write(boxedcount)
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
  results = []
  results += [checkAOI(serialNumber,smt_aoi_server,"SMT")]
  results += [checkAOI(serialNumber,tht_aoi_server,"THT")]
  if results[0] is not True: continue
  if results[1] is not True: continue

  elif runcount > 0:
    # check for found in already found boards
    cur.execute("""SELECT time FROM tempserialtest WHERE serialnumber = %s""",(serialNumber,))
    rows = cur.fetchall()
    foundcount = len(rows)
	
	
    if foundcount > 0:
      # board already in added to this shipment
      print (colored("Error! " + serialNumber + " Already Found and in shipment table!!!!",'yellow',attrs=['reverse']))
      winsound.Beep(500, 1500)
      winsound.Beep(800, 1000)
      for row in rows:
        print(str(row[0]))
      conn.commit()
      cur.close()
	
    else:
    # write found board serial number to temp table
      insertquery = """INSERT INTO tempserialtest (serialnumber, tstuser,runid, pcbfab, boxedcount, prev_shipped) VALUES (%s, %s, %s, %s, %s, %s)"""
      cur.execute(insertquery, (serialNumber, tstuser, runId, pcbFab, boxedcount, shipped) )
      conn.commit()
      cur.close()

      print (colored("Test Found "+ serialNumber,'white','on_green'))
      newcount = countint + 1
      if str(newcount)[-1:] == "0":
        winsound.Beep(3000, 800)
      else:
        winsound.Beep(2100, 800)

      
  # No test results found
  else:
    print (colored("Not Tested!!!",'white','on_red') + "  Send SN: " + serialNumber + colored("  to the Test Fixture... ","cyan"))
    winsound.Beep(800, 1500)
    winsound.Beep(500, 1000)
    conn.commit()
    cur.close()

  
