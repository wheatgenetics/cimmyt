## Tools for CIMMYT Data Automation

### convert_iwis_to_db_plots_germplasm

This program will take a CIMMYT IWIS Excel .xls export file that contains plot and germplasm data in each row and populates
the plot and germplasm tables in the CIMMYT database.

Note that multiple rows can occur for each GID in the IWIS file due to the fact that there are replicated plots
which will have the same GID. The duplicate GID is eliminated by using GID in the dictionary germplasmDict. The same
approach is used for plot_id in the dictionary plotDict.

The Excel file structure is:

Row 1 Col 1: 'TID'        Row 1 Col 2: <tid value>

Row 2 Col 1: 'OCC'        Row 2 Col 2: <occ value>

Row 3 Col 1: 'Trial Name' Row 3 Col 2: <trial name value>

Row 4 Col 1: 'Trial Abbr' Row 4 Col 2: <trial abbreviation value>

Row 5 Col 1: 'Cycle'      Row 5 Col 2: <cycle value>

Row 6 Col 1: 'Program'    Row 6 Col 2; <program value>

Row 7 Blank

Row 8 Column Headings for plot and germplasm data columns

  Column 1: CID

  Column 2: SID

  Column 3: GID

  Column 4: Cross Name

  Column 5: Selection History

  Column 6: Origin (Seed Source)

  Column 7: Plot

  Column 8: Rep

  Column 9: SubBlock

  Column 10: Entry

Row 9 to EOF: plot and germplasm data values

**INPUT Parameters:**

-i, --input Full path to the IWIS input file e.g T66_047345_001.xls

-l, --location Location of the plots, default = 'OBR'

 **OUTPUTS:**

New plots found in the IWIS file will be inserted into the database table cimmyt.plots

New germplasm data found in the IWIS file will be inserted into the database table cimmyt.germplasm

Error Handling:

If any error occurs while attempting to insert into plots table, an exception will be thrown and the program exited.

If any error occurs while attempting to insert into germplams table, an exception will be thrown and the program
exited. However, note that the insert statement used to insert into the germplasm table allows duplicate key errors
to be ignored.

Note that there are some variants of this program that handle slightly different input formats:

### convert_iwis_to_db_plots_germplasm_segregated

This version will handle a different IWIS format for segregated populations F6-F7

N.B.Loading of germplasm table is disabled since all fields required are not in the input file e.g. selection_history.

The Excel file structure for F6-F7 Segregated populations is as follows:

Row 1 Col 1: 'TID'        Row 1 Col 2: <tid value>

Row 2 Col 1: 'OCC'        Row 2 Col 2: <occ value>

Row 3 Col 1: 'Trial Name' Row 3 Col 2: <trial name value>

Row 4 Col 1: 'Trial Abbr' Row 4 Col 2: <trial abbreviation value>

Row 5 Col 1: 'Cycle'      Row 5 Col 2: <cycle value>

Row 6 Col 1: 'Program'    Row 6 Col 2; <program value>

Row 7 Blank

Row 8 Column Headings for plot and germplasm data columns

  Column 0: Entry

  Column 1: CID

  Column 2: SID

  Column 3: GID

  Column 4: Cross Name

  Column 5: Plot

  Column 8: Rep

Row 9 to EOF: plot and germplasm data values


### generate_fieldbook_files_from_database_by_condition_and_trial

This program will generate CIMMYT Field Book import files from plots and germplasm tables in the cimmyt database.

**INPUT Parameters:**

-y,--year,help=The iyear to generate fieldbook file for
-l,--location,help=The ilocation to generate fieldbook file for, default=OBR
-t,--trial,help=The itrial to generate fieldbook file for
-c,--condition,help=The icondition to generate fieldbook file for

**OUTPUTS:**

A csv file containing data for import into Field Book.

The file naming convention is:

Fieldbook_<year>_<location>_<trial>_<condition>.csv

***Example:***

Fieldbook_19_OBR_YTBW_B5I.csv

### generate_fieldbook_files_from_database_by_condition

This program will generate CIMMYT Field Book import files from plots and germplasm tables in the cimmyt database.
It will generate one file for all trials and conditions for a given year and location.

**INPUT Parameters:**

-y,--year,help=The iyear to generate fieldbook file for
-l,--location,help=The ilocation to generate fieldbook file for, default=OBR
-c,--condition,help=The icondition to generate fieldbook file for

**OUTPUTS:**

A csv file containing data for import into Field Book.

The file naming convention is:

Fieldbook_<year>_<location>_<condition>.csv

***Example:***

Fieldbook_19_OBR_B5I.csv

### generate_fieldbook_files_from_database_by_tidocc

This program will generate CIMMYT Field Book import files from plots and germplasm tables in the cimmyt database.
It will generate one file for a given tid occ combination (i.e. for one trial).

**INPUT Parameters:**

'-t','--tid',help='The tid to generate fieldbook file for'
'-o','--occ',help='The occ to generate fieldbook file for'

**OUTPUTS:**

A csv file containing data for import into Field Book.

The file naming convention is:

Fieldbook_<trial>_plots_<start_plot>_<end_plot>.csv

***Example:***

FieldBook_YTHPB5IR_06_plots-601-690.csv

### read_and_annotate_field_map

This program will read a CIMMYT Mexico field map in xlsx format, look up the full plot_id for each plot in the plots
table, generate annotation data for each plot-no with full plot_id, row and column identifiers and generate a new
field map including the annotated plot_id information.

As a secondary task it will populate the row,column database columns for each plot

Note Row and Column Indices in xlsxWriter are zero based.

References:
  1. pandas: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_excel.html
  2. Xlsxwriter: https://xlsxwriter.readthedocs.io

**INPUT Parameters:**

-f,--folder,help=The full path to the folder containing the field map files.
-i,--infile,help=The field map input file name.
-o,--outfile,help=The annotated field map output file name.
-y,--year,help=The iyear to generate field map file for
-l,--location,help=The ilocation to generate field map file for, default='OBR'
-t,--trial,help=The itrial to generate field map file for
-c,--condition,help=The icondition to generate field map file for

**OUTPUT**

An xlsx file with name being a concatenation of the folder and outfile input parameters.

Example:

-f = /Desktop/EYTBW-Fieldmaps/
-i = EYTBW-Flat-5IR_101-390.xlsx
-o = EYTBW-Flat-5IR_101-390_a.xlsx (_a indicates annotated)

Filename: /Desktop/EYTBW-Fieldmaps/EYTBW-Flat-5IR_101-390_a.xlsx

### read_and_annotate_field_map_F5I

### read_and_annotate_field_map_F6-F7

**OUTPUT**

An xlsx file with name being a concatenation of the folder and outfile input parameters.

Example:

-f = /Desktop/F6-F7-Fieldmaps/
-i = PCBW_1-1100-SPC.xlsx
-o = PCBW_1-1100-SPC_a.xlsx (_a indicates annotated)

Filename: /Desktop/Fieldmap_Updates_2018/F6-F7-Fieldmaps/PCBW_1-1100-SPC_a.xlsx


### read_plot_shapefile

This program will read a shapefile representing one or more plots and store them as plot polygons in the cimmyt plot_map
table.

**INPUT Parameters:**

-i, --input,help= Path to Shapefile to import into the database.

**OUTPUT**

Database plot_map table populated with plots found in shape file.


### write_plot_shapefile

This program will read one or more plot polygons from the cimmyt plot_map able and write them to a shapefile.

-p, --plotID , help= Plot_id or partial plot_id of plot polygon(s) to be extracted SQL % symbol will select all plots.

-o, --output ,help= Shapefile to be created...