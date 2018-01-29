#! /usr/bin/python
#
# Program: convert_cimmyt_asia_table_to_database_format.py
# Version: 0.1 October 18,2017 Initial Version
# Version: 0.2 January 22,2018 NB Fixed error where itrial and icondition columns were swapped - line 110
#
# Program to generate database load files from phenotype spreadsheet from India/Bangla Desh/Pakistan
#
#

import csv
import sys

#tableFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_with_plot_id_JBL.csv'
#dbFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_JBL_DB.csv'

#tableFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_with_plot_id_LDH.csv'
#dbFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_LDH_DB.csv'

tableFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_with_plot_id_PUS.csv'
dbFile='/Users/mlucas/Desktop/KSUDatabaseCIMMYT/SABWGPYT00-Master_File-GS2015-16/SABWGPYT00-Master_File-GS2015-16_PUS_DB.csv'


traits={}
dbFileList=[]
newLine = '\n'

traits['Germi'] = 'GERMPCT'
traits['GroundCovr'] = 'GrndCov'
traits['Booting'] = 'DTB'
traits['Heading'] = 'DTHD'
traits['Height'] = 'PH'
traits['Maturity'] = 'DAYSMT'
traits['Lodg%'] = 'LOI'
traits['Yield(t/ha)'] = 'GRYLD'
traits['FL_Len'] = 'FLGLF'
traits['FL_Wdh'] = 'FLGLFW'
traits['Spike_Len'] = 'SpkLng'
traits['TGW'] = 'TGW'
traits['Remark'] = 'NOTES'
traits['Agron_Scor'] = 'AgrScr'
traits['NDVI'] = 'NDVI'
traits['CT'] = 'CT'

with open(tableFile,'rU') as csvFile:
    #skipLine=csvFile.next()
    next(csvFile)

    rowReader=csv.reader(csvFile)
    rowIndex=0
    for row in rowReader:
        if rowIndex==0:
            dates=row
            dateIndex=20
            for d in dates:
                if d != '':
                    dateStrs=d.split('/')
                    year='20'+ dateStrs[2]
                    month=dateStrs[0].zfill(2)
                    day=dateStrs[1].zfill(2)
                    newDate=year+'-'+ month + '-' + day
                    dates[dateIndex]=newDate
                    dateIndex+=1
        elif rowIndex==1:
            header=row
        else:
            dbRow=row[0:6]
            singleTraitColumns=row[6:20]
            #ndviColumns=row[20:34] # for JBL data
            #ctColumns=row[34:47] # for JBL data
            #ndviColumns=row[47:62] # for LDH data
            #ctColumns=row[62:72] # for LDH data
            ndviColumns = row[72:84]  # for PUS data
            ctColumns = row[84:95]  # for PUS data
            colIndex=6
            for col in singleTraitColumns:
                traitId=traits[header[colIndex]]
                traitValue=col
                traitDate='0000-00-00'
                dbRow+=traitId,traitValue,traitDate
                colIndex+=1
                dbFileList.append(dbRow)
                dbRow = row[0:6]
            #colIndex = 47  # for LDH
            colIndex = 72  # for PUS
            for col in ndviColumns:
                traitId=traits[header[colIndex][0:4]]
                traitValue=col
                traitDate=dates[colIndex]
                dbRow += traitId, traitValue,traitDate
                colIndex+=1
                dbFileList.append(dbRow)
                dbRow = row[0:6]
            #colIndex = 62  # for LDH
            colIndex = 84  # for PUS
            for col in ctColumns:
                traitId = traits[header[colIndex][0:2]]
                traitValue = col
                traitDate = dates[colIndex]
                dbRow += traitId, traitValue,traitDate
                colIndex += 1
                dbFileList.append(dbRow)
                dbRow = row[0:6]
        rowIndex += 1
#
# Write out the metadata file
#
with open(dbFile, 'w') as csvfile:
    header = csv.writer(csvfile)
    #header.writerow(
        ['plot_id','iyear','ilocation','icondition','itrial','plot_no','trait_id','phenotype_value','phenotype_date'])
    header.writerow(['plot_id', 'iyear', 'ilocation', 'itrial','icondition',  'plot_no', 'trait_id', 'phenotype_value', 'phenotype_date'])
csvfile.close()

with open(dbFile, 'a') as csvfile:
    print ('Generating database file', dbFile)
    for lineitem in dbFileList:
        fileline = csv.writer(csvfile)
        fileline.writerow([lineitem[0], lineitem[1], lineitem[2],lineitem[3], lineitem[4], lineitem[5], lineitem[6], lineitem[7],lineitem[8]])

csvfile.close()
sys.exit()

