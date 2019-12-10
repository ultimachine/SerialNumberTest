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
import datetime

# terminal init for windows
init()
goodfrequency = 2500
goodduration = 1000


print ("Log process step for board")
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


state = "logging"
runId = '-1'
user = '-1'
process = 'Wave Solder' 
process_step = 'Seho'

# get user name from terminal
while user == '-1':
  print ("\nEnter User ID : ")
  user = input()
  if user == 'exit':
    sys.exit(0)
  

# get runId number from terminal
while runId == '-1':
  print ("\nEnter Run ID : ")
  runId = input()
  if runId == 'exit':
    sys.exit(0)

while (state == 'logging'):
  #setup database
  conn = psycopg2.connect(postgresInfo)
  cur = conn.cursor()
    
  # get serial number from terminal
  print ("\nCurrent Run ID " + runId)
  print ("Current Operator : " + user)
  print ("Current Process " + process)
  print ("Current Process Step " + process_step)
  print ("Type exit to exit")
  print ("\nEnter serial number : ")
  serialNumber = input()
  if serialNumber == 'exit':
    sys.exit(0)
  try:
    # write board serial number to process log
    insertquery = """INSERT INTO process_log (serial, operator, runid, process, process_step) VALUES (%s,%s,%s,%s,%s)"""
#    print (insertquery)
#    print (serialNumber + " " + user + " " + runId + " " + process + " " + process_step)
    cur.execute(insertquery,(serialNumber,user,runId,process,process_step))
   conn.commit()

    print (colored("Logged "+ serialNumber,'white','on_green'))
    winsound.Beep(3000, 800)


    mytoday = str(datetime.date.today())
    mytomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
    
    cur.execute("""SELECT date_part('day', time) AS day, process_step, COUNT (DISTINCT serial) AS boards 
    FROM process_log WHERE time >= %s AND time < %s 
    GROUP BY day, process_step ORDER BY boards DESC""", (mytoday, mytomorrow ))
    rows = cur.fetchall()
    for row in rows:
        print(str(row))
    conn.commit()
    cur.close()
    
    

    
  except (Exception, psycopg2.DatabaseError) as error :
    print ("Error in transction Reverting all other operations of a transction ", error)
    conn.rollback()
  finally:
    #closing database connection.
    if(conn):
      cur.close()
      conn.close()


