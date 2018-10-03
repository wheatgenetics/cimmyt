#! /usr/bin/python
#
#
#
# Program: load_custom_fieldbook_phenotypes_to_database.py
# Version: 0.1 October 3,2018 Initial Version

# Program to read in custom Fieldbook file containing phenotype data values in columns and load into database.
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
insert_phenotypes = "INSERT INTO phenotypes (plot_id,iyear,ilocation,itrial,icondition,plot_no,trait_id,phenotype_value)" \
                   " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"


# Read in the field map input file and determine the dimensions of the field map

phenotypeData = pd.read_excel(inFile,sheet_name=worksheet)

for r in phenotypeData.T:
    plotId=phenotypeData.T[r].plot_id
    plotAttr=plotId.split('-')
    pYear=plotAttr[0]
    pLocation=plotAttr[1]
    pTrial=plotAttr[2]
    pCondition=plotAttr[3]
    plotNo=plotAttr[4]
    colId = 0
    for c in phenotypeData.columns:
        if c in traits:
            traitId=traits[c]
            if pd.notnull(phenotypeData.T[r][colId]):
                phenotypeValue = phenotypeData.T[r][colId]
                phenotypeRow=(plotId, pYear, pLocation, pTrial, pCondition, plotNo, traitId, phenotypeValue)
                print(phenotypeRow)
                cursorA.execute(insert_phenotypes,phenotypeRow)
            elif pd.isnull(phenotypeData.T[r][colId]):
                phenotypeValue='NA'
                phenotypeRow = (plotId, pYear, pLocation, pTrial, pCondition, plotNo, traitId, phenotypeValue)
                print(phenotypeRow)
                cursorA.execute(insert_phenotypes, phenotypeRow)
        colId+= 1
    cnxA.commit()
cursorA.close()
sys.exit()

