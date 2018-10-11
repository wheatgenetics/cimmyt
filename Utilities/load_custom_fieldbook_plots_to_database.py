#! /usr/bin/python
#
#
#
# Program: load_custom_fieldbook_plotss_to_database.py
# Version: 0.1 October 4,2018 Initial Version

# Program to read in custom Fieldbook file containing partial plot data into database.
#
#
import pandas as pd

import mysql.connector
from mysql.connector import errorcode
import test_config

import sys
import os
import argparse

def open_db_connection(test_config):

    # Connect to the HTP database
        try:
            cnx = mysql.connector.connect(user=test_config.USER, password=test_config.PASSWORD,
                                          host=test_config.HOST, port=test_config.PORT,
                                          database=test_config.DATABASE)
            print('Connecting to Database: ' + cnx.database)

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
                sys.exit()
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                sys.exit()
            else:
                print(err)
        else:
            print('Connected to MySQL database:' + cnx.database)
            cursor = cnx.cursor(buffered=True)
        return cursor,cnx


def close_db_connection(cursor,cnx):

    # Commit changes and close cursor and connection

    try:
        cursor.close()
        cnx.close()

    except Exception as e:
            print('There was a problem closing the database connection.')
            print('Error Code: ' + e)

    return

traits={}
traits['GERMPCT'] = 'GERMPCT'
traits['DTHD'] = 'DTHD'
traits['DAYSMT'] = 'DAYSMT'
traits['GRYLD'] = 'GRYLD'
traits['Agrscr'] = 'AgrScr'
traits['PH'] = 'PH'
traits['NOTES']='NOTES'

# Get command line input.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-p','--pfile',help='The full path to the spreadsheet containing the phenotype data.')
cmdline.add_argument('-s','--sheet',help='The worksheet in the spreadsheet to be processing')

# Assign variables to command line arguments

args=cmdline.parse_args()

inFile=args.pfile
worksheet=args.sheet

print()
print('Processing field map input file: '+ inFile + ' Worksheet: ' + worksheet)

# Connect to database - Create one cursor per query

print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(test_config)
cursorB,cnxB=open_db_connection(test_config)
insert_plot = "INSERT IGNORE INTO plots (plot_id,iyear,ilocation,itrial,icondition,plot_no,trial," \
              "seed_source,planting_date,site,year,location,cycle,conditions,rep,block,subblock," \
              "col,row,entry,purpose,gid,tid,occ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#insert_plot = "INSERT IGNORE INTO plots (plot_id,iyear,ilocation,itrial,icondition,plot_no,trial,rep,block,subblock,gid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
check_plot = "SELECT * FROM plots WHERE iyear=%s AND ilocation=%s and itrial=%s and icondition=%s"
# Read in the field map input file and determine the dimensions of the field map

pseedSource=None
pplantingDate=None
psite=None
pyear=2018
plocation='Obregon'
pcycle='Y17-18'
pconditions=None
pblock=None
pcol=None
prow=None
ppurpose=None
ptid=None
pocc=None


phenotypeData = pd.read_excel(inFile,sheet_name=worksheet)

for index,row in phenotypeData.iterrows():
    plotId=row['plot_id']
    plotAttr = plotId.split('-')
    piYear = plotAttr[0]
    piLocation = plotAttr[1]
    piTrial = plotAttr[2]
    piCondition = plotAttr[3]
    plotNo = plotAttr[4]
    pRep = row['Rep']
    pSubblock = row['SubBlock']
    pEntry = row['Entry']
    pGID = row['GID']
    pTrial = row['Trial']
    plotRow = (plotId, piYear, piLocation, piTrial, piCondition, plotNo, pTrial,pseedSource,pplantingDate,psite,pyear,
               plocation,pcycle,pconditions,pRep,pblock, pSubblock,pcol,prow, pEntry, ppurpose,pGID,ptid,pocc )
    print(plotRow)
    cursorA.execute(insert_plot,plotRow)
    cnxA.commit()
cursorB.execute(check_plot,(piYear,piLocation,piTrial,piCondition))
rowCount=cursorB.rowcount
print('Number of rows for '+ piYear+'-'+piLocation+'-'+piTrial+'-'+piCondition+'='+str(rowCount))
cursorA.close()
cursorB.close()


sys.exit()

