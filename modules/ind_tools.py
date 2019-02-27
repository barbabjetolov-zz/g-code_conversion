import numpy as np
import sys

'''
Checks for verbosity
'''
for n,i in enumerate(sys.argv):
    if i == '-nv' or i == '--non-verbose':
        VERBOSE = 0
    else:
        VERBOSE = 1

def read_rsoft_file(file):
    content = file.readlines()
    content = [x.strip( ) for x in content]
    return content

def import_variables(content):
    dict_content = {}
    for c in content:
        if bool(c) != False:
            try:
                dict_content[c.split(' ')[0]] = c.split(' ')[2].replace('^','**')
            except IndexError:
                break
    return dict_content

def find_user_taper(content):
    taper = []
    for n,s in enumerate(content):
        if s.split(' ')[0]=='user_taper':
            taper.append(n)
    if VERBOSE == 1:
        print('Found %d user_taper section/s'%len(taper))
    return taper

#looks for segment section/s
def find_segment(content):
    segment = []
    for n,s in enumerate(content):
        if s.split(' ')[0]=='segment':
            segment.append(n)
    if VERBOSE == 1:
        print('Found %d segment section/s'%len(segment))
    return segment

def find_expressions(content,taper,list_of_ut):
    temp = {}
    for i in taper:
        temp['number'] = content[i].split(' ')[1]
        k = i
        while k>0:
            k=k+1
            s=content[k].split(' ')[0]
            if s=='expression':
                #substitutes all the syntax python doesn't understand
                temp[s] = content[k].split(' ')[2].replace('^','**')
                break
        list_of_ut.append(temp)
    return list_of_ut

def find_segment_content(content,segment,list_of_seg):
    for index in segment:
        temp = {}
        k=index
        temp['number'] = content[k].split(' ')[1]
        k=index+1
        while content[k] != 'end segment':
            temp[content[k].split(' ')[0]] = content[k].split('=')[1]
            k=k+1
        list_of_seg.append(temp)
    return list_of_seg

def extremes_reformat(list_of_seg):
    return list_of_seg

#main parsing function
def cad_parser(file):

    list_of_ut = []
    list_of_seg = []

    content = read_rsoft_file(file)

    dict_variables = import_variables(content)

    taper = find_user_taper(content)

    segment = find_segment(content)

    list_of_ut = find_expressions(content,taper,list_of_ut)

    list_of_seg = find_segment_content(content,segment,list_of_seg)

    return dict_variables, list_of_ut, list_of_seg

'''
Function sorting list of dictionaries by parameter string
'''
def sel_sorting(list_of_seg,str):
    for n,segment in enumerate(list_of_seg):
        if n==0:
            continue
        key = segment
        j = n-1
        curr = list_of_seg[j][str]
        while j >= 0 and float(key[str]) < float(list_of_seg[j][str]):
                list_of_seg[j+1] = list_of_seg[j]
                j -= 1
        list_of_seg[j+1] = key

'''
Function reconstructing waveguides
This function reorders the list of dictionaries such that contiguous sections are adiacent
'''
def wg_reconstruction(list_of_seg):
    begins = []
    #saves the first segment of every waveguide
    for segment in list_of_seg:
        if float(segment['begin.z']) == 0:
            begins.append(segment)
    print('\nFound %d waveguide/s\n'%len(begins))
    #sorts the beginning segments by y
    sel_sorting(begins,'begin.y')

    return begins

'''
Function that converts the units in the segment to the uno used by the machine
'''
def unit_conversion(list_of_seg,conv_factor):
    for segment in list_of_seg:
        for key in segment:
            #converts all the numbers in the segment, except its number and user_taper's
            if key != 'number' and key != 'position_taper':
                try:
                    segment[key] = float(segment[key])*conv_factor
                except ValueError:
                    pass
