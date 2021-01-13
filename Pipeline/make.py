#!/usr/bin/env python

from os import system, chdir

log = f'make.log'

directory2make = {'1_Prem_Matrices_to_df/':'prem_matrices_to_df_make.py',
                  '2_ARRP/':'arrp_countries_make.py',
                  '3_Prem_Matrices_to_PF_Eigenvalue/':'prem_matrices_to_pf_eigenvalue_make.py',
                  '4_R0_ARRP/':'r0_arrp_make.py'}

with open( log, "w" ) as lfh:
    for ( directory, make ) in directory2make.items():
        print( directory, file=lfh )
        chdir( f'{directory}Executable/' )
        system( f'python {directory2make[directory]}' )
        chdir( '../../' )
