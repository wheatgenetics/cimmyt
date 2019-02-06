#! /usr/bin/python
#
# Program: generate_mexico_fieldbook_files_from_database.py
# Version: 0.1 October 26,2017 Initial Version
#
# Program to generate Mexico fieldbook data files from CIMMYT plots and germplasm tables.
#
#

import mysql.connector
from mysql.connector import errorcode
import test_config
import sys
import csv
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

cmdline = argparse.ArgumentParser()

cmdline.add_argument('-y','--year',help='The iyear to generate fieldbook file for')
cmdline.add_argument('-l','--location',help='The ilocation to generate fieldbook file for', default='OBR')
#cmdline.add_argument('-t','--trial',help='The itrial to generate fieldbook file for')
cmdline.add_argument('-c','--condition',help='The icondition to generate fieldbook file for')


args=cmdline.parse_args()

fyear=args.year
flocation=args.location
#itrial=args.trial
fcondition=args.condition
#plotId=iyear+'-'+ilocation+'-'+itrial+'-'+icondition+'%'

fieldBookRecord=[]
fieldBookList=[]



#fieldBookQuery="Select plots.plot_id,plots.plot_no,plots.rep,plots.entry,concat(plots.itrial,plots.icondition) " \
#               "as trial,germplasm.gid,germplasm.cross_name as pedigree from plots,germplasm " \
#               "where plots.gid=germplasm.gid and plots.plot_id like %s order by plots.plot_no"

fieldBookQuery="Select plots.plot_id,plots.plot_no,plots.rep,plots.entry,plots.trial " \
               "as trial,germplasm.gid,germplasm.cross_name as pedigree from plots,germplasm " \
               "where plots.gid=germplasm.gid and (plots.iyear=%s and plots.ilocation=%s and plots.icondition=%s) " \
               "order by trial,plots.plot_id"


print("")
print("Connecting to Database...")
cursorA,cnxA=open_db_connection(test_config)
cursorA.execute(fieldBookQuery, (fyear,flocation,fcondition ))
print()
print("Number of records found for icondition " + fcondition + ' for ' + fyear + '-' + flocation + " = " +
      str(cursorA.rowcount))

if cursorA.rowcount != 0:

    for rowA in cursorA:
        plot        = rowA[0]
        plotNo      = rowA[1]
        rep         = rowA[2]
        entry       = rowA[3]
        trial       = rowA[4]
        gid         = rowA[5]
        crossName   = rowA[6].strip() # N.B. Stripped trailing \r character from cross_name field
        fieldBookRecord=[plot,plotNo,rep,entry,trial,gid,crossName]
        fieldBookList.append(fieldBookRecord)
else:
    print("No Records Found For icondition: " + fcondition)
    close_db_connection(cursorA, cnxA)
    sys.exit()

startPlot=str(fieldBookList[0][1])
endPlot=str(fieldBookList[-1][1])
outFile="Fieldbook_" + fyear + '-' + flocation + '-' + fcondition +'.csv'
print('Generating Field Book CSV file: ' + outFile )
#
# Write out the metadata file
#
with open(outFile, 'w') as csvfile:
    header = csv.writer(csvfile)
    header.writerow(
        ['plot_id','plot_no','rep','entry','trial','gid','cross_name'])
csvfile.close()

with open(outFile, 'a') as csvfile:
    for lineitem in fieldBookList:
        fileline = csv.writer(csvfile)
        fileline.writerow([lineitem[0], lineitem[1], lineitem[2],lineitem[3], lineitem[4], lineitem[5], lineitem[6]])

print()
print('Closing database connection and exiting ...')
csvfile.close()
sys.exit()
