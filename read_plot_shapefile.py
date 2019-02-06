#! /usr/bin/python
#
# Program: read_plot_shapefile.py
#
# Version: 0.1 August 7,2018 Initial Version
#
# This program will read a shapefile representing one or more plots and store them as plot polygons in the plot_map
# table.
#
# INPUT: Path to shapefile to be read into database
#
# OUTPUT: Database plot_map table populated with plots found in shape file.
#

import fiona

from shapely.geometry import shape
from shapely import wkt
from shapely.wkt import dumps
from shapely.geometry import Point,Polygon,MultiPoint

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
cmdline.add_argument('-i','--input',help='Path to Shapefile to import...')
args=cmdline.parse_args()
inputFile=args.input

# Query to populate the plot_map table in the CIMMYT database

plotMapInsert = "INSERT INTO plot_map_test (plot_id,plot_polygon) VALUES(%s,ST_PolygonFromText(%s))"

# Open database connection

cursorA, cnxA = open_db_connection(test_config)


# Read the shape file and update database with plot coordinates
plotInserts=0
with fiona.open(inputFile) as plot:
    print(plot.schema)
    for feat in plot:
        plotId=feat['properties']['Plot_ID']
        plotGeometry=feat['geometry']
        plotShape=shape(plotGeometry)
        print(plotId,plotGeometry)
        print(plotId,plotShape.convex_hull)
        print(plotId,dumps(plotShape.convex_hull))
        plotMapPolygon=dumps(plotShape.convex_hull)
        plotMapRow=(plotId,plotMapPolygon)
        try:
            cursorA.execute(plotMapInsert, plotMapRow)
            plotInserts+=1
            print()
        except Exception as e:
            print("Error occurred while attempting to insert plot into database:",e)



commit_and_close_db_connection(cursorA, cnxA)
sys.exit()


