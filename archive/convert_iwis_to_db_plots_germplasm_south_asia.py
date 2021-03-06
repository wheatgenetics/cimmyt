#! /usr/bin/python
#
# Program: convert_iwis_to_db_plots_germplasm.py
# Version: 0.1 September 18,2017 Initial Version
# Version: 0.2 October 25,2017 Eliminated duplicate gid in germplasm data records in IWIS files by using Dictionary
#
# This program will take a CIMMYT IWIS Excel .xls export file that contains plot and germplasm data in each row and populates
# the plot and germplasm tables in the CIMMYT database.
#
# Note that multiple rows can occur for each GID in the IWIS file due to the fact that there are replicated plots
# which will have the same GID. The duplicate GID is eliminated by using GID in the dictionary germplasmDict. The same
# approach is used for plot_id in the dictionary plotDict.
#
# The Excel file structure is as follows:
#
# Row 1 Col 1: 'TID'        Row 1 Col 2: <tid value>
# Row 2 Col 1: 'OCC'        Row 2 Col 2: <occ value>
# Row 3 Col 1: 'Trial Name' Row 3 Col 2: <trial name value>
# Row 4 Col 1: 'Trial Abbr' Row 4 Col 2: <trial abbreviation value>
# Row 5 Col 1: 'Cycle'      Row 5 Col 2: <cycle value>
# Row 6 Col 1: 'Program'    Row 6 Col 2; <program value>
# Row 7 Blank
# Row 8 Column Headings for plot and germplasm data columns
#   Column 1: CID
#   Column 2: SID
#   Column 3: GID
#   Column 4: Cross Name
#   Column 5: Selection History
#   Column 6: Origin (Seed Source)
#   Column 7: Plot
#   Column 8: Rep
#   Column 9: SubBlock
#   Column 10: Entry
# Row 9 to EOF: plot and germplasm data values
#
# Error Handling:
#
# If any error occurs while attempting to insert into plots table, an exception will be thrown and the program exited.
#
# If any error occurs while attempting to insert into germplams table, an exception will be thrown and the program
# exited. However, note that the insert statement used to insert into the germplasm table allows duplicate key errors
# to be ignored.
#
#


from pyexcel_xls import get_data
import sys
import mysql.connector
from mysql.connector import errorcode
import config
from collections import OrderedDict
import argparse

plotDict=OrderedDict()
germplasmDict = OrderedDict()

# condition is a dictionary that translates from IWIS condition to CIMMYT database icondition
iconditions={}
iconditions['B5IR']='B5I'
iconditions['B2IR']='B2I'
iconditions['BLHT']='LHT'
iconditions['F5IR']='F5I'
iconditions['BEHT']='EHT'
iconditions['DRIP']='DRM'
iconditions['Melga']='MEL'

# location is a dictionary that translates from CIMMYT database ilocation to IWIS location

locations={}
locations['OBR']='Obregon'
locations['FAS'] = 'Faisalabad'

# occs is a dicationary that translats from CIMMYT occ to icondition
occs={}
occs[5]='MEL'
occs[6]='LHT'

# Get command line input.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-i','--input',help='IWIS input file')
cmdline.add_argument('-l','--location',help='Location of the plots', default='OBR')
cmdline.add_argument('-s','--sheet',help='Worksheet in the spreadsheet',default='Sheet1')
cmdline.add_argument('-c','--icondition',help='Condition associated with a trial', default='B5I')

args=cmdline.parse_args()


inputFile=args.input
ilocation=args.location
location=locations[ilocation]
wksheet=args.sheet
condition=args.icondition
#conditions=condition[icondition]
seedSource = None
purpose = None
plantingDate = None
site = 'Faisalabad'
col = None
row = None

# Read in the data from the Excel IWIS file

data = get_data(inputFile)

print()
print('Processing IWIS file: ' + inputFile)

