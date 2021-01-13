#!/usr/bin/env python
"""
Separates each Prem matrix into its own *.csv file, named by ISO-3166 3-letter country code.
"""

# Import libraries
import argparse
from sys import exit
from os.path import exists, isfile
from os import mkdir
from json import load
import pandas as pd

# Prem matrices
#   https://doi.org/10.1371/journal.pcbi.1005697.s002
ifn1 = "MUestimates_all_locations_1.json"
ifn2 = "MUestimates_all_locations_2.json"

# UN ISO 3166-1 alpha-3 Country Codes
#   https://unstats.un.org/unsd/methodology/m49/overview/UNSD — Methodology.csv
code_fn = "UNSDMethodology.csv"

# The code depends on a dictionary maintaining order according to insertion.

def main(): 
    parser = getArguments()
    argument = parser.parse_args()
    check( argument )  
    
    # Loads UN ISO 3166-1 alpha-3 Country Codes from columns in *.csv file.
    # The UN made errors in columns, so the read needs to specify relevant columns (which are uncorrupted).
    fields = ['Country or Area', 'ISO-alpha3 Code']
    df = pd.read_csv( f'{argument.idir}{code_fn}', skipinitialspace=True, usecols=fields )
    country2code = df.set_index('Country or Area').to_dict()['ISO-alpha3 Code']

    # Loads input json file with Prem_2017 matrices with headings.
    with open( f'{argument.idir}{ifn1}' ) as iFH:
        country2matrix = load( iFH ) # This file contains the strata as headings.
    init=True
    for country,matrix in country2matrix.items():
        if init:
            stratumS = matrix[0].keys()
            stratumL = list(stratumS)
            init=False # Records the stratumS only on the first country.
        assert len(stratumS) == len(matrix) # The matrix must be square.
        stratum2rate = dict()
        for stratum in stratumS:
            stratum2rate[ stratum ] = []
        for row in matrix:
            assert row.keys() == stratumS # The keys for each column must match.
            for stratum,rate in row.items():
                stratum2rate[ stratum ].append(rate)
        df = pd.DataFrame(stratum2rate, index=stratumS)
        code = country2code.get(country)
        if code is None:
            print(country)
            code = country
        df.to_csv(f'{argument.odir}{code}.csv')

    # Loads input json file with Prem_2017 matrices without headings.
    with open( f'{argument.idir}{ifn2}' ) as iFH:
        country2matrix = load( iFH ) # This file contains the strata as headings.
    for country,matrix in country2matrix.items():
        assert len(stratumS) - 1 == len(matrix) # The matrix must be square and without headings.
        stratum2rate = dict()
        for stratum in stratumS:
            stratum2rate[ stratum ] = []
        init=True
        for row in matrix:
            rateS = row.keys()
            assert len(stratumS) == len( rateS )
            j = 0
            for stratum,rate in row.items():
                if init:
                    i = 0
                    for stratum in row.keys():
                        stratum2rate[ stratumL[ i ] ].append(stratum)
                        i += 1
                init=False
                stratum2rate[ stratumL[ j ] ].append(rate)
                j += 1
        df = pd.DataFrame(stratum2rate, index=stratumS)
        code = country2code.get(country)
        if code is None:
            print(country)
            code = country
        df.to_csv(f'{argument.odir}{code}.csv')

# Check and fixes arguments if possible.    
def check( argument ): 
    if not exists( f'{argument.idir}' ):
        print( f'Error: a valid INPUT_DIRECTORY "{argument.idir}" is required.' )
        exit
    if not isfile( f'{argument.idir}{ifn1}' ):
        print( f'Error: a valid INPUT_JSON_PREM_MATRICES "{argument.idir}{ifn1}" is required.' )
        exit
    if not isfile( f'{argument.idir}{ifn2}' ):
        print( f'Error: a valid INPUT_JSON_PREM_MATRICES "{argument.idir}{ifn2}" is required.' )
        exit
    if not isfile( f'{argument.idir}{code_fn}' ):
        print( f'Error: a valid INPUT_CSV_COUNTRY2CODE "{argument.idir}{code_fn}" is required.' )
        exit
    if not exists( f'{argument.odir}' ):
        mkdir( f'{argument.odir}' )
    
def getArguments():
    parser = argparse.ArgumentParser(description='The program outputs prem matrices by country as csv.\n')
    parser.add_argument("-i", "--idir", dest="idir", default="../Data/", # input directory
                        help="INPUT_DIRECTORY", metavar="INPUT_DIRECTORY")
    parser.add_argument("-o", "--odir", dest="odir", default="../Output/", # input directory
                        help="OUTPUT_DIRECTORY", metavar="OUTPUT_DIRECTORY")
    return parser
    
if __name__ == "__main__":
    main()
