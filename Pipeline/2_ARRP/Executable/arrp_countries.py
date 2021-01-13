#!/usr/bin/env python
"""
Extracts json data from the OWID COVID-19 json file.

The OWID json file contains 3-letter country codes and its own locations.
"""

# Import libraries
import argparse
from sys import exit
from os import system, mkdir
from os.path import exists, isfile
from pandas import DataFrame
import datetime
import math
from time import time
from json import load

ofbn = 'slope'

def main(): 
    parser = getArguments()
    argument = parser.parse_args()
    check( argument )  
    
    # Loads OWID COVID-19 json file.
    start = time()
    print( f'-- Reading "{argument.json_file}" started --', flush=True )
    with open( f'{argument.idir}{argument.json_file}' ) as iFH:
        code2data = load( iFH )
    print( f'-- Reading "{argument.json_file}" ended --', flush=True )
    print( f'-- Elapsed time { int( time() - start ) } secs --', flush=True )
    code2country = code2country_( code2data )
    print( f'-- Writing "{argument.odir}code2country.json" ended --', flush=True )
    print( f'-- Elapsed time { int( time() - start ) } secs --', flush=True )
    # Writes asymptotic regression data, output, and summary files.
    colS = [ 'code', 'country', 'slope', 'error', 'number_of_points', 'start_date', 'end_date' ]
    index = 0
    head2arrpout = dict()
    for col in colS:
        head2arrpout[ col ] = []
    print( f'-- Writing regression files started --', flush=True )
    codeS = sorted( code2country.keys() ) # OWID country codes
    for code in codeS:
        print( f'-- "{code2country[ code ]}" started --', flush=True )
        oFBC = f'{argument.odir}{argument.cdir}{code}' # basename of output files for code
        name2data = name2data_( argument, code, code2data )
        pointS = name2data[ "pointS" ]
        startDashDate = name2data[ "startDashDate" ]
        if len( pointS ) < 2:
             print( f'-- arrp needs at least 2 points to regress --', flush=True )
        else:   
            with open( f'{oFBC}.dat', 'w' ) as oFH:
                for point in pointS:
                    oFH.write( "%d\t%f\t%f\n" % ( point["x"], point["y"], point["error"] ) )
            try:
                system( f'arrp.exe -in {oFBC}.dat -out {oFBC}.out -include left 1> /dev/null 2> /dev/null' )
            except:
                print( f'-- "{code2country[ code ]}" arrp threw an error --', flush=True )
        if isfile( f'{oFBC}.out' ):
            addTo_head2arrpout_( head2arrpout, colS, code, code2country[ code ], startDashDate, f'{oFBC}.out' )
        index += 1
            # addTo_head2arrpout_( code, code2country[ code ], head2arrpout, startDashDate, f'{oFBC}.out' )
        print( f'-- Elapsed time { int( time() - start ) } secs --', flush=True )
    print( f'-- Writing regression files ended --', flush=True )
    print( f'-- Elapsed time { int( time() - start ) } secs --', flush=True )
    # csv output 
    df = DataFrame(head2arrpout, columns=colS)
    df.to_csv(f'{argument.odir}{ofbn}.csv', index = False)      
    # https://stackoverflow.com/questions/18695605/python-pandas-dataframe-to-dictionary  

# Adds a line to outS from the arrp output file.    
def addTo_head2arrpout_( head2arrpout, colS, code, country, startDashDate, iFC ): 
    with open( iFC ) as iFH: # Runs if regression succeeds.
        lines = iFH.readlines()
        line = lines.pop(0)
        while lines and not line.startswith( 'beta1' ):
            line = lines.pop(0)
        line.rstrip()
        fieldS = line.split() # Splits on whitespace.
        value = { "slope": float( fieldS[ 1 ] ), "error": float( fieldS[ 3 ] ) }
        while lines and not line.startswith( "X" ):
           line = lines.pop(0)
        line.rstrip()
        numberPoints = 0
        weight = '1'
        while lines and weight == '1':
            line = lines.pop(0)
            line.rstrip()
            fieldS = line.split() # Splits on whitespace.
            weight = fieldS[ 3 ]
            if weight == '1':
                numberPoints += 1
        endDate = datetime.datetime.strptime( startDashDate, "%Y-%m-%d" ).date() + datetime.timedelta( days = numberPoints - 1 )
        endDashDate = endDate.strftime( "%Y-%m-%d" )
        # Constructs the fieldS.
        #     colS = [ 'index', 'code', 'country', 'slope', 'error', 'number_of_points', 'start_date', 'end_date' ]
        headS = list(colS)
        head2arrpout[ headS.pop(0) ].append(str(code))
        head2arrpout[ headS.pop(0) ].append(str(country))
        head2arrpout[ headS.pop(0) ].append(str(value[ "slope" ]))
        head2arrpout[ headS.pop(0) ].append(str(value[ "error" ]))
        head2arrpout[ headS.pop(0) ].append(str(numberPoints))
        head2arrpout[ headS.pop(0) ].append(str(startDashDate))
        head2arrpout[ headS.pop(0) ].append(str(endDashDate))
        assert not headS
    
