# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2014-05-06 13:03
# modified : 2014-05-06 13:03
"""
Parse the concepticon and convert it to different outputs.
"""

__author__="Johann-Mattis List"
__date__="2014-05-06"

from lingpy import *
import re
import html.parser

h = html.parser.HTMLParser() #.unescape('Suzy &amp; John')
# 'Suzy & John'

#html.parser.HTMLParser().unescape('&quot;')
# '"'

data = csv2list('Concepticon - WOLD.tsv')

head2line = dict(
        zip(
            [k.lower() for k in data[0]],
            range(len(data[0]))
            )
        )

output = {}
errors = open('errors.tsv', 'w')
bads = 0
good_lines = []
for line in data:

    link = line[7]
    idx = link.split('(')[-1][:-1]
    
    if ' ' in idx:
        idx = idx.split(' ')[0]
        print(idx)


    if ')' in idx:
        print(idx)
        idx = idx.replace(')','')

    try:
        idx = int(idx)
        # append stuff to important lines
        appends = []
        appends += [str(idx)] # omega-wiki link
        
        if line[11].strip():
            print(line[0],line[7])
            alts = [p.strip().split('(')[-1][:-1] for p in line[11].strip().split(',')]
            alts = ';'.join([a for a in alts if a.isdigit()])
            if alts:
                appends += [alts]
            else:
                appends += ['-']
        else:
            appends += ['-']

        appends += [line[2].upper()] # english raw gloss
        appends += [line[5]] # part of speech


        appends += [line[3] if not line[3].startswith('0') else '-'] # wold key
        appends += [line[6]]

        if '.999' in line[3]:
            print('! ABORTING this one!', line[3])
            raise


        good_lines += [appends]
    except:
        bads += 1
        errors.write('\t'.join(line)+'\n')
print(bads)
errors.close()

outf = open('../concepticon.tsv','w')
comment = """# CONCEPTICON
# Created by: QLC Research Group
# Created on: {0}

"""
doublets = open('doublets.tsv','w')
visited = {}
outf.write(comment.format(rc('timestamp')))
outf.write('OMEGAWIKI\tSEEALSO\tGLOSS\tSEMANTICFIELD\tDEFINITION\tPOS\tWOLD\n')
sorter = []
for line in sorted(good_lines, key=lambda x:x[2]):
    if line[0] not in visited:
        visited[line[0]] = [line[1:]]
        #outf.write('\t'.join(line)+'\n')
        sorter += [line[0]]
    else:
        visited[line[0]] += [line[1:]]


#outf.close()
d = 0
for key in visited:
    if len(visited[key]) > 1:
        d += 1
        for line in visited[key]:
            doublets.write(key+'\t'+'\t'.join(line)+'\n')
        doublets.write('#\n')
doublets.close()


def isfloat(var):
    try:
        float(var)
        return True
    except:
        return False

from urllib.request import urlopen

from pickle import load,dump
try:
    defs = load(open('defs.bin','rb'))
except:
    defs = {}

for i,key in enumerate(sorter):

    
    try:
        definition = defs[key]
    except:

        # get the definition first
        response = urlopen(
                'http://www.omegawiki.org/api.php?format=xml&action=ow_define&dm={0}'.format(
                    key
                    )
                )
        xml = response.read()
        xml = str(xml, 'utf-8')

        # extract defition 
        definition = re.findall('lang="(.*?)" text="(.*?)"', xml)
        
        if definition:
            lang = definition[0][0]
            definition = definition[0][1].replace('\t',' ').replace('\r\n', ' ').replace('\n',' ')
            if lang != 'English':
                definition = '-'
                
        else:
            definition = '-'

        definition = h.unescape(definition);
        definition = ''.join([k for k in definition if k not in '\t\r\n'])

        print(i,'\t',definition)
        defs[key] = definition

    print(key)
    # get the 
    if len(visited[key]) == 1:
        outf.write(key+'\t'+visited[key][0][0]+'\t'+visited[key][0][1]+'\t'+visited[key][0][-1]+'\t'+definition+'\t'+'\t'.join(visited[key][0][2:-1])+'\n')
    else:
        # get multiple glosses and wold keys
        wolds = []
        glosses = []
        for line in visited[key]:
            wolds += [line[-2]]
            glosses += [line[1]]

        wolds = [w for w in sorted(set(wolds)) if isfloat(w)]
        if not wolds:
            wolds = ['-']
        glosses = [g for g in sorted(set(glosses)) if g != visited[key][0][1]
                and g.strip() and g.strip() != '-']
        if glosses:
            pass
        else:
            glosses = ['-']

        outstr = key+'\t'+visited[key][0][0]+'\t'+visited[key][0][1]+','+', '.join(glosses)+'\t'+visited[key][0][-1]+'\t'+definition+'\t'+visited[key][0][2]+'\t'+';'.join(wolds)+'\n'
        outstr = outstr.replace(',-\t','\t')
        outf.write(outstr)
outf.close()

import os
os.system('cp ../concepticon.tsv ../../concepticon.github.io/datapackage/concepticon.tsv')

with open('defs.bin', 'wb') as f:
    dump(defs,f)


wold = csv2list('../concepticon.tsv')

with open('../concept_lists/wold.tsv','w') as f:
    f.write('OMEGAWIKI\tWOLD\tGLOSS\tSEMANTICFIELD\tDEFINITION\tPOS\n')
    for line in wold:
        if len(line) < 7:
            print(line)
        else:
            if line[-1].replace('-','').strip():
                f.write('\t'.join(
                    [
                    line[0],
                    line[6],
                    line[2],
                    line[3],
                    line[4],
                    line[5]]
                    )+'\n')

os.system('cp ../concept_lists/wold.tsv ../../concepticon.github.io/datapackage/concept_lists/')
