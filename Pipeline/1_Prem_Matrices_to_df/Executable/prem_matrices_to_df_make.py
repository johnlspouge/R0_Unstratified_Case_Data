#!/usr/bin/env python

from os import system

log = f'prem_matrices_to_df.log'

system( f'python prem_matrices_to_df.py > {log}' )

# Not all Prem countries correspond to ISO-3166 3-letter country names.
# Occasional differences require ad hoc correction.
system( f'python prem_matrices_to_df_country2code.py >> {log}' ) 
