#!/usr/bin/env python
"""
Renames each Prem matrix by ISO-3166 3-letter country code.
"""

# Import libraries
import argparse
from sys import exit
from os import chdir, rename
from os.path import exists

def main(): 
    parser = getArguments()
    argument = parser.parse_args()
    check( argument )  
    
    # Renames Prem_2017 matrices *.csv files  by ISO-3166 3-letter country code where necessary.
    fn2code_fn = {
        'Bolivia (Plurinational State of':'BOL',
        'Czech Republic':'CZE',
        'Hong Kong SAR, China':'HKG',
        'Lao People\'s Democratic Republi':'LAO',
        'Sao Tome and Principe ':'STP',
        'Taiwan':'TWN',
        'TFYR of Macedonia':'MKD',
        'United Kingdom of Great Britain':'GBR',
        'Venezuela (Bolivarian Republic ':'VEN',
        'MO':'MAC',
    }
    
    chdir( f'{argument.odir}')
    for (key, value) in fn2code_fn.items():
        rename( f'{key}.csv', f'{value}.csv' )

# Check and fixes arguments if possible.    
def check( argument ): 
    if not exists( f'{argument.odir}' ):
        print( f'Error: a valid OUTPUT_DIRECTORY "{argument.odir}" is required.' )
        exit
    
def getArguments():
    parser = argparse.ArgumentParser(description='The program corrects occasional country codes for Prem matrices csv.\n')
    parser.add_argument("-o", "--odir", dest="odir", default="../Output/", # input directory
                        help="OUTPUT_DIRECTORY", metavar="OUTPUT_DIRECTORY")
    return parser
    
if __name__ == "__main__":
    main()
