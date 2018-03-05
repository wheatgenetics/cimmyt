#! /usr/bin/python
#
# Program: populate_phenotypes_from_database_file.py
# Version: 0.1 September 29,2017 Initial Version
# Version: 0.2 March 1,2018 Added support for populating plots and germplasm tables.
#
# Program to load CIMMYT phenotypes table from CIMMYT database file.
#
# Order of columns in input file type A:
# 0 plot_id
# 1 iyear
# 2 ilocation
# 3 itrial
# 4 icondition
# 5 occ
# 6 trial
# 7 cid
# 8 sid
# 9 gid
# 10 cross_name
# 11 selection_history
# 12 origin
# 13 plot
# 14 rep
# 15 block
# 16 entry
# 17 phenotype_date
# 18 trait_id
# 19 phenotype_value
#
# Order of columns in input file type B:
# 0 plot_id
# 1 iyear
# 2 ilocation
# 3 itrial
# 4 icondition
# 5 cid
# 6 sid
# 7 gid
# 8 cross_name
# 9 selection_history
# 10 entry
# 11 plot
# 12 rep
# 13 phenotype_date
# 14 trait_id
# 15 phenotype_value
#
#
# CAUTION: Check data format on phenotype_date column before import as the format varies from file to file!!!
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
cmdline.add_argument('-s', '--sheet', help='Name of Excel Worksheet to Load')
cmdline.add_argument('-l', '--layout', help='Layout of input file, i.e. column order')

args = cmdline.parse_args()

inputFile = args.file
print('')
print("Loading input file: ", inputFile)

wksheet=args.sheet
print ("Processing Worksheet: ",wksheet)
print('')

fileType=args.layout

phenotypeRecord = []
phenotypeList = []

plotRecord=[]
plotList = []

germplasmRecord = []
germplasmList = []

locations={}
locations['BTN']='El Batan'
locations['FAS']='Faisalabad'
locations['JAM']='Jamalpur'
locations['JBL']='Manegaon'
locations['LDH']='Ludhiana'
locations['NJR']='Njoro'
locations['OBR']='Obregon'
locations['PUS']='Pusa'
locations['TLC']='Toluca'

# Read in the input spreadsheet (in xlsx format).
data = get_data(inputFile)

# Process data for input file of type A - See note above
if fileType=='A':
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
            if cid =='':
                cid=None
            sid = data[wksheet][index][8]
            if sid == '':
                sid = None
            gid = data[wksheet][index][9]
            if gid == '':
                gid = None
            crossName= data[wksheet][index][10]
            selectionHistory = data[wksheet][index][11]
            if selectionHistory == '':
                selectionHistory=None
            origin = data[wksheet][index][12]
            if origin == '':
                origin=None
            plot = str(data[wksheet][index][13])
            rep = str(data[wksheet][index][14])
            block = str(data[wksheet][index][15])
            entry = str(data[wksheet][index][16])
            dateStr=str(data[wksheet][index][17])
            if len(dateStr) > 0 and dateStr !='000000':
                year=dateStr[0:4]
                day = dateStr[5:7]
                month = dateStr[8:10]
                phenoDate=year + '-' + month + '-' + day
            else:
                phenoDate=None


            phenoValue=data[wksheet][index][19]
            traitId=str(data[wksheet][index][18])
            phenoPerson=None
            phenotypeRecord=[plotId,iyear,ilocation,itrial,icondition,plot,traitId,phenoValue,phenoDate,phenoPerson]
            phenotypeList.append(phenotypeRecord)

            plantingDate=None
            site=locations[ilocation]
            pyear = '20' + str(iyear)
            seedSource = origin
            location=locations[ilocation]
            cycle=None
            conditions=None
            col=None
            row=None
            purpose=None
            tid=None
            plotRecord=[plotId,iyear,ilocation,itrial,icondition,plot,trial,origin,plantingDate,site,pyear,location,cycle,
                        conditions,rep,block,col,row,entry,purpose,gid,tid,occ]
            plotList.append(plotRecord)

            germplasmRecord=[gid,cid,sid,selectionHistory,crossName]
            germplasmList.append(germplasmRecord)

        index+=1
