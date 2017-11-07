#! /usr/bin/python
#
# Program: generate_mexico_field_map.py
#
# Version: 0.1 October 24,2017 Initial Version
# Version: 0.2 Updated based on input from CIMMYT
#
# This program will generate a CIMMYT Mexico field map.
#
# Note Row and Column Indices in xlsxWriter are zero based.
#
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
# Note that some of these may be input via other means in the future e.g. reading from a document of spreadsheet.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-y','--year',help='The iyear to generate fieldbook file for')
cmdline.add_argument('-l','--location',help='The ilocation to generate fieldbook file for', default='OBR')
cmdline.add_argument('-t','--trial',help='The itrial to generate fieldbook file for')
cmdline.add_argument('-c','--condition',help='The icondition to generate fieldbook file for')
cmdline.add_argument('-p','--planting', help='The planting date')
cmdline.add_argument('-s','--startplot', help='The starting plot number for each planting date')
cmdline.add_argument('-e','--endplot', help='The ending plot number for each planting date')
cmdline.add_argument('-r','--rows', help='The number of rows in each map file')
cmdline.add_argument('-x','--startpos',help='The starting side of the section North (N) or South(S)',default='N')

# Assign variables to command line arguments

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
startPosition=args.startpos

plotList=[]
firstPlotRow=2
lastPlotRow=43
columnMap={}
trialDims={}

#merge_format = workbook.add_format({
#    'bold':     True,
#    'border':   6,
#    'align':    'center',
#    'valign':   'vcenter',
#    'fg_color': '#D7E4BC',
#})
# write the column label row to the worksheet

#worksheet.write_string(0, 0, 'Trial',merge_format)

# Connect to database - Create one cursor per query

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

# For each trial query the database to find the row,column dimensions of the field map.

for rowD in cursorD:
    mapTrial=rowD[0]

    cursorB.execute(maxRowQuery, (plotId,mapTrial))
    cursorC.execute(maxColQuery, (plotId,mapTrial))

    for rowB in cursorB:
        maxRow=rowB[0]
    for rowC in cursorC:
        maxCol=rowC[0]

    maxPlot=maxRow*maxCol

    trialDims[mapTrial]=[maxRow,maxCol,maxPlot]

# Build the column map dictionary used to map a database column number to a spreadsheet column number depending on
# serpentine path direction. The dictionary has a primary index of trial and a secondary index of database column (col)

for trial in trialDims:
    maxCol=trialDims[trial][1]
    columnMap[trial]={}
    southIndex = maxCol
    for col in range(1,maxCol+1):
        columnMap[trial][col]=[col,southIndex]
        southIndex-=1

# Query the plots to be included in the field map files and build a list of plots

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
#  TODO-Question: Are there always 15 columns in a CIMMYT field map?
maxCol=15
maxPlotsPerSheet=(int(sectionRows)-2) * maxCol
numSheets=cursorA.rowcount//maxPlotsPerSheet

# Initialize the rowOffset depending on the startPosition of the serpentine path

if startPosition=='N':
    rowOffset=lastPlotRow # Start the first sheet from the last row in the map
elif startPosition=='S':
    rowOffset=firstPlotRow
else:
    print("Starting position is undefined...exiting")
    sys.exit(0)

#sheet=1 # Index of the first worksheet in the set to be generated
startIndex=0 # Index of first plot in the first field map
startCol=1
for sheet in range(1,numSheets+1):
    endIndex=startIndex+maxPlotsPerSheet-1
    print("Start " + str(startIndex) + " End ", str(endIndex), "Row Offset ", rowOffset)
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



    # Generate the spreadsheet entries for the border plots and label the row numbers at the end of the sheet

    for c in range(1,16):
        worksheet.write_string(rowOffset+1, c, "Borlaug 100", format)
    worksheet.write_number(rowOffset+1, 0, rowOffset+1, format2)
    worksheet.write_string(rowOffset+1, 16, "RELLENO", format)

    # Generate the data for the plots in the first sheet

    for plot in range(startIndex,endIndex+1):
        fullPlotId = plotList[plot][0]
        plotNo = plotList[plot][1]
        trial = plotList[plot][2]
        plotCol = plotList[plot][3]
        plotRow = plotList[plot][4]
        rep = plotList[plot][5]
        mapRow = rowOffset

        if startPosition=='N':
            mapCol=columnMap[trial][plotCol][0]
        elif startPosition=='S':
            mapCol=columnMap[trial][plotCol][1]

        mapPlot = plotNo
        mapRep = rep
        worksheet.write_number(mapRow, mapCol, mapPlot, format)
        # Label the row number on the map
        if columnCount == 0:
            worksheet.write_number(mapRow, 0, mapRow, format2)
        columnCount+=1
        # Label the trial on the map
        if columnCount==maxCol:
            if startPosition=='N':
                rowOffset-=1
            else:
                rowOffset+=1
            columnCount=0
            worksheet.write_string(mapRow, 16, trial, format)

    # Generate the spreadsheet entries for the border plots and label the column numbers at the start of the sheet

    for c in range(1,maxCol+1):
        worksheet.write_string(1, c, "Borlaug 100", format)
        worksheet.write_number(0, c, (c+startCol-1), format2) # label the columns

    worksheet.write_number(1, 0, 1, format2)
    worksheet.write_string(1,16,"RELLENO",format)

    worksheet.write_string(48, 1, "FECHA DE SIEMBRA", format2)
    worksheet.write_string(49, 1, plantingDate, format2)
    worksheet.write_string(50,1,"<Plantador>")

    worksheet.write_string(48, 9, "MAPA-"+str(sheet), format2)
    worksheet.write_string(48, 14, outFile, format2)

    worksheet.write_string(52, 1, "2ST/2.8M", format2)


    workbook.close()
    rowOffset=43
    startCol=startCol+maxCol
    startIndex = startIndex + maxPlotsPerSheet
    if startPosition=='N':
        startPosition='S'
        rowOffset = firstPlotRow
    elif startPosition=='S':
        startPosition='N'
        rowOffset = lastPlotRow

# Close all database connections, close the spreadsheet file and exit

close_db_connection(cursorA,cnxA)
close_db_connection(cursorB,cnxB)
close_db_connection(cursorC,cnxC)
close_db_connection(cursorD,cnxD)

sys.exit()


