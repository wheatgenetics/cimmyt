#! /usr/bin/python
#
# Program: write_plot_shapefile.py
#
# Version: 0.1 August 8,2018 Initial Version
#
# INPUT: TBD
#
# OUTPUT: Absolute path for shapefile to be created
#

import fiona

from shapely.geometry import shape
from shapely import wkt
from shapely.wkt import dumps,loads
from shapely.geometry import Polygon,mapping

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
                print('Something is wrong with your user name or password')
                sys.exit()
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Database does not exist')
                sys.exit()
            else:
                print(err)
        else:
            print('Connected to MySQL database:' + cnx.database)
            cursor = cnx.cursor(buffered=True)
        return cursor,cnx

#------------------------------------------------------------------------
def commit_and_close_db_connection(cursor,cnx):

    # Commit changes and close cursor and connection

    try:
        cnx.commit()
        cursor.close()
        cnx.close()

    except Exception as e:
            print('There was a problem committing database changes or closing a database connection.')
            print('Error Code: ' + e)
    return
#------------------------------------------------------------------------

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-p','--plotID',help='Plot_id or partial plot_id of the plot polygon(s) to be extracted...')
cmdline.add_argument('-o','--output',help='Shapefile to be created...')
args=cmdline.parse_args()
plots=args.plotID + '%'
outFile=args.output

#Define a polygon feature geometry with one attribute
schema = {
    'geometry': 'Polygon',
    'properties': {'Plot_ID': 'str:254'},
}

# Query to populate the plot_map table in the CIMMYT database

plotMapSelect = "SELECT plot_id,ST_AsText(plot_polygon) FROM plot_map WHERE plot_id LIKE %s ORDER BY plot_id"

# Open database connection

cursorA, cnxA = open_db_connection(test_config)
cursorA.execute(plotMapSelect,(plots,))

plotCount=0
plotList=[]
for row in cursorA:
    plotCount+=1
    plotId=row[0]
    plotPolygon=row[1]
    shapelyPolygon = loads(plotPolygon)
    plotList.append([plotId,shapelyPolygon])
commit_and_close_db_connection(cursorA, cnxA)

print ("Number of plots read from database:" + str(plotCount))

# Write a new Shapefile
with fiona.collection(outFile, 'w', 'ESRI Shapefile', schema) as output:
    for plot in plotList:
        plotId=plot[0]
        plotPoly=plot[1]
        output.write({
            'geometry': mapping(plotPoly),
            'properties': {'Plot_ID': plotId},
        })

sys.exit()


