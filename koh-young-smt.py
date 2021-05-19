import pytds #python-tds
from termcolor import colored, cprint
import winsound

server = '168.254.0.60'
user = 'ro'
password = 'password'


#conn = pymssql.connect(server='168.254.0.59', user='sa', password='kohyoung', database='KY_AOI') 

cnx = pytds.connect(server=server, user=user, password=password, autocommit=True)
cur = cnx.cursor()
cur.execute('SELECT [ResultDBName] FROM [KY_AOI].[dbo].[TB_ResultDB] order by [ResultDBName] DESC')
# Prove we got rows back

databases = cur.fetchall()

#print(databases[0])

#print(databases[0][0])

#cur.execute("SELECT [PanelResultAfter] FROM [" + databases[0][0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '045614340' " )
#boards = cur.fetchall()

#for board in boards:
#    print( board )

while(True):
  print ("\nEnter serial number : ")
  serialNumber = input()
  if serialNumber == 'exit':
    sys.exit(0)

  for weekly_db in databases:
    print(weekly_db[0])
    cur.execute("SELECT [PanelResultAfter] FROM [" + weekly_db[0] +  "].[dbo].[TB_AOIPanel] where [PanelBarCode] = '" + serialNumber + "' " )
    boards = cur.fetchall()
    if( len(boards) ):
      print("Found result: " + str(boards[0][0]))
      if( boards[0][0] == 12000000 or boards[0][0] == 11000000 ):
        print(colored("Passed AOI",'white','on_green'))
        winsound.Beep(3000, 800)
      else:
         print(colored("Failed AOI",'white','on_red'))
         winsound.Beep(500, 800)
      break
    else:
      if( weekly_db == databases[len(databases)-1] ):
         print(colored("Not Found!",'yellow'))
         winsound.Beep(500, 800)
         winsound.Beep(500, 800)

#for line in databases:
#    print(line[0])


