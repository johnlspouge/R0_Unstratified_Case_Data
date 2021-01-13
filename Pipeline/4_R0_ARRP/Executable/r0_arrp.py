#!/usr/bin/env python
"""
Regresses R0 from r against rho(Prem matrix) by country.
"""

# Imports libraries.
import argparse
from sys import exit
from os.path import exists, isfile
from os import mkdir, remove

import pandas as pd
from json import load

def main(): 
    parser = getArguments()
    argument = parser.parse_args()
    check( argument )  

    # Reads parameters for the gamma distribution of generation time.
    with open( f'{argument.idir}{argument.generation_time}' ) as iFH:
        gammas = load( iFH )
    #print(gammas)
    gamma = gammas[0]
    gamma[ "mu" ] = gamma[ "mean" ]
    gamma[ "kappa" ] = (gamma[ "standard_deviation" ]/ gamma[ "mean" ]) ** 2
    
    # Loads UN ISO 3166-1 alpha-3 Country Codes from columns in *.csv file.
    # The UN made errors in columns, so the read needs to specify relevant columns (which are uncorrupted).
    fields = ['Region Name', 'Sub-region Name', 'ISO-alpha3 Code']
    df_code = pd.read_csv( f'{argument.code_fn}', skipinitialspace=True, usecols=fields )
    code2info = df_to_key2dictionary( df_code, 'ISO-alpha3 Code' )
            
    # Loads Prem matrix PF eigenvalues from columns in *.csv file.
    df_eigenvalue = pd.read_csv( f'{argument.eigenvalue_fn}', skipinitialspace=True )
    code2eigenvalue = df_to_key2dictionary( df_eigenvalue, 'ISO-alpha3 Code' )
            
    # Loads slopes and related information from columns in *.csv file.
    df_slope = pd.read_csv( f'{argument.slope_fn}', skipinitialspace=True )
    code2slope = df_to_key2dictionary( df_slope, 'code' )
    
    codes = [ c for c in code2slope if c in code2eigenvalue and c in code2info ]
    
    print( f'-- combining country values started --', flush=True )
    code2r0 = {}
    for c in codes:
        code2r0[c] = { **code2info[c], **code2slope[c], **code2eigenvalue[c] }
    
    # Calculates R0 and R0_error.
    for (key,value) in code2r0.items():
        print( f'-- Processing "{key}" started --', flush=True )
        # Adds the r0 and r0_error calculated from r.
        r = value[ "slope" ]
        delta_r = value[ "error" ]
        code2r0[ key ][ "r0" ] = float( r0( gamma, r ) )
        code2r0[ key ][ "r0_error" ] = float( r0_error( gamma, r, delta_r ) )
        #print( code2r0[ key ], flush=True )

    # Writes dataframe to code2r0.csv.
    #cols=['code', 'country', 'slope', 'slope_error', 'r0', 'r0_error', 'pf_eigenvalue'...& other deleted matrices ]
    df = pd.DataFrame.from_dict( code2r0, orient='index' )
    cols = df.columns.tolist()
    # Moves the column names 'pf_eigenvalue*' to the end.
    pfs = [x for x in cols if x.startswith('pf_eigenvalue')] 
    cols = [x for x in cols if not x.startswith('pf_eigenvalue')]
    cols.extend( pfs )
    df = df[ cols ]
    
    df.index.name='code'
    ofn = f'{argument.odir}code2r0.csv'
    if isfile( ofn ):
        remove( ofn )
    df.to_csv( ofn )
              
# Returns R0 for given gamma distribution and Malthusian parameter r.    
def df_to_key2dictionary( df, key ): 
    dictionaries = df.to_dict( 'records' )
    key2dictionary = dict()
    for d in dictionaries:
        code = d[ key ]
        del d[ key ]
        key2dictionary[ code ] = d
    return key2dictionary

# Returns R0 for given gamma distribution and Malthusian parameter r.    
def r0( gamma, r ): 
    return pow( 1.0 + r * gamma["mu"] * gamma["kappa"], 1.0/gamma["kappa"] ) 

# Returns absolute error in R0 for given gamma distribution and Malthusian parameter r.    
def r0_error( gamma, r, delta_r ): 
    return delta_r * gamma["mu"] * pow( 1.0 + r * gamma["mu"] * gamma["kappa"], 1.0/gamma["kappa"] - 1.0 ) 

# Checks and fixes arguments if possible.    
def check( argument ): 
    if not exists( f'{argument.idir}' ):
        print( f'Error: a valid INPUT_DIRECTORY "{argument.idir}" is required.' )
        exit
    if not exists( f'{argument.odir}' ):
        mkdir( f'{argument.odir}' )
    if not isfile( f'{argument.idir}{argument.generation_time}' ):
        print( f'Error: a valid GENERATION_TIME "{argument.idir}{argument.generation_time}" is required.' )
        exit
    if not isfile( f'{argument.code_fn}' ):
        print( f'Error: a valid CODE_FN "{argument.code_fn}" is required.' )
        exit
    if not isfile( f'{argument.eigenvalue_fn}' ):
        print( f'Error: a valid EIGENVALUE_FN "{argument.eigenvalue_fn}" is required.' )
        exit
    if not isfile( f'{argument.slope_fn}' ):
        print( f'Error: a valid SLOPE_FN "{argument.slope_fn}" is required.' )
        exit
    
def getArguments():
    parser = argparse.ArgumentParser(description='The program outputs Perron-Frobenius eigenvalue for prem matrices by country as csv.\n')
    parser.add_argument("-i", "--idir", dest="idir", default="../Data/", 
                        help="INPUT_DIRECTORY", metavar="INPUT_DIRECTORY")
    parser.add_argument("-o", "--odir", dest="odir", default="../Output/", 
                        help="OUTPUT_DIRECTORY", metavar="OUTPUT_DIRECTORY")
    parser.add_argument("-g", "--generation_time", dest="generation_time", default="generation_time.json", # generation_time gamma parameters The 0-th element is used.
                        help="GENERATION_TIME", metavar="GENERATION_TIME")
    parser.add_argument("-c", "--code_fn", dest="code_fn", # *.csv with code to country
                        help="CODE_FN", metavar="CODE_FN")
    parser.add_argument("-e", "--eigenvalue_fn", dest="eigenvalue_fn",  
                        help="EIGENVALUE_FN", metavar="EIGENVALUE_FN")
    parser.add_argument("-s", "--slope_fn", dest="slope_fn", 
                        help="SLOPE_FN", metavar="SLOPE_FN")
    return parser
    
if __name__ == "__main__":
    main()
