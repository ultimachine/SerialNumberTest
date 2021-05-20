import pytds #python-tds
from termcolor2 import colored
#from termcolor import colored, cprint
import winsound

import colorama
colorama.init()

server_smt = '168.254.0.60'
server_tht = '168.254.0.53'

server = server_tht
user = 'ro'
password = 'password'


#conn = pymssql.connect(server='168.254.0.59', user='sa', password='kohyoung', database='KY_AOI') 

#cnx = pytds.connect(server=server, user=user, password=password, autocommit=True)

# AOI - Get list of weekly databases
server_smt = '168.254.0.60'
server_tht = '168.254.0.53'
aoi_server = server_tht
aoi_user = 'ro'
aoi_password = 'password'
print ("Connecting to AOI database...")
try: 
  cnx = pytds.connect(server=aoi_server, user=aoi_user, password=aoi_password, autocommit=True)
  print ("Connect to AOI success.")
except:
  print ("Failed AOI connection.")
  sys.exit(0)


cur = cnx.cursor()
cur.execute('SELECT TOP 20 [ResultDBName] FROM [KY_AOI].[dbo].[TB_ResultDB] order by [ResultDBName] DESC')
# Prove we got rows back

databases = cur.fetchall()
print("Count of DBs: " + str(len(databases)) )

#print(databases[0])

#print(databases[0][0])

#cur.execute("SELECT [PanelResultAfter] FROM [" + databases[0][0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '045614340' " )
#boards = cur.fetchall()

#for board in boards:
#    print( board )


def checkAOI(serialNumber):
  returnValue = None
  for weekly_db in databases:
    print(weekly_db[0])
    cur.execute("SELECT [PanelResultAfter] FROM [" + weekly_db[0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '" + serialNumber + "' " )
    boards = cur.fetchall()
    if( len(boards) == 0 ):
      continue

    results = [board[0] for board in boards]
    print(results)
    for result in results:
      #result = board[0]
      print("Found result: " + str(result) + "  ",end='')
      if( result == 12000000 or result == 11000000 ):
        print(colored("Passed AOI",'white','on_green'))
        winsound.Beep(3000, 200)
        if( returnValue is None ):
          returnValue = True
      elif( result == 13000000 ):
        #returnValue = False
        print(colored("Failed AOI",'white','on_red'))
        winsound.Beep(500, 200)
      else:
        #returnValue = False
        print(colored("Unknown AOI",'white','on_red'))
        winsound.Beep(500, 200)

    if( returnValue is None):
      returnValue = False
    break

  if( returnValue is None ):
    returnValue = False
    print(colored("Not Found!",'yellow'))
    winsound.Beep(500, 800)
    winsound.Beep(500, 800)

  print("Return Value: ", returnValue)
  return returnValue



while(True):
  print ("\nEnter serial number : ")
  serialNumber = input()
  if serialNumber == 'exit':
    sys.exit(0)

  checkAOI(serialNumber)
'''
  for weekly_db in databases:
    print(weekly_db[0])
    cur.execute("SELECT [PanelResultAfter] FROM [" + weekly_db[0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '" + serialNumber + "' " )
    boards = cur.fetchall()
    if( len(boards) ):
      print(boards)
      print("Found result: " + str(boards[0][0]))
      if( boards[0][0] == 12000000 or boards[0][0] == 11000000 ):
        print(colored("Passed AOI",'white','on_green'))
        winsound.Beep(3000, 800)
      elif( boards[0][0] == 13000000 ):
         print(colored("Failed AOI",'white','on_red'))
         winsound.Beep(500, 800)
      else:
         print(colored("Unknown AOI",'white','on_red'))
         winsound.Beep(500, 800)
      break
    else:
      if( weekly_db == databases[len(databases)-1] ):
         print(colored("Not Found!",'yellow'))
         winsound.Beep(500, 800)
         winsound.Beep(500, 800)
'''
