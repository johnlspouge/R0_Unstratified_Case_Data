#!/usr/bin/env python

from os import system

log = f'r0_arrp.log'

C = ' -c ../../1_Prem_Matrices_to_df/Data/UNSDMethodology.csv'
E = ' -e ../../3_Prem_Matrices_to_PF_Eigenvalue/Output/pf_eigenvalue.csv'
S = ' -s ../../2_ARRP/Output/slope.csv'

system( f'r0_arrp.py {C} {E} {S} > {log}' )