index = 0
for item in data[wksheet]:
    if index == 0:
        tid = data[wksheet][index][1]
        print('TID:',tid)
    elif index == 1:
        occ = data[wksheet][index][1]
        print('OCC',occ)
        icondition=occs[occ]
    elif index == 2:
        pass
    elif index == 3:
        trial=data[wksheet][index][1]
        if 'SABW' in trial:
            itrial = 'SAG'
        print('itrial:',itrial)
        print('trial:',trial)
        print('icondition:',icondition)
        print('conditions:',condition)
    elif index == 4:
        cycle = data[wksheet][index][1]
        iyear = cycle.split('-')[1]
        year = '20' + iyear
        print('iyear:',iyear)
        print('year',year)
        print('cycle',cycle)
    elif index == 7:
        header = data[wksheet][index]
    elif index > 7:
        cid = data[wksheet][index][0]
        sid = data[wksheet][index][1]
        gid = data[wksheet][index][2]
        crossName= data[wksheet][index][3]
        selectionHistory = data[wksheet][index][4]
        origin = data[wksheet][index][5]
        plot = str(data[wksheet][index][6])
        rep = str(data[wksheet][index][7])
        block=None # For Future use. Block not currently supported in IWIS files.
        subblock = str(data[wksheet][index][8])
        entry = str(data[wksheet][index][9])

        plotId=iyear + '-' + ilocation + '-' + itrial + '-' + icondition + '-' + plot
        plotDict[plotId]=[plotId,iyear,ilocation,itrial,icondition,plot,trial,seedSource,plantingDate,site,year,location,cycle,condition,rep,block,subblock,col,row,entry,purpose,gid,tid,occ]
        germplasmDict[gid]=[gid,cid,sid,selectionHistory,crossName]

    index+=1

# Connect to database and return two cursors: One for insert into the plots table and
# one for insert into germplasm table
try:
    cnx = mysql.connector.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                      port=config.PORT,database=config.DATABASE)
    print()
    print("Connecting to database " + cnx.database + " ...")
    print()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursorA = cnx.cursor(buffered=True)
    cursorB = cnx.cursor(buffered=True)
    cursorC = cnx.cursor(buffered=True)
    cursorD = cnx.cursor(buffered=True)


# Insert data into plots table. Exit if any error occurs, only commit changes when all updates are made.

count_plots = "SELECT * from plots"
insert_plot = "INSERT IGNORE INTO plots (plot_id,iyear,ilocation,itrial,icondition,plot_no,trial,seed_source,planting_date,site,year,location,cycle,conditions,rep,block,subblock,col,row,entry,purpose,gid,tid,occ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

try:
    print("Inserting data into plots table...")
    cursorC.execute(count_plots,)
    startPlotCount=cursorC.rowcount
    plotInserts=0
    for plotId,p in plotDict.items():
        plotRow=(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14],p[15],p[16],p[17],p[18],p[19],p[20],p[21],p[22],p[23])
        cursorA.execute(insert_plot,plotRow)
        plotInserts+=1
    cnx.commit()
    cursorA.close()
    cursorC.execute(count_plots,)
    endPlotCount = cursorC.rowcount
    print("Plot Records Processed :" + str(plotInserts))
    print("Plot Records Inserted: " + str(endPlotCount-startPlotCount))
    print()
    cursorC.close()
except mysql.connector.Error as err:
    print()
    print('An error occurred while attempting to insert data into CIMMYT database plots table. Exiting...')
    print(err)
    print('**************************************************************************************************')
    print()
    sys.exit()

# Insert data into germplasm table. Exit if any error occurs, only commit changes when all updates are made.
# Note that INSERT IGNORE allows duplicate key errors to be ignored and processing to continue

count_germplasm = "SELECT * FROM germplasm"
insert_germplasm = "INSERT IGNORE INTO germplasm (gid,cid,sid,selection_history,cross_name) VALUES (%s,%s,%s,%s,%s)"

try:
    print("Inserting data into germplasm table...")
    cursorD.execute(count_germplasm, )
    startGermplasmCount=cursorD.rowcount
    germplasmInserts=0
    for plotId,g in germplasmDict.items():
        germplasmRow=(g[0],g[1],g[2],g[3],g[4])
        cursorB.execute(insert_germplasm,germplasmRow)
        germplasmInserts+=1
    cnx.commit()
    cursorB.close()
    cursorD.execute(count_germplasm, )
    endGermplasmCount = cursorD.rowcount
    print("Germplasm Records Processed :" + str(germplasmInserts))
    print("Unique Germplasm Records Inserted: " + str(endGermplasmCount - startGermplasmCount))
    cursorD.close()
except mysql.connector.Error as err:
    print()
    print('An error occurred while attempting to insert data into CIMMYT database germplasm table. Exiting...')
    print(err)
    print('**************************************************************************************************')
    print()
    sys.exit()

print()
print("Program executed successfully. Exiting...")
print()

sys.exit()


