# author   : Johann-Mattis List
# email    : mattis.list@uni-marburg.de
# created  : 2014-05-19 08:10
# modified : 2014-05-19 08:10
"""
Merge two wordlists into a meta-list.
"""

__author__="Johann-Mattis List"
__date__="2014-05-19"

from lingpy import *
import re
import html.parser
from urllib.request import urlopen

h = html.parser.HTMLParser()

listA = csv2list('../conceptlists/huber1992.tsv')
listB = csv2list('../concepticon.tsv')


# make dictionary from lists
dictB = {}
for line in listB[1:]:
    try:
        dictB[line[0]] += [line[1:]]
    except:
        dictB[line[0]] = [line[1:]]

# make dictionary from lists
dictA = {}
for line in listA[1:]:
    try:
        dictA[line[-1]] += [line[:-1]]
    except:
        dictA[line[-1]] = [line[:-1]]

new_keys = [k for k in dictA if k not in dictB]


def crawlOW(key):
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

    return definition


comment = """# CONCEPTICON
# Created by: QLC Research Group
# Created on: {0}
"""
with open('concepticon_update.tsv', 'w') as f:
    f.write(comment.format(rc('timestamp')))
    f.write('\t'.join(listB[0])+'\n')
    for line in listB[1:]:
        f.write('\t'.join(line)+'\n')
    for k in new_keys:
        definition = crawlOW(k)
        if len(dictA[k]) == 1:
            line = dictA[k][0]
            f.write('\t'.join(
                [
                    k,
                    '-',
                    line[2],
                    '-',
                    definition,
                    '-',
                    '-',
                    ])+'\n')
            print('ADDED',line[2])
        else:
            pass
            #print(k,[l[2] for l in dictA[k]])

        
import os
os.system('mv concepticon_update.tsv ../../concepticon.github.io/datapackage/concepticon.tsv')
