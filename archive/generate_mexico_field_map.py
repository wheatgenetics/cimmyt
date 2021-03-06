#! /usr/bin/python
#
# Program: generate_mexico_field_map.py
# Version: 0.1 October 24,2017 Initial Version
#
# This program will generate a CIMMYT Mexico field map.
#
#

import xlsxwriter

import mysql.connector
from mysql.connector import errorcode
import config

import sys
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

# Get command line input.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-y','--year',help='The iyear to generate fieldbook file for')
cmdline.add_argument('-l','--location',help='The ilocation to generate fieldbook file for', default='OBR')
cmdline.add_argument('-t','--trial',help='The itrial to generate fieldbook file for')
cmdline.add_argument('-c','--condition',help='The icondition to generate fieldbook file for')

args=cmdline.parse_args()

iyear=args.year
ilocation=args.location
itrial=args.trial
icondition=args.condition
plotId=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'%'

outFile=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'_Field_Map.xlsx'

# Open .xlsx output file and set up worksheet formatting

workbook = xlsxwriter.Workbook(outFile)
worksheet = workbook.add_worksheet()
format = workbook.add_format()
format.set_bg_color('#42f498')
format.set_border()
format2=workbook.add_format()
format2.set_bg_color("#D7E4BC")


merge_format = workbook.add_format({
    'bold':     True,
    'border':   6,
    'align':    'center',
    'valign':   'vcenter',
    'fg_color': '#D7E4BC',
})
# write the column label row to the worksheet

worksheet.write_string(0, 0, 'Trial',merge_format)

# Connect to database - One cursor per query

print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(config)
cursorB,cnxB=open_db_connection(config)
cursorC,cnxC=open_db_connection(config)
cursorD,cnxD=open_db_connection(config)

plotQuery = "SELECT plot_id,plot_no,trial,col,row,rep FROM plots WHERE plot_id LIKE %s AND trial = %s ORDER BY plot_no"
maxRowQuery = "SELECT MAX(row) FROM plots WHERE plot_id LIKE %s AND trial = %s"
maxColQuery = "SELECT MAX(col) FROM plots WHERE plot_id LIKE %s AND trial = %s"
trialQuery="SELECT DISTINCT trial FROM plots WHERE plot_id LIKE %s ORDER by tid"

# Query the list of distinct trials for the plotID

cursorD.execute(trialQuery,(plotId,))

# For each trial query the data required to build the field map and compute the range of rows and columns.

trialCount = 0
rowOffset=0
for rowD in cursorD:
    mapTrial=rowD[0]

    cursorA.execute(plotQuery, (plotId,mapTrial))
    cursorB.execute(maxRowQuery, (plotId,mapTrial))
    cursorC.execute(maxColQuery, (plotId,mapTrial))

    for rowB in cursorB:
        maxRow=rowB[0]
    for rowC in cursorC:
        maxCol=rowC[0]

    maxPlot=maxRow*maxCol
    print("Processing trial "+ mapTrial + ' (' + str(maxPlot) + " plots)")

# Write the plot data to the worksheet

    plotCount=1
    for rowA in cursorA:
        mapRow =((maxRow + 1) - rowA[4]) + rowOffset
        mapCol=rowA[3]
        mapPlot=rowA[1]
        mapRep=rowA[5]
        worksheet.write_number(mapRow,mapCol,mapPlot,format)
        plotCount+=1
        if mapCol==maxCol:
            repString='Rep '+ str(mapRep)
            worksheet.write_string(mapRow, mapCol+1, repString)
        if mapCol==1:
            worksheet.write_string(mapRow,0, " ",format2)

    worksheet.write_string(mapRow,0,mapTrial,format2)
    rowOffset+=maxRow + 1
    trialCount+=1

# write the title to the worksheet

titleStr="Field Map for "+ plotId[:-1]
worksheet.merge_range(0,1,0,maxCol,titleStr,merge_format)

# Close all database connections, close the spreadsheet file and exit

close_db_connection(cursorA,cnxA)
close_db_connection(cursorB,cnxB)
close_db_connection(cursorC,cnxC)
close_db_connection(cursorD,cnxD)
workbook.close()

sys.exit()


