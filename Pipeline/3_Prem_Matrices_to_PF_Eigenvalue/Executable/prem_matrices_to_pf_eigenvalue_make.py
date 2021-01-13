#!/usr/bin/env python

from os import system

log = f'prem_matrices_to_pf_eigenvalue.log'

C = ' -c ../../1_Prem_Matrices_to_df/Data/UNSDMethodology.csv'
P = ' -p ../../1_Prem_Matrices_to_df/Output/'
E = ' -e [[0],[0,1],[0,1,2],[0,1,2,3],[0,1,2,3,4],[0,1,2,3,4,5],[0,1,2,3,4,5,6],[0,1,2,3,4,5,6,7]]'

system( f'python prem_matrices_to_pf_eigenvalue.py {C} {P} {E} > {log}' )
