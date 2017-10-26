#! /usr/bin/python
#
# Program: generate_tid-occ_to_plot-no_mapping_file.py
# Version: 0.1 October 18,2017 Initial Version
#
# Program to generate plot_id to tid-occ mapping from test files sent by CIMMYT
#
#

from pyexcel_xlsx import get_data,save_data
import sys
import csv
import os

import argparse

# Get command line input.

cmdline = argparse.ArgumentParser()

cmdline.add_argument('-f', '--file', help='Full Path to CIMMYT database input file to import')

args = cmdline.parse_args()

#inputFile = "/Users/mlucas/Desktop/KSUDatabaseCIMMYT/TID_OCC_Y16-17_OBR.xlsx"
#outputFile= "/Users/mlucas/Desktop/KSUDatabaseCIMMYT/TID_OCC _Y16-17_OBR_Database.xlsx"

inputFile = "/Users/mlucas/Desktop/KSUDatabaseCIMMYT/EYTBWMEL_01-EYTHPMEL_45_Y15-16.xlsx"

tidOccRecord=[]
tidOccList=[]


data = get_data(inputFile)

iyear='16'
ilocation='OBR'
cycle='Y15-Y16'
lastIcondition=''

index = 0
for item in data['Sheet1']:
    if index == 0:
        icondition=''
    elif index > 0:
        if index==1:
            icondition = data['Sheet1'][index][5]
            lastIcondition = icondition
        tid=data['Sheet1'][index][0]
        occ=data['Sheet1'][index][1]
        trial=data['Sheet1'][index][2]
        plotStart=data['Sheet1'][index][3]
        plotStartNum=int(plotStart)
        plotEnd=data['Sheet1'][index][4]
        plotEndNum=int(plotEnd+1)
        itrial=data['Sheet1'][index][6]
        icondition=data['Sheet1'][index][5]

        if icondition == lastIcondition:
            for plot in range(plotStartNum,plotEndNum):
                plotNum=str(plot)
                tidOccRecord = []
                plotId=iyear+'-'+ilocation+'-'+itrial +'-'+icondition+'-'+plotNum
                tidOccRecord=[plotId,tid,occ,trial,icondition]
                tidOccList.append(tidOccRecord)

        if icondition != lastIcondition:
            #outputFilePath = '/Users/mlucas/Desktop/KSUDatabaseCIMMYT/Archive/Obregon_2016-2017/YTBW' + lastIcondition + '_' + cycle + '_tidocc.csv'
            outputFilePath = '/Users/mlucas/Desktop/KSUDatabaseCIMMYT/EYT' + lastIcondition + '_' + cycle + '_tidocc.csv'
            print('Writing file: ', outputFilePath)

            # Write out the experiment file with long/lat coords

            with open(outputFilePath, 'w') as csvFile:
                header = csv.writer(csvFile,lineterminator=',\n')
                header.writerow(['plot_id', 'tid', 'occ','trial'])
                for row in tidOccList:
                    fileline = csv.writer(csvFile, quoting=csv.QUOTE_ALL, lineterminator=',\n')
                    fileline.writerow([row[0], row[1], row[2],row[3]])

            csvFile.close()
            tidOccList=[]

            for plot in range(plotStartNum,plotEndNum):
                plotNum=str(plot)
                tidOccRecord = []
                plotId=iyear+'-'+ilocation+'-'+itrial +'-'+icondition+'-'+plotNum
                tidOccRecord=[plotId,tid,occ,trial,icondition]
                tidOccList.append(tidOccRecord)

        lastIcondition = icondition
        print


    index+=1

#outputFilePath = '/Users/mlucas/Desktop/KSUDatabaseCIMMYT/Archive/Obregon_2016-2017/YTBW' + lastIcondition + '_' + cycle + '_tidocc.csv'#
outputFilePath = '/Users/mlucas/Desktop/KSUDatabaseCIMMYT/EYT' + lastIcondition + '_' + cycle + '_tidocc.csv'
print('Writing file: ', outputFilePath)
# Write out the experiment file with long/lat coords

with open(outputFilePath, 'w') as csvFile:
    header = csv.writer(csvFile,lineterminator=',\n')
    header.writerow(['plot_id', 'tid', 'occ','trial'])
    for row in tidOccList:
        fileline = csv.writer(csvFile, quoting=csv.QUOTE_ALL, lineterminator=',\n')
        fileline.writerow([row[0], row[1], row[2],row[3]])


csvFile.close()
tidOccList = []

for plot in range(plotStartNum, plotEndNum):
    plotNum = str(plot)
    tidOccRecord = []
    plotId = iyear + '-' + ilocation + '-' + itrial + '-' + icondition + '-' + plotNum
    tidOccRecord = [plotId, tid, occ, trial,icondition]
    tidOccList.append(tidOccRecord)

sys.exit()


