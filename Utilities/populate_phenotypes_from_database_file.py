#! /usr/bin/python
#
# Program: populate_phenotypes_from_database_file.py
# Version: 0.1 September 29,2017 Initial Version
#
# Program to load CIMMYT phenotypes table from CIMMYT database file.
#
# N.B. Check order of columns in input file as it is not consistently the same!!
#
#

from pyexcel_xlsx import get_data
import sys
import mysql.connector
from mysql.connector import errorcode
import test_config
import argparse

# Get command line input.

cmdline = argparse.ArgumentParser()

cmdline.add_argument('-f', '--file', help='Full Path to CIMMYT database input file to import')
cmdline.add_argument('-s', '--sheet', help='Name of Excel Worksheet to Load')

args = cmdline.parse_args()

inputFile = args.file
wksheet=args.sheet

phenotypeRecord = []
phenotypeList = []


data = get_data(inputFile)

index = 0
for item in data[wksheet]:
    if index == 0:
        pass
    elif index > 0:
        plotId=data[wksheet][index][0]
        iyear=data[wksheet][index][1]
        ilocation=data[wksheet][index][2]
        itrial=data[wksheet][index][3]
        icondition=data[wksheet][index][4]
        occ =data[wksheet][index][5]
        trial=data[wksheet][index][6]
        cid=data[wksheet][index][7]
        sid = data[wksheet][index][8]
        gid = data[wksheet][index][9]
        crossName= data[wksheet][index][10]
        selectionHistory = data[wksheet][index][11]
        origin = data[wksheet][index][12]
        plot = str(data[wksheet][index][13])
        rep = str(data[wksheet][index][14])
        block = str(data[wksheet][index][15])
        entry = str(data[wksheet][index][16])
        dateStr=str(data[wksheet][index][17])
        if len(dateStr) > 0 and dateStr !='000000':
            year='20'+ dateStr[0:2]
            month = dateStr[2:4]
            day = dateStr[4:6]
            phenoDate=year + '-' + month + '-' + day
        else:
            phenoDate=None

        phenoValue=data[wksheet][index][19]
        traitId=str(data[wksheet][index][18])
        phenoPerson=None
        phenotypeRecord=[plotId,iyear,ilocation,itrial,icondition,plot,traitId,phenoValue,phenoDate,phenoPerson]
        phenotypeList.append(phenotypeRecord)

    index+=1
    print(index)

print("")
print("Connecting to Database...")

try:
    cnx = mysql.connector.connect(user=test_config.USER, password=test_config.PASSWORD, host=test_config.HOST,
                                      port=test_config.PORT,database=test_config.DATABASE)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursorA = cnx.cursor(buffered=True)

insert_phenotype = "INSERT INTO phenotypes (plot_id,iyear,ilocation,itrial,icondition,plot_no,trait_id,phenotype_value,phenotype_date,phenotype_person) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

phenoInserts=0
for p in phenotypeList:
    phenoRow=(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9])
    print(phenoInserts,phenoRow)
    cursorA.execute(insert_phenotype,phenoRow)
    cnx.commit()
    phenoInserts+=1
cursorA.close()


sys.exit()


