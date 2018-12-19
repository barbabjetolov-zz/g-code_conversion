def init_parse(init):
    dicinit = {}
    init = open('%s'%init,'r')
    lines = init.readlines()
    lines = [x.strip( ) for x in lines]
    for line in lines:
        if line.startswith('#'):
            pass
        else:
            try:
                dicinit[line.split(' ')[0]] = line.split(' ')[2]
            except IndexError:
                break
    init.close()
    return dicinit
