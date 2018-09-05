#! /usr/bin/python
#
# Program: read_and_annotate_field_map.py
#
# Version: 0.1 January 23,2018 Initial Version
# Version: 0.2 February 6,2018 Corrected error where row and column were transposed.
#
# This program will read a CIMMYT Mexico field map in xlsx format, look up the full plot_id for each plot in the plots
# table, generate annotation data for each plot-no with full plot_id, row and column identifiers and generate a new
# field map including the annotated plot_id information.
#
# As a secondary task it will populate the row,column database columns for each plot
#
# Note Row and Column Indices in xlsxWriter are zero based.
#
# References:
#   1. pandas: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html
#   2. Xlsxwriter: https://xlsxwriter.readthedocs.io
#
#

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

import xlsxwriter

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

# Get command line input.
# Note that some of these may be input via other means in the future e.g. reading from a document of spreadsheet.

cmdline = argparse.ArgumentParser()
cmdline.add_argument('-f','--folder',help='The full path to the folder containing the field map files.')
cmdline.add_argument('-i','--infile',help='The field map input file name.')
cmdline.add_argument('-o','--outfile',help='The annotated field map output file name.')
cmdline.add_argument('-y','--year',help='The iyear to generate field map file for')
cmdline.add_argument('-l','--location',help='The ilocation to generate field map file for', default='OBR')
cmdline.add_argument('-t','--trial',help='The itrial to generate field map file for')
cmdline.add_argument('-c','--condition',help='The icondition to generate field map file for')

# Assign variables to command line arguments

args=cmdline.parse_args()

fieldMapFolder=os.path.join(args.folder, '')
fieldMapInFile=os.path.join(fieldMapFolder,args.infile)
fieldMapOutFile=os.path.join(fieldMapFolder,args.outfile)
print()
print('Processing field map input file: '+ fieldMapInFile)
print('Annotated field map output file: ' + fieldMapOutFile)
print()
iyear=args.year
ilocation=args.location
itrial=args.trial
icondition=args.condition
plotId=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'%'
plotPrefix=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'-'
print('Processing plots: '+ plotId)

# Read in the field map input file and determine the dimensions of the field map

fieldMap = pd.read_excel(fieldMapInFile)
numRows=fieldMap.shape[0]
numCols=fieldMap.shape[1]
r=range(numRows)
c=range(numCols)
print('Rows:',r)
print('Columns:',c)

plotColOffset=2 # Indicates offset from first column in spreadsheet to the first column where data is present.
plotRowOffset=0 # Indicates offset from first row in spreadsheet to first row where data is present.

# Connect to database - Create one cursor per query

print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(test_config)
updatePlot='UPDATE plots SET row=%s,col=%s WHERE plot_id = %s'

# Open .xlsx output file and set up worksheet formatting
workbook = xlsxwriter.Workbook(fieldMapOutFile)
worksheet = workbook.add_worksheet()
format = workbook.add_format()
worksheet.set_column(2, 16, 40.0)
worksheet.set_column(18,18, 15.0)
format.set_border()

# Write the header row for the workbook and get the list of column subscripts
# fieldmap.axes[1] is the list of column labels for the fieldmap (including unlabelled columns '' or Unnamed).
# write_number parameters: (row, col, number [, cell_format ])
# write_string parameters: (row, col, string [, cell_format ])

columnList=[]
for column in range(numCols):
    if str(fieldMap.axes[1][column]).isdigit():
        worksheet.write_number(0, column, fieldMap.axes[1][column], format)
        columnList.append(fieldMap.axes[1][column])
    else:
        worksheet.write_string(0, column, '', format)

# Get the list of row subscripts for the input fieldmap
rowList=[]
for row in range(numRows-1):
    rowList.append(fieldMap.iloc[row:row + 1].values[0,0])

# Write the rest of rows of the workbook
# plotColOffset identifies the first spreadsheet column that contains a plot number
# numCols -1 identifies the last spreadsheet column that contains a plot number
# rows-2 is the last spreadsheet row that contains a plot number
print('Writing field map spreadsheet')
for row in range(numRows):
   for column in range(numCols):
       cellValue=str(fieldMap.iloc[row:row + 1, column:column + 1].values[0,0])
       isPlotNumber=cellValue.isdigit()
       if (column >=plotColOffset and column <=numCols-1) and (row<=numRows-2) and isPlotNumber:
            fullPlotId=plotPrefix+cellValue
            mapPlotCol = str(columnList[column - plotColOffset])
            mapPlotRow = str(rowList[row])
            mapPlot='R:'+ mapPlotRow +' C:'+  mapPlotCol + ' ' + fullPlotId
            worksheet.write_string(row+1,column,mapPlot, format)
            print('Updating plot '+ fullPlotId)
            cursorA.execute(updatePlot, (int(mapPlotRow),int(mapPlotCol),fullPlotId))
            cnxA.commit()
       elif cellValue!='nan':
           # Write any values that are not plot numbers i.e. RELLENO column values
           worksheet.write_string(row+1,column,cellValue,format)
       else:
           # Otherwise, just write out an empty cell.
           worksheet.write_string(row+1, column, '', format)

worksheet.set_landscape()
worksheet.fit_to_pages(1,1)

workbook.close()

# Close all database connections, close the spreadsheet file and exit

close_db_connection(cursorA,cnxA)

print('Completed')
