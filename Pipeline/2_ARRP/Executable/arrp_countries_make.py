#!/usr/bin/env python

from os import system

from math import sqrt

log = f'arrp_countries.log'

factor = 1.0/sqrt(7.0)

N = ' -n new_cases_smoothed'
S = f' -s {factor}'
T = ' -t 30'
D = ' -d new_cases_smoothed'

system( f'python arrp_countries.py {N} {S} {T} {D} > {log}' )
