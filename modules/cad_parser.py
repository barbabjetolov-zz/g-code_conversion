import numpy as np

def read_rsoft_file(file):
    content = file.readlines()
    content = [x.strip( ) for x in content]
    return content

def import_variables(content):
    dict_content = {}
    for c in content:
        if bool(c) != False:
            try:
                dict_content[c.split(' ')[0]] = c.split(' ')[2]
            except IndexError:
                break
    return dict_content

def find_user_taper(content):
    taper = []
    for n,s in enumerate(content):
        if s=='end user_taper':
            taper.append(n)

    print('Found %d user_taper section/s'%len(taper))
    return taper

#looks for segment section/s
def find_segment(content):
    segment = []
    for n,s in enumerate(content):
        if s=='end segment':
            segment.append(n)
    print('Found %d segment section/s'%len(segment))
    return segment

def find_expressions(content,taper,list_of_ut):
    temp = {}
    for i in taper:
        k = i
        while k>0:
            k=k-1
            s=content[k].split(' ')[0]
            if s=='expression':
                temp[s] = content[k].split(' ')[2]
                break
        list_of_ut.append(temp)
    return list_of_ut

def find_segment_content(content,segment,list_of_seg):
    temp = {}
    for index in segment:
        k=index-1;
        while content[k].split(' ')[0]!='segment':
            temp[content[k].split(' ')[0]] = content[k].split(' ')[2]
            k=k-1
        list_of_seg.append(temp)
    return list_of_seg

#main parsing function
def cad_parser(file):

    list_of_ut = []
    list_of_seg = []

    content = read_rsoft_file(file)

    dict_variables = import_variables(content)

    print(dict_variables)

    taper = find_user_taper(content)

    segment = find_segment(content)

    list_of_ut = find_expressions(content,taper,list_of_ut)

    list_of_seg = find_segment_content(content,segment,list_of_seg)

    return dict_variables, list_of_ut, list_of_seg