elif fileType=='B':
    index = 0
    for item in data[wksheet]:
        if index == 0:
            pass
        elif index > 0:
            plotId = data[wksheet][index][0]
            iyear = data[wksheet][index][1]
            ilocation = data[wksheet][index][2]
            itrial = data[wksheet][index][3]
            icondition = data[wksheet][index][4]
            occ = None
            trial = None
            cid = data[wksheet][index][5]
            if cid == '':
                cid = None
            sid = data[wksheet][index][6]
            if sid == '':
                sid = None
            gid = data[wksheet][index][7]
            if gid == '':
                gid = None
            crossName = data[wksheet][index][8]
            selectionHistory = data[wksheet][index][9]
            if selectionHistory == '':
                selectionHistory = None
            origin = None
            entry = str(data[wksheet][index][10])
            plot = str(data[wksheet][index][11])
            rep = str(data[wksheet][index][12])
            block = None
            entry = None
            phenoValue = data[wksheet][index][13]
            traitId = str(data[wksheet][index][14])
            dateStr = str(data[wksheet][index][15])
            if len(dateStr) > 0 and dateStr != '000000':
                year = dateStr[0:4]
                day = dateStr[5:7]
                month = dateStr[8:10]
                phenoDate = year + '-' + month + '-' + day
            else:
                phenoDate = None

            phenoPerson = None
            phenotypeRecord = [plotId, iyear, ilocation, itrial, icondition, plot, traitId, phenoValue, phenoDate,
                               phenoPerson]
            phenotypeList.append(phenotypeRecord)

            plantingDate = None
            site = locations[ilocation]
            pyear = '20' + str(iyear)
            seedSource = origin
            location = locations[ilocation]
            cycle = None
            conditions = None
            col = None
            row = None
            purpose = None
            tid = None
            plotRecord = [plotId, iyear, ilocation, itrial, icondition, plot, trial, origin, plantingDate, site, pyear,
                          location, cycle,
                          conditions, rep, block, col, row, entry, purpose, gid, tid, occ]
            plotList.append(plotRecord)

            germplasmRecord = [gid, cid, sid, selectionHistory, crossName]
            germplasmList.append(germplasmRecord)

        index += 1
else:
    print("Unknown File Type...exiting")
    sys.exit()

inputRecordCount=index

# Open the database connections required (1 per table).

print("")
print("Connecting to Database...",config.DATABASE)

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
    cursorB = cnx.cursor(buffered=True)
    cursorC = cnx.cursor(buffered=True)

# Insert the plot data - this must be done due to foreign key constraints on phenotypes table
# Ignore rows with duplicate plot_id

insert_plot = "INSERT INTO plots (plot_id,iyear,ilocation,itrial,icondition,plot_no,trial,seed_source,planting_date,site,year," \
              "location,cycle,conditions,rep,block,col,row,entry,purpose,gid,tid,occ) " \
              "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
plotInserts=0

print("")
print("Inserting plot records...")

for p in plotList:
    try:
        plotRow=(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14],p[15],p[16],p[17],p[18],
                 p[19],p[20],p[21],p[22])
        cursorB.execute(insert_plot,plotRow)
        cnx.commit()
        plotInserts+=1
    except mysql.connector.Error as err:
        if err.errno==errorcode.ER_DUP_ENTRY:
            continue
        elif err.errno==errorcode.ER_BAD_NULL_ERROR:
            continue
        else:
            print(err,plotInserts,p[20])
cursorB.close()

# Insert the phenotypes data

insert_phenotype = "INSERT INTO phenotypes (plot_id,iyear,ilocation,itrial,icondition,plot_no,trait_id,phenotype_value," \
                   "phenotype_date,phenotype_person) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
phenoInserts=0

print("")
print("Inserting phenotype records...")

for p in phenotypeList:
    try:
        phenoRow=(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9])
        cursorA.execute(insert_phenotype,phenoRow)
        cnx.commit()
        phenoInserts+=1
    except mysql.connector.Error as err:
        print(err) # Program will exit if error occurs
cursorA.close()

# Insert the germplasm data - ignore rows where gid is not present.

insert_germplasm = "INSERT INTO germplasm () Values(%s,%s,%s,%s,%s)"
germplasmInserts=0

print("")
print("Inserting germplasm records...")

for g in germplasmList:
    try:
        germplasmRow=(g[0],g[1],g[2],g[3],g[4])
        cursorC.execute(insert_germplasm,germplasmRow)
        cnx.commit()
        germplasmInserts+=1
    except mysql.connector.Error as err:
        if err.errno==errorcode.ER_DUP_ENTRY:
            continue
        elif err.errno==errorcode.ER_BAD_NULL_ERROR:
            continue
        else:
            print(err,germplasmInserts,g[0])
cursorC.close()

print("")
print("Input Records processed:     ",inputRecordCount)
print("Phenotype Records inserted : ",phenoInserts)
print("Plot Records Inserted:       ",plotInserts)
print("Germplasm Records Inserted:  ", germplasmInserts)

sys.exit()


