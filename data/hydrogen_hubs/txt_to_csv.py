#!/usr/bin/env python3

"""
Created on Wed Jun 28 10:24:00 2023
@author: danikam

Purpose: Quick script to convert electrolyzer data copied from https://www.hydrogen.energy.gov/pdfs/23003-electrolyzer-installations-united-states.pdf into a csv file
"""

import re

f_txt = open('electrolyzers.txt', 'r')
f_csv = open('electrolyzers_prelim.csv', 'w')

f_csv.write('Location,Power (kW),Status\n')

for line in f_txt:
    # Remove commas
    line = line.replace(',', '')
    
    # Split the line into string and numerical parts
    separated_line = re.split('(\d+)', line)
    
    # Remove leading and trailing spaces
    for i in range(len(separated_line)):
        separated_line[i] = separated_line[i].strip()
    
    # Construct the equivalent csv line and add it to the csv file
    line_csv = ''
    for i in range(len(separated_line)):
        if i < len(separated_line) - 1: line_csv = line_csv + separated_line[i] + ', '
        else: line_csv += separated_line[i]
        
    f_csv.write(line_csv + '\n')
        
