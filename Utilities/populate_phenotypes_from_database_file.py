#! /usr/bin/python
#
# Program: populate_phenotypes_from_database_file.py
# Version: 0.1 September 29,2017 Initial Version
#
# Program to load CIMMYT phenotypes table from CIMMYT database file.
#
#

from pyexcel_xlsx import get_data
import sys
import mysql.connector
from mysql.connector import errorcode
import config
import argparse

# Get command line input.

cmdline = argparse.ArgumentParser()

cmdline.add_argument('-f', '--file', help='Full Path to CIMMYT database input file to import')

args = cmdline.parse_args()

inputFile = args.file

phenotypeRecord = []
phenotypeList = []


data = get_data(inputFile)

index = 0
for item in data['Sheet1']:
    if index == 0:
        pass
    elif index > 0:
        plotId=data['Sheet1'][index][0]
        iyear=data['Sheet1'][index][1]
        ilocation=data['Sheet1'][index][2]
        itrial=data['Sheet1'][index][3]
        icondition=data['Sheet1'][index][4]
        occ =data['Sheet1'][index][5]
        trial=data['Sheet1'][index][6]
        cid=data['Sheet1'][index][7]
        sid = data['Sheet1'][index][8]
        gid = data['Sheet1'][index][9]
        crossName= data['Sheet1'][index][10]
        selectionHistory = data['Sheet1'][index][11]
        origin = data['Sheet1'][index][12]
        plot = str(data['Sheet1'][index][13])
        rep = str(data['Sheet1'][index][14])
        block = str(data['Sheet1'][index][15])
        entry = str(data['Sheet1'][index][16])
        dateStr=str(data['Sheet1'][index][17])
        if len(dateStr) > 0:
            year='20'+ dateStr[0:2]
            month = dateStr[2:4]
            day = dateStr[4:6]
            phenoDate=year + '-' + month + '-' + day
        else:
            phenoDate=None

        phenoValue=data['Sheet1'][index][18]
        traitId=str(data['Sheet1'][index][19])
        phenoPerson=None
        phenotypeRecord=[plotId,iyear,ilocation,itrial,icondition,plot,traitId,phenoValue,phenoDate,phenoPerson]
        phenotypeList.append(phenotypeRecord)

    index+=1

print("")
print("Connecting to Database...")

try:
    cnx = mysql.connector.connect(user=config.USER, password=config.PASSWORD, host=config.HOST,
                                      port=config.PORT,database=config.DATABASE)
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


