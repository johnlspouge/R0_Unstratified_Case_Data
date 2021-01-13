#!/usr/bin/env python
"""
Calculates R0 by country.
"""

# Import libraries
import argparse
from sys import exit
from os.path import exists, isfile
from os import mkdir, listdir, remove
import pandas as pd

import numpy as np
from scipy.linalg import eig
from json import loads, dumps

def main(): 
    parser = getArguments()
    argument = parser.parse_args()
    check( argument )  

    # Loads UN ISO 3166-1 alpha-3 Country Codes from columns in *.csv file.
    # The UN made errors in columns, so the read needs to specify relevant columns (which are uncorrupted).
    fields = ['Country or Area', 'ISO-alpha3 Code']
    df = pd.read_csv( f'{argument.code_fn}', skipinitialspace=True, usecols=fields )
    code2country = df.set_index('ISO-alpha3 Code').to_dict()['Country or Area']
        
    # Processes all the *.csv files in f'{argument.pdir}'.
    values = []
    count = 0
    for ifn in sorted( listdir( f'{argument.pdir}' ) ):
        code = iso_csv_to_code( ifn )
        if code is None:
            print( "Invalid input *.csv name:", ifn )
            continue
        country = code2country.get(code)
        if country is None:
            print( "Invalid 3-letter *.csv name:", ifn )
            country = code
        count += 1
        print( f'-- Reading "{ifn}" started --', flush=True )
        dataframe = pd.read_csv( f'{argument.pdir}{ifn}' )
        first_column = dataframe.columns[0]
        # Delete first
        dataframe = dataframe.drop([first_column], axis=1)
        # Calculates for the full Prem matrix.
        vector = [ code, country ]
        matrix0 = dataframe.to_numpy()
        assertPremMatrix( matrix0 )
        # Iterates through exclude.
        matrix = matrix0.copy()
        excludes = loads( argument.excludes )
        while True:
            eigval, eigvec = perron_frobenius_eig( matrix )
            vector.append( eigval )
            if not excludes:
                break
            exclude = excludes.pop(0) # row&col numbers to delete
            matrix = np.delete( np.delete( matrix0, exclude, 0 ), exclude, 1 )
            assert is_square( matrix )
            assert is_nonnegative( matrix )
        values.append( vector )
    print( f'-- Processed {count} Prem matrices --', flush=True )
    cols = ['ISO-alpha3 Code', 'country', 'pf_eigenvalue']
    excludes = loads( argument.excludes )
    for exclude in excludes:
        cols.append( 'pf_eigenvalue ' + dumps( exclude ) )
    df = pd.DataFrame( values, columns = cols ) 
    #df.set_index('ISO-alpha3 Code')
    #df['ISO-alpha3 Code']=df.index
    ofn = f'{argument.odir}pf_eigenvalue.csv'
    if isfile( ofn ):
        remove( ofn )
    df.to_csv( ofn, index=False )

# Halts execution if df is not a Prem matrix.    
def assertPremMatrix( matrix ): 
    SIXTEEN = 16
    assert matrix.shape == (SIXTEEN, SIXTEEN) 
    assert is_nonnegative( matrix ) 

# Returns upper-case 3-letter code for filename [code].csv or None.    
def iso_csv_to_code( ifn ): 
    if not ifn.endswith(".csv"):
        return None
    code = ifn.split( '.' )[0]
    if not len(code) == 3:    
        return None
    if not code.isupper():    
        return None
    return code

# Returns True if matrix is 2D square.
def is_square( np_array ):
    if np_array.ndim != 2:
        return False
    (m, n) = np_array.shape
    return m == n

# Returns True if all elements are nonnegative.
def is_nonnegative( np_array ):
    for x in np.nditer(np_array):
        if x < 0.0:
            return False
    return True

# Calculates Perron-Frobenius eigenvalue and eigenvector.
def perron_frobenius_eig( np_array ):
    if not is_square( np_array ):
        raise ValueError('np_array is not a square two-dimensional matrix.')
    if not is_nonnegative( np_array ):
        raise ValueError('np_array contains negative elements.')
    vals, vecs = eig(np_array)
    maxcol = list(vals).index(max(vals))
    perron_frobenius_eigval = vals[maxcol]
    perron_frobenius_eigvec = vecs[:,maxcol]
    if any([ coord < 0.0 for coord in perron_frobenius_eigvec ]):
        perron_frobenius_eigvec = -perron_frobenius_eigvec
    return perron_frobenius_eigval.real, perron_frobenius_eigvec.real

# Checks and fixes arguments if possible.    
def check( argument ): 
    if not exists( f'{argument.odir}' ):
        mkdir( f'{argument.odir}' )
    if not exists( f'{argument.pdir}' ):
        print( f'Error: a valid PREM_MATRICES_DIRECTORY "{argument.pdir}" is required.' )
        exit
    if not f'{argument.pdir}'.endswith('/'):
        argument.pdir += '/'        
    
def getArguments():
    parser = argparse.ArgumentParser(description='The program outputs Perron-Frobenius eigenvalue for prem matrices by country as csv.\n')
    parser.add_argument("-o", "--odir", dest="odir", default="../Output/", # input directory
                        help="OUTPUT_DIRECTORY", metavar="OUTPUT_DIRECTORY")
    parser.add_argument("-c", "--code_fn", dest="code_fn", default="../Data/UNSDMethodology.csv", # *.csv code to country
                        help="CODE_FN", metavar="CODE_FN")
    parser.add_argument("-p", "--prem_matrices_directory", dest="pdir", # [3-letter code].csv contains Prem matrix.
                        help="PREM_MATRICES_DIRECTORY", metavar="PREM_MATRICES_DIRECTORY")
    parser.add_argument("-e", "--exclude_from_prem_matrices", dest="excludes", default="[]", # rows&cols to delete from Prem matrix eigenvalue calculation.
                        help="EXCLUDE_FROM_PREM_MATRICES", metavar="EXCLUDE_FROM_PREM_MATRICES")
    return parser
    
if __name__ == "__main__":
    main()
