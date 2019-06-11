#!/usr/bin/env python

# test if barcode in correct production run and passed
# keep up with how many boards found total
# tempSerialTest serialnumber, date time, user


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
say.setProperty('rate', 250)


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
runId = '221'
tstuser= '1'

while (state == 'testing'):
  #setup database
  conn = psycopg2.connect(postgresInfo)
  cur = conn.cursor()
  
  #output run quantity
  cur.execute("""SELECT COUNT(*) FROM tempserialtest""")
  cnt = cur.fetchone()
  countint = cnt[0]
  count = str(countint)
  print("Count " + count)  
#  print("Count " + count)  
  tens = count[-2:]
  if tens[-1:] == "0":
    if tens == "00":
      say.say(count)
    else:
      say.say(tens)
  say.runAndWait()
  conn.commit()
  
  
  # get serial number from terminal
  print ("\nEnter serial number : ")
  serialNumber = input()
  if serialNumber == 'exit':
    sys.exit(0)
	
  
  cur.execute("""SELECT serial FROM testdata WHERE productionrunid = %s AND testresults LIKE 'Passed' AND serial = %s""",(runId,serialNumber))
  rows = cur.fetchall()
  runcount = len(rows)
#  runcount = int(cur.fetchone()[0])
  	

 
  #print(runcount)
  
  # print results
  if runcount > 0:
    # check for found in already found boards
    cur.execute("""SELECT time FROM tempserialtest WHERE serialnumber = %s""",(serialNumber,))
    rows = cur.fetchall()
    foundcount = len(rows)
	
	
    if foundcount > 0:
      # board already in found table
      print (colored("Error! " + serialNumber + " Already Found and in table!!!!",'white','on_yellow'))
      winsound.Beep(500, 1500)
      winsound.Beep(800, 1000)
      for row in rows:
        print(str(row[0]))
#      cur.execute("""SELECT COUNT(*) FROM tempserialtest""")
#      count = cur.fetchone()
#      print("Count " + str(count[0]))  
      conn.commit()
      cur.close()
	
    else:
    # write found result to temp table
      insertquery = """INSERT INTO tempserialtest (serialnumber, tstuser) VALUES (%s, %s)"""
      cur.execute(insertquery,(serialNumber,tstuser))
      conn.commit()
      cur.close()

      print (colored("Found "+ serialNumber,'white','on_green'))
      newcount = countint + 1
      if str(newcount)[-1:] == "0":
        winsound.Beep(3000, 800)
      else:
        winsound.Beep(2100, 800)
#      cur.execute("""SELECT COUNT(*) FROM tempserialtest""")
#      cnt = cur.fetchone()
#      count = str(cnt[0])
#      print("Count " + count)  
#      tens = count[-2:]
#      if tens[-1:] == "0":
#        if tens == "00":
#          say.say(count)
#        else:
#          say.say(tens)
#        say.runAndWait()
#      conn.commit()
#      cur.close()
      
  # No test results found
  else:
    print (colored("Not Found!!!! "+ serialNumber,'white','on_red'))
    winsound.Beep(800, 1500)
    winsound.Beep(500, 1000)
#    cur.execute("""SELECT COUNT(*) FROM tempserialtest""")
#    count = cur.fetchone()
#    for row in rows:
#      print("Count " + str(count[0]))  
      
    conn.commit()
    cur.close()

  

#	cursor.execute("""SELECT date FROM finishedgoodstracking WHERE date = %s""",(dateTest,))
#	rows = cursor.fetchall()
#	if len(rows) > 0:
#		cursor.execute("""UPDATE finishedgoodstracking SET minirambos=%s, rambos=%s, total=%s WHERE date=%s""",(miniNum,ramboNum,total,dateTest))
#	else:
#		cursor.execute("""INSERT INTO finishedgoodstracking(date,minirambos,rambos,total) VALUES(%s::date,%s,%s,%s)""",(dateTest,miniNum,ramboNum,total))
#	testStorage.commit()



 # SELECT COUNT(DISTINCT serial) FROM testdata WHERE productionrunid = 221 and testresults LIKE 'Passed'