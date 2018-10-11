#! /usr/bin/python
#
#
#
# Program: load_physiological_phenotypes_to_database.py
# Version: 0.1 October 11,2018 Initial Version

# Program to read in a file containing physiological phenotype data values and load into database.
#
#
import pandas as pd

import mysql.connector
from mysql.connector import errorcode
import config

import sys
import os
import argparse

def open_db_connection(config):

    # Connect to the HTP database
        try:
            cnx = mysql.connector.connect(user=config.USER, password=config.PASSWORD,
                                          host=config.HOST, port=config.PORT,
                                          database=config.DATABASE)
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
traits['TGW']='TGW'
traits['LODG_0_10']='LODG_0_10'


# Get command line input.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-p','--pfile',help='The full path to the spreadsheet containing the phenotype data.')
cmdline.add_argument('-s','--sheet',help='The worksheet in the spreadsheet to be processing')

# Assign variables to command line arguments

args=cmdline.parse_args()

inFile=args.pfile
worksheet=args.sheet

print()
print('Processing input file: '+ inFile + ' Worksheet: ' + worksheet)

# Connect to database - Create one cursor per query

print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(config)
insert_phenotypes = "INSERT INTO phenotypes (plot_id,iyear,ilocation,itrial,icondition,plot_no,trait_id," \
                    "phenotype_value,phenotype_date)" \
                   " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"


# Read in the field map input file and determine the dimensions of the field map

phenotypeData = pd.read_excel(inFile,sheet_name=worksheet)
cnt=0
for r in phenotypeData.T:
    plotId=phenotypeData.T[r].plot_id
    plotAttr=plotId.split('-')
    pYear=plotAttr[0]
    pLocation=plotAttr[1]
    pTrial=plotAttr[2]
    pCondition=plotAttr[3]
    plotNo=plotAttr[4]

    if pd.isnull(phenotypeData.T[r].phenotype_value):
        phenotypeValue='NA'
    else:
        phenotypeValue = phenotypeData.T[r].phenotype_value
    traitId=phenotypeData.T[r].trait_id
    pDate=str(phenotypeData.T[r].phenotype_date)
    tyear=pDate[0:4]
    tmonth=pDate[4:6]
    tday=pDate[6:8]
    phenotypeDate=tyear+'-'+tmonth+'-'+tday
    phenotypeRow = (plotId, pYear, pLocation, pTrial, pCondition, plotNo, traitId, phenotypeValue,phenotypeDate)
    print(phenotypeRow)
    cursorA.execute(insert_phenotypes, phenotypeRow)
    #print(plotId,pYear,pLocation,pTrial,pCondition,plotNo,phenotypeValue,traitId,pDate,tyear,tmonth,tday,phenotypeDate)
    #a=input('Hit Any Key to Continue')
    cnxA.commit()
    cnt+=1
cursorA.close()
print('Number of rows processed: ',cnt)
sys.exit()

