#! /usr/bin/python
#
# Program: generate_cimmyt_phenotype_report.py
# Version: 0.1 October 26,2017 Initial Version
#
# Prototype program to generate CIMMYT Phenotype (Breeder's) Report
#
#

import csv
import sys
import mysql.connector
from mysql.connector import errorcode
import config
import datetime

year='16'
location='JBL'
trait='NDVI'
traitToLabel={}
labelToTrait={}
dateRow=[]
headerRow=[]
emptyTraitRow=[]
plots={}
phenotypeData={}

labelToTrait['Germi'] = 'GERMPCT'
labelToTrait['GroundCovr'] = 'GrndCov'
labelToTrait['Booting'] = 'DTB'
labelToTrait['Heading'] = 'DTHD'
labelToTrait['Height'] = 'PH'
labelToTrait['Maturity'] = 'DAYSMT'
labelToTrait['Lodg%'] = 'LOI'
labelToTrait['Yield(t/ha)'] = 'GRYLD'
labelToTrait['FL_Len'] = 'FLGLF'
labelToTrait['FL_Wdh'] = 'FLGLFW'
labelToTrait['Spike_Len'] = 'SpkLng'
labelToTrait['TGW'] = 'TGW'
labelToTrait['Remark'] = 'NOTES'
labelToTrait['Agron_Scor'] = 'AgrScr'
labelToTrait['NDVI'] = 'NDVI'
labelToTrait['CT'] = 'CT'

traitToLabel['GERMPCT'] = ['Germi']
traitToLabel['GrndCov']=['GroundCovr']
traitToLabel['DTB']=['Booting']
traitToLabel['DTHD']=['Heading']
traitToLabel['PH']=['Height']
traitToLabel['DAYSMT']=['Maturity']
traitToLabel['LOI']=['Lodg%']
traitToLabel['GRYLD']=['Yield(t/ha)']
traitToLabel['FLGLF']=['FL_Len']
traitToLabel['FLGLFW']=['FL_Wdh']
traitToLabel['SpkLng']=['Spike_Len']
traitToLabel['TGW']=['TGW']
traitToLabel['NOTES']=['Remark']
traitToLabel['AgrScr']=['Agron_Scor']
traitToLabel['NDVI'] = ['NDVI']
traitToLabel['CT'] = ['CT']

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



# Get the distinct plot_ids required for the report and store them as keys in the dictionary plots

cursor,cnx=open_db_connection(config)
query1=("SELECT DISTINCT plot_id FROM phenotypes WHERE iyear = %s and ilocation = %s ORDER by plot_no" )
cursor.execute(query1,(year,location))
if cursor.rowcount != 0:
    for row in cursor:
        plotId=str(row[0])
        plots[plotId]={}
close_db_connection(cursor,cnx)

# Get the distinct trait_ids and dates required to formulate the date header row and trait header row in the report

cursor,cnx=open_db_connection(config)
query0=("SELECT DISTINCT trait_id,phenotype_date FROM phenotypes WHERE iyear = %s and ilocation = %s ORDER by phenotype_date")
cursor.execute(query0,(year,location))
if cursor.rowcount != 0:
    for row in cursor:
        traitId=str(row[0])
        headerRow+=[str(row[0])]
        if row[1]==None:
            dateRow+=['']
        else:
            dateRow+=[str(row[1])]
        for plot in plots:
            plots[plot][traitId]=[]
close_db_connection(cursor, cnx)

#cursor,cnx=open_db_connection(config)
#query1=("SELECT DISTINCT phenotype_date FROM phenotypes WHERE iyear = %s and ilocation = %s and trait_id = %s" )
#cursor.execute(query1,(year,location,trait))
#if cursor.rowcount != 0:
#    for row in cursor:
#        print str(row[0].year),str(row[0].month).zfill(2),str(row[0].day).zfill(2)

#


cursor,cnx=open_db_connection(config)# Get the rows from the database containing the phenotype data for the year and location of interest.
query2 = ("SELECT plot_id,trait_id,phenotype_value,phenotype_date FROM phenotypes WHERE iyear = %s and ilocation = %s")
cursor.execute(query2,(year,location))
plotId=''
if cursor.rowcount != 0:
    for row in cursor:
        plotId=str(row[0])
        traitId=str(row[1])
        phenotypeValue=str(row[2])
        phenotypeDate=str(row[3])
        plots[str(row[0])][str(row[1])]+=phenotypeValue,phenotypeDate
close_db_connection(cursor,cnx)

for k,v in sorted(plots.items()):
    print(k,v)

sys.exit()
