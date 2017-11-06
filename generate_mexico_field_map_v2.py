#! /usr/bin/python
#
# Program: generate_mexico_field_map.py
# Version: 0.1 October 24,2017 Initial Version
# Version: 0.2 Updated based on input from CIMMYT
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
cmdline.add_argument('-p','--planting', help='The planting date')
cmdline.add_argument('-s','--startplot', help='The starting plot number for each planting date')
cmdline.add_argument('-e','--endplot', help='The ending plot number for each planting date')
cmdline.add_argument('-r','--rows', help='The number of rows in each map file')

args=cmdline.parse_args()

iyear=args.year
ilocation=args.location
itrial=args.trial
icondition=args.condition
plotId=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'%'

plantingDate=args.planting
startPlotNo=args.startplot
endPlotNo=args.endplot
sectionRows=args.rows

plotList=[]

#merge_format = workbook.add_format({
#    'bold':     True,
#    'border':   6,
#    'align':    'center',
#    'valign':   'vcenter',
#    'fg_color': '#D7E4BC',
#})
# write the column label row to the worksheet

#worksheet.write_string(0, 0, 'Trial',merge_format)

# Connect to database - One cursor per query

print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(config)
cursorB,cnxB=open_db_connection(config)
cursorC,cnxC=open_db_connection(config)
cursorD,cnxD=open_db_connection(config)

plotQuery = "SELECT plot_id,plot_no,trial,col,row,rep FROM plots WHERE plot_id LIKE %s AND plot_no >= %s and plot_no <= %s ORDER BY plot_no"
maxRowQuery = "SELECT MAX(row) FROM plots WHERE plot_id LIKE %s AND trial = %s"
maxColQuery = "SELECT MAX(col) FROM plots WHERE plot_id LIKE %s AND trial = %s"
trialQuery="SELECT DISTINCT trial FROM plots WHERE plot_id LIKE %s AND plot_no >= %s AND plot_no <= %s ORDER by tid"

# Query the list of distinct trials for the plotID

cursorD.execute(trialQuery,(plotId,startPlotNo,endPlotNo))

# Query the plots to be included in the field map files.

cursorA.execute(plotQuery,(plotId,startPlotNo,endPlotNo))
for plot in cursorA:
    fullPlotId=plot[0]
    plotNo=plot[1]
    trial=plot[2]
    plotCol=plot[3]
    plotRow=plot[4]
    rep=plot[5]
    plotList.append([fullPlotId,plotNo,trial,plotCol,plotRow,rep])

# Calculate the number of files to be produced.
maxCol=15
maxPlotsPerSheet=(int(sectionRows)-2) * maxCol
numSheets=cursorA.rowcount//maxPlotsPerSheet

# For each trial, query the data required to build the field map and compute the range of rows and columns.

trialCount = 1
rowOffset=43
sheet=1
startIndex=0

for sheets in range(1,5):
    endIndex=startIndex+maxPlotsPerSheet-1
    print("Start " + str(startIndex) + " End ", str(endIndex))
    startPlot=plotList[startIndex]
    endPlot=plotList[endIndex]
    outFile = itrial + icondition + '_' + str(startPlot[1]) + '-' + str(endPlot[1]) + '.xlsx'
    print(outFile)
    # Open .xlsx output file and set up worksheet formatting
    workbook = xlsxwriter.Workbook(outFile)
    worksheet = workbook.add_worksheet()
    format = workbook.add_format()
    #format.set_bg_color('#42f498')
    worksheet.set_column(0,16,10.0)
    format.set_border()
    format2 = workbook.add_format()
    #format2.set_bg_color("#D7E4BC")
    columnCount=0
    for c in range(1,16):
        worksheet.write_string(rowOffset+1, c, "Borlaug 100", format)
    worksheet.write_number(rowOffset+1, 0, rowOffset+1, format2)
    worksheet.write_string(rowOffset+1, 16, "RELLENO", format)
    for plot in range(startIndex,endIndex+1):
        fullPlotId = plotList[plot][0]
        plotNo = plotList[plot][1]
        trial = plotList[plot][2]
        plotCol = plotList[plot][3]
        plotRow = plotList[plot][4]
        rep = plotList[plot][5]
        mapRow = rowOffset
        mapCol = plotCol
        mapPlot = plotNo
        mapRep = rep
        worksheet.write_number(mapRow, mapCol, mapPlot, format)
        if columnCount == 0:
            worksheet.write_number(mapRow, 0, mapRow, format2)
        columnCount+=1
        if columnCount==maxCol:
            rowOffset-=1
            columnCount=0
            worksheet.write_string(mapRow, 16, trial, format)
    for c in range(1,16):
        worksheet.write_string(1, c, "Borlaug 100", format)
        worksheet.write_number(0, c, c, format2)

    worksheet.write_number(1, 0, 1, format2)
    worksheet.write_string(1,16,"RELLENO",format)
    workbook.close()
    rowOffset=43
    startIndex = startIndex + maxPlotsPerSheet


# Close all database connections, close the spreadsheet file and exit

close_db_connection(cursorA,cnxA)
close_db_connection(cursorB,cnxB)
close_db_connection(cursorC,cnxC)
close_db_connection(cursorD,cnxD)
sys.exit()


sys.exit()