# Returns points for COVID-19 ARRP input file.    
def name2data_( argument, code, code2data ): 
    DATUM_FOR_THRESHOLD = argument.datum_for_threshold
    THRESHOLD = argument.threshold
    NEW_CASES = argument.new_cases
    ST_DEV_FACTOR = argument.st_dev_factor

    pointS = []
    startDashDate = ""
    for datum in code2data[ code ][ "data" ]:
        # Starts pointS whe total cases = THRESHOLD. NYT uses 100 new cases.
        if not startDashDate:
            if DATUM_FOR_THRESHOLD in datum and THRESHOLD <= datum[ DATUM_FOR_THRESHOLD ]:
                startDashDate = datum[ "date" ]
                startDate = datetime.datetime.strptime( startDashDate, "%Y-%m-%d" ).date()
            else:
                continue
        # DATUM_FOR_THRESHOLD has exceeded THRESHOLD.
        nextNewCases = datum[ NEW_CASES ]
        # Stops if 0,1 new cases on the next day.
        if nextNewCases <= 1.0: 
            break
        # Appends the points for asymptotic regression to the list.
        nextDashDate = datum[ "date" ]
        nextDate = datetime.datetime.strptime( nextDashDate, "%Y-%m-%d" ).date()
        x = (nextDate - startDate).days # days after 2019-12-31
        y = math.log( nextNewCases ) # linear for the initial exponential rise
        # Multiplies the error by a factor to compensate for smoothing (if any).
        error = math.pow( y, -0.5 ) * ST_DEV_FACTOR # Poisson error based on the same day
        point = {"x": x, "y": y, "error": error }
        pointS.append( point )
    return { "pointS": pointS, "startDashDate": startDashDate }
        
# Writes code2country.    
def code2country_( code2data ): 
    code2country = dict()
    for code in code2data.keys():
        code2country[ code ] = code2data[ code ][ "location" ]
    return code2country
        
# Check and fixes arguments if possible.    
def check( argument ): 
    if not exists( argument.idir ):
        print( f'Error: a valid INPUT_DIRECTORY "{argument.idir}" is required.' )
        exit()
    if not argument.idir.endswith( '/' ):
        argument.idir = f'{argument.idir}/'
    if not isfile( f'{argument.idir}{argument.json_file}' ):
        print( f'Error: a valid INPUT_JSON_FILE "{argument.idir}{argument.json_file}" is required.' )
        exit()
    
    if not argument.odir.endswith( '/' ):
        argument.odir = f'{argument.odir}/'
    if not exists( argument.odir ):
        mkdir( f'{argument.odir}' )
    if not argument.cdir.endswith( '/' ):
        argument.cdir = f'{argument.cdir}/'
    if not exists( f'{argument.odir}{argument.cdir}' ):
        mkdir( f'{argument.odir}{argument.cdir}' )

def getArguments():
    parser = argparse.ArgumentParser(description='The program extracts json data from the OWID COVID-19 json file.')
    parser.add_argument("-t", "--threshold", dest="threshold", type=int, default=100, # threshold to start initial slope
                        help="THRESHOLD", metavar="THRESHOLD")
    parser.add_argument("-d", "--datum_for_threshold", dest="datum_for_threshold", default="total_cases",  # case type for threshold to start initial slope : "new_cases"
                        help="DATUM_FOR_THRESHOLD", metavar="DATUM_FOR_THRESHOLD")
    parser.add_argument("-i", "--idir", dest="idir", default="../Data", # input directory 
                        help="INPUT_DIRECTORY", metavar="INPUT_DIRECTORY")
    parser.add_argument("-j", "--json_file", dest="json_file", default="owid-covid-data.json", # Our World in Data Coronavirus data
                        help="INPUT_JSON_FILE", metavar="INPUT_JSON_FILE")
    parser.add_argument("-o", "--odir", dest="odir", default="../Output", # output directory 
                        help="OUTPUT_DIRECTORY", metavar="OUTPUT_DIRECTORY")
    parser.add_argument("-c", "--cdir", dest="cdir", default="Countries", # directory for UN ISO-3116 code.csv files in the output directory
                        help="COUNTRY_DIRECTORY", metavar="COUNTRY_DIRECTORY")
    parser.add_argument("-n", "--new_cases", dest="new_cases", default="new_cases", # "new_cases_smoothed" is a new alternative.
                        help="NEW_CASES", metavar="NEW_CASES")
    parser.add_argument("-s", "--st_dev_factor", dest="st_dev_factor", type=float, default=1.0, # Multiplies the calculated standdard deviation for Y-error.
                        help="ST_DEV_FACTOR", metavar="ST_DEV_FACTOR")
    return parser
    
if __name__ == "__main__":
    main()
