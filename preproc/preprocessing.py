# --- regularise text
import re
import csv
import os
from datetime import datetime

# --- set up spaCy
import spacy
parser = spacy.load('en')

# ------------------------------------------------------------------ PART 1

# --- input files
in_dir = './00_input/'

# --- output files
out_dir = './01_preprocessed/'
for f in os.listdir(out_dir):
    os.remove(os.path.abspath(os.path.join(out_dir, f)))

# --- dictionaries
dic1 = dict(csv.reader(open('./lexicon/abbrev.txt')))
dic2 = dict(csv.reader(open('./lexicon/mwe.txt')))

for file in os.listdir(in_dir):
    # --- read document
    f = open(in_dir + file, 'r')
    doc = f.read()
    f.close()

    # --- remove XML elements and special characters
    doc = re.sub('.*CDATA\[', '', doc, flags=re.S)
    doc = re.sub('\]\]></TEXT>.*', '', doc, flags=re.S)
    doc = re.sub('<[a-zA-Z]+>', ' ', doc)
    doc = doc.replace('HEEN&T', 'HEENT')
    doc = doc.replace('(Stat Lab)', ' ')
    doc = doc.replace('&nbsp', ' ')
    doc = doc.replace('&#183;', ' . ')
    doc = doc.replace('&#224;', ' . ')
    doc = doc.replace('&#8211;', ' . ')
    doc = doc.replace('&#8217;', '\'')
    doc = doc.replace('&#8220;;', '')
    doc = doc.replace('&#8221;', '')
    doc = doc.replace('&gt;', ' greater than ')
    doc = doc.replace('&lt;', ' less than ')
    doc = doc.replace('>', ' greater than ')
    doc = doc.replace('<', ' less than ')
        
    # --- gender
    doc = doc.replace('gentleman', 'male')
    doc = doc.replace('lady', 'female')
    
    # --- titles so that they don't get confused with other acronyms
    doc = doc.replace('M.Sc.', '')
    doc = doc.replace('Ph.D.', '')
    doc = doc.replace('PhD', '')
    doc = doc.replace('Jr.', '')
    doc = doc.replace('JR.', '')
    
    # --- enclytics
    doc = doc.replace('aren\'t', 'are not')
    doc = doc.replace('can\'t', 'cannot')
    doc = doc.replace('couldn\'t', 'could not')
    doc = doc.replace('didn\'t', 'did not')
    doc = doc.replace('doesn\'t', 'does not')
    doc = doc.replace('don\'t', 'do not')
    doc = doc.replace('hadn\'t', 'had not')
    doc = doc.replace('hasn\'t', 'has not')
    doc = doc.replace('haven\'t', 'have not')
    doc = doc.replace('isn\'t', 'is not')
    doc = doc.replace('wasn\'t', 'was not')
    doc = doc.replace('wouldn\'t', 'would not')
    doc = doc.replace('won\'t', 'will not')
    doc = doc.replace('con\'t', 'continue')
    doc = doc.replace('cont\'d', 'continue')
    doc = doc.replace('\'m', ' am')
    doc = doc.replace('\'ll', ' will')
    doc = doc.replace('\'s', '')
    doc = doc.replace('\'ve', '')
    doc = doc.replace('\'d', '')
    doc = doc.replace('\'ed', '')

    # --- special punctuation
    doc = re.sub('\sC\\.', ' C ', doc, flags=re.IGNORECASE) # C. diff --> C diff
    doc = re.sub('\sE\\.', ' E ', doc, flags=re.IGNORECASE) # E. coli --> E coli
    doc = re.sub('[^\w]vit\\.', ' vit ', doc, flags=re.IGNORECASE) # vit. D --> vit D
    doc = doc.replace('x. ', 'x ') # fx. of --> fx of
    doc = re.sub('\sq\\.\s', ' q.', doc, flags=re.IGNORECASE) # q. a.m. --> q.a.m.
    doc = re.sub('([a-z])\\.([a-z])\\.([a-z])\\.', '\\1\\2\\3', doc, flags=re.IGNORECASE) # q.a.m. --> qam
    doc = re.sub('([a-z])\\.([a-z])\\.', '\\1\\2', doc, flags=re.IGNORECASE) # q.d. --> qd
    #doc = re.sub('q\\.(\d)', 'q\\1', doc, flags=re.IGNORECASE) # q.4 --> q4
    doc = re.sub('\sq\\.\s', ' q ', doc, flags=re.IGNORECASE|re.S) # q.\n --> q
    doc = re.sub('\sq\\.', ' q ', doc, flags=re.IGNORECASE) # q. --> q
    doc = re.sub('\sq\s+', ' q ', doc, flags=re.IGNORECASE|re.S) # q\n --> q
    doc = re.sub('\sh\\.\s', ' h ', doc, flags=re.IGNORECASE) # h. --> h
    doc = re.sub('(\\.)([a-z])', '. \\2', doc, flags=re.IGNORECASE) # .blah --> . blah
    doc = doc.replace('.)', '. ') # overzealous numbering
    doc = doc.replace('ELEM.', 'ELEM ') # elemental
    doc = doc.replace('TAB.SR', 'TABLET')
    doc = re.sub('\(\s*S\s*\)', ' ', doc, flags=re.IGNORECASE)

    # --- record date
    doc = re.sub('Record date: (\d\d\d\d)-(\d\d)-(\d\d)', '. This is record date \\1\\2\\3 .', doc)
   
    # --- dates
    doc = re.sub('\s\d\d/\d\d/\d\d\d\d\s', ' ', doc)
    
    # --- force sentence spliting where punctuation is not used properly
    doc = re.sub('\n[0-9]+\\.\s', ' . This is a list item. ', doc) # 1. blah blah
    doc = re.sub('\n[0-9]+\)\s', ' . This is a list item. ', doc)  # 1) blah blah
    doc = re.sub('\n-+', ' . This is a list item. ', doc)          # -- blah blah

    doc = doc.replace('(H)', ' ') # lab: high
    doc = doc.replace('(L)', ' ') # lab: low
    doc = doc.replace('(T)', ' ') # lab: trace
    doc = re.sub('QTY:.{0,30} End:', ' . ', doc)
    doc = re.sub('QTY:.{0,20} Start:', ' . ', doc)
    doc = re.sub('QTY:.{0,10} Refills:\d*', ' . ', doc)
    doc = re.sub('take:', 'take ', doc)
    doc = re.sub('TABLET\s+CR\s+', 'TABLET ', doc)   # controlled release, not creatinine
    doc = re.sub('CAPSULE\s+CR\s+', 'CAPSULE ', doc) # controlled release, not creatinine
    doc = re.sub('creatinine\s*:\s*', 'creatinine ', doc, flags=re.IGNORECASE)
    doc = re.sub('[\s/]PE:', '\nPHYSICAL EXAMINATION:', doc)
    doc = re.sub('\n([^\n]+): ', '\n . \\1: ', doc)
    doc = re.sub('\n+', ' ', doc)
    doc = re.sub('_+', 'NEW RECORD: ', doc)
    doc = re.sub('--+', ' . ', doc)
    doc = re.sub('==+', ' . ', doc)
    doc = re.sub('##+', ' ', doc)
    doc = re.sub('-', ' ', doc)
    doc = re.sub('\\*+', '.', doc)
    doc = re.sub('\\"', '', doc)
    doc = re.sub('\s+', ' ', doc)
    doc = re.sub(': ', ': . ', doc)
    doc = re.sub('~', ' ', doc)
    doc = re.sub('(\d)([a-z])', '\\1 \\2', doc, flags=re.IGNORECASE)
#    doc = re.sub('(\d)\-([a-zA-Z])', '\\1 - \\2', doc)
    doc = re.sub(' yo m ', ' yo male ', doc, flags=re.IGNORECASE)
    doc = re.sub(' yo f ', ' yo female ', doc, flags=re.IGNORECASE)
    doc = re.sub('[xX] ray', 'xray', doc)
#    doc = re.sub('[aA]\-fib', 'afib', doc)
    doc = re.sub('[aA] fib', 'afib', doc)
#    doc = re.sub('[vV]\-fib', 'vfib', doc)
    doc = re.sub('[vV] fib', 'vfib', doc)
    doc = re.sub('(\\. )*\\.', '.', doc)
    doc = re.sub('\s+', ' ', doc)
    doc = doc.replace('CVA tenderness', 'costovertebral angle tenderness')
    doc = re.sub('(nkda)\\.', '\\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(nka)\\.', '\\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(\\. )*\\.', '.', doc)
    doc = re.sub('\ss\/p\s', ' status post ', doc, flags=re.IGNORECASE)
    doc = re.sub('\sb\s6\s', ' b6 ', doc, flags=re.IGNORECASE|re.S)
    doc = re.sub('\sb\s12\s', ' b6 ', doc, flags=re.IGNORECASE|re.S)
    doc = re.sub('\sb6\/b12\s', ' b6 b12 ', doc, flags=re.IGNORECASE|re.S)
    doc = re.sub('\sb12\/b6\s', ' b6 b12 ', doc, flags=re.IGNORECASE|re.S)
    
    # --- parse document
    parsedDoc = parser(doc)

    sents = []
    # the "sents" property returns spans
    # spans have indices into the original string
    # where each index value represents a token
    for span in parsedDoc.sents:
        # go from the start to the end of each span, returning each token in the sentence
        # combine each token using join()
        sent = ''.join(parsedDoc[i].string for i in range(span.start, span.end)).strip()
        sents.append(sent)

    f = open(out_dir + file + '.txt','w')
    for sentence in sents: 
        sentence = re.sub('\\: \\.', ':', sentence)
        if sentence not in ['This is a list item.', '.']:
            parse = parser(sentence)
            tokenized = ' '
            for i, token in enumerate(parse):
                t = token.lower_
                if t in dic1.keys(): t = dic1[t]
                tokenized += t + ' '
            for key in dic2: tokenized = tokenized.replace(' ' + key + ' ',  ' ' + dic2[key] + ' ')
            #tokenized = tokenized.strip(' ')
            if tokenized not in ['']: f.write(tokenized+'\n')
    f.close()

# ------------------------------------------------------------------ PART 2

# --- input files
in_dir = './01_preprocessed/'

# --- output files

family = './02_family/'
for f in os.listdir(family):
    os.remove(os.path.abspath(os.path.join(family, f)))

allergy = './02_allergy/'
for f in os.listdir(allergy):
    os.remove(os.path.abspath(os.path.join(allergy, f)))

negated = './02_negated/'
for f in os.listdir(negated):
    os.remove(os.path.abspath(os.path.join(negated, f)))

main = './02_main/'
for f in os.listdir(main):
    os.remove(os.path.abspath(os.path.join(main, f)))

twomonths = './02_months_two/'
for f in os.listdir(twomonths):
    os.remove(os.path.abspath(os.path.join(twomonths, f)))

threemonths = './02_months_three/'
for f in os.listdir(threemonths):
    os.remove(os.path.abspath(os.path.join(threemonths, f)))

sixmonths = './02_months_six/'
for f in os.listdir(sixmonths):
    os.remove(os.path.abspath(os.path.join(sixmonths, f)))
    
for file in os.listdir(in_dir):
    # --- read document
    f = open(in_dir + file, 'r')
    doc = f.read()
    f.close()
    
    # --- vitamin D
    doc = re.sub('vitamind', 'DDDD', doc)
    doc = re.sub('vitamin d[^a-zA-Z]', 'DDDD ', doc)
    doc = re.sub('\sd\svitamin', ' DDDD', doc)
    doc = re.sub('vitd\s', 'DDDD ', doc)
    doc = re.sub('vit d[^a-zA-Z]', 'DDDD ', doc)
    doc = re.sub('\w*calciferol', 'DDDD', doc)
    doc = re.sub('calcitri?ol', 'DDDD', doc)
    doc = re.sub('calcitol', 'DDDD', doc)

    # --- remove information about family members
    f = open(family + file,'w')

    f.write('FAMILY HISTORY\n\n')
    for item in re.findall('family history [^\n]*:\n[^\n\\.]+', doc): f.write("%s\n" % item.replace('\n', ' '))
    doc = re.sub('family history :\n[^\n\\.]+', 'XXX ', doc, flags=re.S)
    for item in re.findall('family history \w[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('family history \w[^\n\\.]+', 'XXX ', doc)
    
    f.write('\n\nFAMILY MEMBER\n\n')
    for item in re.findall('[^\n\\.:;]+family member[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]+family member[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nDIED\n\n')
    for item in re.findall('[^\n\\.:;]+died[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]+died[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;]+death[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]+death[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;]+passed away[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]+passed away[^\n\\.]+', 'XXX ', doc)

    f.close()

    # --- remove allergy information
    f = open(allergy + file,'w')

    doc = re.sub('(no known drug allergies)', '\\1 .\n', doc)
    doc = re.sub('(no known allergies)', '\\1 .\n', doc)
    doc = re.sub(' all :', ' allergies :', doc)
    doc = re.sub('( allerg[^\n]+:)', ' allergies :', doc)
    doc = re.sub('\n *allergies *\n', ' allergies : ', doc, flags=re.S)
    doc = re.sub(' allergies ?\/ \n', ' allergies : ', doc, flags=re.S)
    doc = re.sub('(allergies : )\n', '\\1', doc, flags=re.S)
    doc = re.sub('(adverse reactions? : )\n', '\\1', doc, flags=re.S)
    for item in re.findall(' allerg[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub(' allerg[^\n\\.]+', ' XXX ', doc)
    for item in re.findall('adverse reaction[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub(' adverse reaction[^\n\\.]+', ' XXX ', doc)
    
    f.close()

    # --- speaks English?
    dic = dict(csv.reader(open('./lexicon/language.txt')))
    for key in dic:
        doc = re.sub('('+key+'.{0,10} speak)', 'NOENGL \\1', doc)
        doc = re.sub('(speak.{0,20} '+key+')', 'NOENGL \\1', doc)

    doc = re.sub('(not) (speak.{0,20} english)', 'NOENGL njet \\2', doc)
    doc = re.sub('(english.{0,10}) (not)', 'NOENGL \\1 njet', doc)
    doc = re.sub('interpreter', 'NOENGL interpreter', doc)
    
    # --- remove negated information
    f = open(negated + file,'w')

    f.write('\n\n: NO\n\n')
    for item in re.findall('[^\n\\.:;,]+:\s*none', doc): f.write("%s\n" % item.replace('\n', ''))
    doc = re.sub('[^\n\\.:;,]+:\s+none', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]+:\s*negative', doc): f.write("%s\n" % item.replace('\n', ''))
    doc = re.sub('[^\n\\.:;,]+:\s+negative', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]+:\s*no [^\n\\.]*', doc): f.write("%s\n" % item.replace('\n', ''))
    doc = re.sub('[^\n\\.:;,]+:\s*no [^\n\\.]*', 'XXX ', doc)

    for item in re.findall('[^\n\\.:;,]+:\s+denies[^\n\\.]+', doc): f.write("%s\n" % item.replace('\n', ''))
    doc = re.sub('[^\n\\.:;,]+:\s+denies[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]+:\s+unremarkable[^\n\\.]+', doc): f.write("%s\n" % item.replace('\n', ''))
    doc = re.sub('[^\n\\.:;,]+:\s+unremarkable[^\n\\.]+', 'XXX ', doc)
    
    f.write('\n\nRULE OUT\n\n')
    for item in re.findall('[^\n\\.:;]*rule[sd]? out[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]*rule[sd]? out[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nRULE SOMETHING OUT\n\n')
    for item in re.findall('[^\n\\.:;]*rule[sd]? \w+ out[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]*rule[sd]? \w+ out[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nDENIES\n\n')
    for item in re.findall('[^\n\\.:;,]*denie[sd]? [^\n\\.]*', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*denie[sd]? [^\n\\.]*', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]*deny.{0,3} [^\n\\.]*', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*deny.{0,3} [^\n\\.]*', 'XXX ', doc)

    f.write('\n\nCANNOT SEE\n\n')
    for item in re.findall('[^\n\\.:;]*cannot see[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]*cannot see[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nUNLIKELY\n\n')
    for item in re.findall('[^\n\\.:;]*unlikely [^\n\\.]*', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]*unlikely [^\n\\.]*', 'XXX ', doc)
    
    f.write('\n\nNEGATIVE FOR\n\n')
    for item in re.findall('[^\n\\.:;]*negative for [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;]*negative for [^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNEITHER\n\n')
    for item in re.findall('[^\n\\.:;,]*neither [^\n\\.,]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*neither [^\n\\.,]+', 'XXX ', doc)

    f.write('\n\nNOR\n\n')
    for item in re.findall('[^\n\\.:;,]* nor [^\n\\.,]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]* nor [^\n\\.,]+', 'XXX ', doc)

    f.write('\n\nNOT APPEAR\n\n')
    for item in re.findall('[^\n\\.:;,]*not appear[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not appear[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT KNOWN TO\n\n')
    for item in re.findall('[^\n\\.:;,]*not known to[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not known to[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT APPRECIATE\n\n')
    for item in re.findall('[^\n\\.:;,]*not appreciate[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not appreciate[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT COMPLAIN\n\n')
    for item in re.findall('[^\n\\.:;,]*not complain[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not complain[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT DEMONSTRATE\n\n')
    for item in re.findall('[^\n\\.:;,]+not demonstrate[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]+not demonstrate[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT EXHIBIT\n\n')
    for item in re.findall('[^\n\\.:;,]*not exhibit[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not exhibit[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT FEEL\n\n')
    for item in re.findall('[^\n\\.:;,]*not feel[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not feel[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]*not felt [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not felt [^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT REVIEWED\n\n')
    for item in re.findall('[^\n\\.:;,]*not reviewed[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not reviewed[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nNOT HAVE\n\n')
    for item in re.findall('[^\n\\.:;,]*not have [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not have [^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]*not had [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('[^\n\\.:;,]*not had [^\n\\.]+', 'XXX ', doc)
    for item in re.findall('[^\n\\.:;,]*never had [^\n\\.]+', doc): f.write("%s\n" % item)

    f.write('\n\nDOES NOT\n\n')
    for item in re.findall('does not [^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('does not [^\n\\.]{0,50}', 'XXX ', doc)
    for item in re.findall('did not see[^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('did not see[^\n\\.]{0,50}', 'XXX ', doc)
    for item in re.findall('did not show[^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('did not show[^\n\\.]{0,50}', 'XXX ', doc)
    for item in re.findall('did not reveal[^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('did not reveal[^\n\\.]{0,50}', 'XXX ', doc)
    for item in re.findall('did not experience[^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('did not experience[^\n\\.]{0,50}', 'XXX ', doc)
    for item in re.findall('did not take[^\n\\.]{0,50}', doc): f.write("%s\n" % item)
    doc = re.sub('did not take[^\n\\.]{0,50}', 'XXX ', doc)

    f.write('\n\nNO\n\n')
    for item in re.findall('\sno [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('\sno [^\n\\.]+', ' XXX ', doc)

    f.write('\n\nWITHOUT\n\n')
    doc = re.sub(' w\/o ', ' without ', doc)
    for item in re.findall('without any[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('without any[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('without evidence[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('without evidence[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('without indication[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('without indication[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('without sign[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('without sign[^\n\\.]+', 'XXX ', doc)
    for item in re.findall('without[^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('without[^\n\\.]+', 'XXX ', doc)

    f.write('\n\nFREE OF\n\n')
    for item in re.findall('free of [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('free of [^\n\\.]+', 'XXX ', doc)
    for item in re.findall('absence of [^\n\\.]+', doc): f.write("%s\n" % item)
    doc = re.sub('absence of [^\n\\.]+', 'XXX ', doc)
    doc = doc.replace(' pain free ', ' XXX ')
    doc = doc.replace(' symptom free ', ' XXX ')
    
    f.close()

    # --- medication prescription MEDRX
    doc = re.sub('\ssub\sq\s', ' subq ', doc, flags=re.S)
    doc = re.sub('\sslow\s+rel\\.\s', ' ', doc, flags=re.S)
    doc = re.sub('\sslow\s+release\s', ' ', doc, flags=re.S)
    doc = re.sub('\scontrolled\s+release\s', ' ', doc, flags=re.S)
    doc = re.sub('\sextended\s+release\s', ' ', doc, flags=re.S)
    doc = re.sub('\simmed\w*\s+release\s', ' ', doc, flags=re.S)
    doc = re.sub('\ssustained\s+release\s', ' ', doc, flags=re.S)
    doc = re.sub('\schewable\s', ' ', doc, flags=re.S)
    
    doc = re.sub('\(.{0,10} on prior note \)', 'MEDRX', doc, flags=re.S)
    doc = re.sub('\spo\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\sac\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stop daily use\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\sdaily use\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\sonc?e a day\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stwice a day\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\sonc?e daily\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stwice daily\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\smg a day\s', ' mg MEDRX ', doc, flags=re.S)
    doc = re.sub('\smg daily\s', ' mg MEDRX ', doc, flags=re.S)
    doc = re.sub('\smg per day\s', ' mg MEDRX ', doc, flags=re.S)
    doc = re.sub('\stablets? a day\s', ' tablet MEDRX ', doc, flags=re.S)
    doc = re.sub('\stablets? daily\s', ' tablet MEDRX ', doc, flags=re.S)
    doc = re.sub('\stablets? per day\s', ' tablet MEDRX ', doc, flags=re.S)
    doc = re.sub('\spills? a day\s', ' pill MEDRX ', doc, flags=re.S)
    doc = re.sub('\spills? daily\s', ' pill MEDRX ', doc, flags=re.S)
    doc = re.sub('\spills? per day\s', ' pill MEDRX ', doc, flags=re.S)
    doc = re.sub('\sq\s?d\w*\s', ' MEDRX ', doc, flags=re.S) # q day
    doc = re.sub('\sq\s?.{0,15}days?\s', ' MEDRX ', doc, flags=re.S) # q monday, # q other day
    doc = re.sub('\sq\s?mon\s', ' MEDRX ', doc, flags=re.S) # q mon
    doc = re.sub('\sq\s?tue\s', ' MEDRX ', doc, flags=re.S) # q tue
    doc = re.sub('\sq\s?wed\s', ' MEDRX ', doc, flags=re.S) # q wed
    doc = re.sub('\sq\s?thu\s', ' MEDRX ', doc, flags=re.S) # q thu
    doc = re.sub('\sq\s?fri\s', ' MEDRX ', doc, flags=re.S) # q fri
    doc = re.sub('\sq\s?sat\s', ' MEDRX ', doc, flags=re.S) # q sat
    doc = re.sub('\sq\s?sun\s', ' MEDRX ', doc, flags=re.S) # q sun
    doc = re.sub('\sq\s?week\s', ' MEDRX ', doc) # q week
    doc = re.sub('\sq\s.{0,15}weeks?\s', ' MEDRX ', doc) # q other week
    doc = re.sub('\sq\s?month\w*\s', ' MEDRX ', doc) # q month
    doc = re.sub('take .{0,25}meals?', ' MEDRX ', doc)
    doc = re.sub('take with food', ' MEDRX ', doc)
    doc = re.sub('units at night', 'units MEDRX ', doc)
    doc = re.sub('units at bedtime', 'units MEDRX ', doc)
    doc = re.sub('units at hs', 'units MEDRX ', doc)
    doc = re.sub('units at a time', 'units MEDRX ', doc)
    doc = re.sub('units at the next dose', 'units MEDRX ', doc)
    doc = re.sub('units in the morning', 'units MEDRX ', doc)
    doc = re.sub('units in the afternoon', 'units MEDRX ', doc)
    doc = re.sub('units in.{0,10} am', 'units MEDRX ', doc)
    doc = re.sub('units in.{0,10} pm', 'units MEDRX ', doc)
    doc = re.sub('units before breakfast', 'units MEDRX ', doc)
    doc = re.sub('units before bedtime', 'units MEDRX ', doc)
    doc = re.sub('units before dinner', 'units MEDRX ', doc)
    doc = re.sub('units before lunch', 'units MEDRX ', doc)
    doc = re.sub('\sqod\s', ' MEDRX ', doc)
    doc = re.sub('\sbid\s', ' MEDRX ', doc)
    doc = re.sub('\stid\s', ' MEDRX ', doc)
    doc = re.sub('\sqid\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?am\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?pm\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?ac\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?hs\s', ' MEDRX ', doc)
    doc = re.sub('\sprn\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+ h\w*\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+ \d+ h\w*\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+ min\w*\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+ \d+ min\w*\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+ \d+\s', ' MEDRX ', doc)
    doc = re.sub('\sq\s?\d+\s', ' MEDRX ', doc)
    doc = re.sub('\(.{0,25}\stake\s.{0,25}\)', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stake\s.{1,10}\stablets?\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stake\s.{1,10}\spills?\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stake\s.{1,5}\scapsules?\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stake\s.{1,5}\scap\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\stake\sas\sdirected\s', ' MEDRX ', doc, flags=re.S)
    doc = re.sub('\sq MEDRX', ' MEDRX', doc)
    doc = re.sub('\d+ tablet MEDRX', 'MEDRX', doc)
    doc = re.sub('\d+ capsule MEDRX', 'MEDRX', doc)
    doc = doc.replace('tablet MEDRX', 'MEDRX')
    doc = doc.replace('capsule MEDRX', 'MEDRX')
    doc = doc.replace('MEDRX daily', 'MEDRX')
    for counter in range(0,10): doc = doc.replace('MEDRX MEDRX', 'MEDRX')
    doc = re.sub('MEDRX.{1,4}MEDRX', 'MEDRX', doc, flags=re.S)
    doc = doc.replace('MEDRX MEDRX', 'MEDRX')
   
    # --- heart medications
    doc = re.sub('\s\w+nitrate', ' nitrate', doc)
    dic = dict(csv.reader(open('./lexicon/hrtmed.txt')))
    for key in dic: doc = doc.replace(' ' + key + ' ',  ' ' + dic[key] + ' ')
    doc = re.sub('\s\w+statin\s', ' statin ', doc)
    doc = re.sub('\sstatins\s', ' statin ', doc)

    doc = re.sub(' ca\s+(citrate) ', ' calcium \\1 ', doc, flags=re.S)
    doc = re.sub(' k\s+(citrate) ', ' potassium \\1 ', doc, flags=re.S)
    doc = re.sub(' mg\s+(citrate) ', ' magnesium \\1 ', doc, flags=re.S)
    doc = re.sub(' ca\s+(carbonate) ', ' calcium \\1 ', doc, flags=re.S)
    doc = re.sub(' k\s+(carbonate) ', ' potassium \\1 ', doc, flags=re.S)
    doc = re.sub(' mg\s+(carbonate) ', ' magnesium \\1 ', doc, flags=re.S)
    doc = re.sub(' ca\s+(acetate) ', ' calcium \\1 ', doc, flags=re.S)
    doc = re.sub(' k\s+(acetate) ', ' potassium \\1 ', doc, flags=re.S)
    doc = re.sub(' mg\s+(acetate) ', ' magnesium \\1 ', doc, flags=re.S)
    doc = re.sub(' elemental\s+ca([^\w])', ' calcium \\1', doc, flags=re.S)
    doc = re.sub(' elem\s+ca([^\w])', ' calcium \\1', doc, flags=re.S)
    doc = re.sub(' (ca)[^\w]+(.{0,10}DDDD) ', ' calcium \\2 ', doc, flags=re.S)
    doc = re.sub(' (DDDD\s.{0,10})\s(ca)[^\w]+', ' \\1 calcium ', doc, flags=re.S)

    doc = re.sub('\w+cobalamin', 'cobalamin', doc)
    dic = dict(csv.reader(open('./lexicon/supplements.txt')))
    for key in dic:
        doc = re.sub('\s('+key+'.{0,50} MED)', ' SPLMNT \\1', doc, flags=re.S)
        doc = re.sub('(MED|medication|take|taking|continue|refill)(.{0,50})\s('+key+')', '\\1\\2 SPLMNT \\3', doc, flags=re.S)
        doc = re.sub('\s('+key+'.{0,20})\s(supplement|replacement)', ' SPLMNT \\1 \\2', doc, flags=re.S)
        doc = re.sub('(supplement.{0,20})\s('+key+')', '\\1 SPLMNT \\2', doc, flags=re.S)
    
    doc = re.sub('(\w*vitamins?)', 'SPLMNT \\1', doc)
    doc = re.sub('(minerals)', 'SPLMNT \\1', doc)
    doc = re.sub('(fe supp)', 'SPLMNT \\1', doc)
    doc = re.sub('(green tea)', 'SPLMNT \\1', doc)
    doc = re.sub('(ginger)', 'SPLMNT \\1', doc)
    doc = re.sub('( nephro )', 'SPLMNT\\1', doc)
    doc = re.sub('(oral supplement)', 'SPLMNT \\1', doc)
    doc = re.sub('(take.{0,20}) (supplement)', '\\1 SPLMNT \\2', doc)
    doc = re.sub('(taking.{0,20}) (supplement)', '\\1 SPLMNT \\2', doc)
    doc = re.sub('(replet)', 'SPLMNT \\1', doc)
    
    for counter in range(0,3): doc = doc.replace('SPLMNT SPLMNT', 'SPLMNT')

    dic = dict(csv.reader(open('./lexicon/deficiency.txt')))
    for key in dic: doc = re.sub('('+key+')', '\\1 DFCNCY', doc)

    # --- heart treatments
    doc = re.sub('(angioplast\w*)', 'HRTTRT \\1', doc)
    doc = re.sub('(defibrillat\w*)', 'HRTTRT \\1', doc)
    doc = re.sub('\s(stent\w*)', ' HRTTRT \\1', doc)
    doc = re.sub('(coronary artery bypass)', 'HRTTRT \\1', doc)
    doc = re.sub('(coronary bypass)', 'HRTTRT \\1', doc)
    doc = re.sub('(cardiac bypass)', 'HRTTRT \\1', doc)
    doc = re.sub('(cardiac surgery)', 'HRTTRT \\1', doc)
    doc = re.sub('(valve surgery)', 'HRTTRT \\1', doc)
    doc = re.sub('(valve replacement)', 'HRTTRT \\1', doc)
    doc = re.sub('(coronary intervention)', 'HRTTRT \\1', doc)
    doc = re.sub('(thromboly\w*)', 'HRTTRT \\1', doc)
    doc = re.sub('(pacemaker)', 'HRTTRT \\1', doc)
    doc = re.sub('\s(pacer)', ' HRTTRT \\1', doc)
    doc = re.sub('(\w*catheteriz\w*)', 'HRTTRT \\1', doc)
    doc = re.sub('(catheter ablation)', 'HRTTRT \\1', doc)
    
    # --- ischemia
    doc = doc.replace('nonischemic', 'XXX')
    doc = doc.replace('non ischemic', 'XXX')
    doc = re.sub('( ischemi.{0,50})(cardio|cardia|coronary|HRT|heart)', ' HRTISC\\1\\2', doc, flags=re.S)
    doc = re.sub('(cardio|cardia|coronary|HRT|heart)(.{0,50})( ischemi)', '\\1\\2 HRTISC\\3', doc, flags=re.S)
    for counter in range(0,4): doc = doc.replace('HRTISC HRTISC', 'HRTISC')
    
    # --- angina
    doc = re.sub('chest (pain|pressure|ache|tight|discomfort|heav)', 'HRTANG chest \\1', doc)
    doc = re.sub('chest wall (pain|pressure|ache|tight|discomfort|heav)', 'HRTANG chest wall \\1', doc)
    doc = doc.replace(' angina', ' HRTANG angina')
    for counter in range(0,3): doc = doc.replace('HRTANG HRTANG', 'HRTANG')

    # --- advanced CAD feature
    doc = doc.replace('HRT', 'HRTCAD HRT')
    doc = re.sub('(coronary) (syndrome|disease|care|lesion|event)', 'HRTCAD \\1 \\2', doc)
    doc = re.sub('(cardiac) (disease|hospital|rehabilitation|event)', 'HRTCAD \\1 \\2', doc)
    doc = re.sub('(given|extensive)(.{0,20} cardiac history)', '\\1 \\2 HRTCAD', doc)
    doc = re.sub('(cardiomyopathy|cardiac myopathy|heart failure|myocardial infarction)', '\\1 HRTCAD', doc)
    
    # --- high creatinine?
    doc = re.sub('(elevated[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} elevated)', 'HIGHCRT \\1', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} increased?)', 'HIGHCRT \\1', doc)
    doc = re.sub('(increas[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} remarkable)', 'HIGHCRT \\1', doc)
    doc = re.sub('( remarkable[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} notable)', 'HIGHCRT \\1', doc)
    doc = re.sub('(notable[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} above)', 'HIGHCRT \\1', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} over)', 'HIGHCRT \\1', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} greater)', 'HIGHCRT \\1', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} ris\w+)', 'HIGHCRT \\1', doc)
    doc = re.sub('( ris[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} bump\w*)', 'HIGHCRT \\1', doc)
    doc = re.sub('(bump[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine[\w\s]{0,20} high)', 'HIGHCRT \\1', doc)
    doc = re.sub('(high[\w\s]{0,20}) (creatinine)', '\\1 HIGHCRT \\2', doc)
    doc = re.sub('(creatinine is up)', 'HIGHCRT \\1', doc)
    doc = re.sub('(creatinine was up)', 'HIGHCRT \\1', doc)
    doc = re.sub('creatinine \d{1,2}\/\d{1,2}\/\d{2,4}\s+', 'creatinine XXX ', doc, flags=re.S)
    doc = re.sub('(creatinine.{0,10}) :', '\\1 ', doc, flags=re.S)
    doc = re.sub('creatinine\s?=\s?', 'creatinine ', doc)
    doc = re.sub('creatinine\s\\.\s+(\d\\.\d\s\\.)', 'creatinine \\1', doc)
    doc = re.sub('(creatinine)(\s?\(\s?)(\d\\.\d)(\d?\s?\)\s)', '\\1 \\3 ', doc)
    doc = re.sub('\s*/\s*creatinine\s+\d+\s*/\s*', ' creatinine ', doc, flags=re.S) # bun/cre b/c --> bun cre c
    for item in set(re.findall('creatinine[\w\s\d]{0,15} \d\\.\d', doc)):
        if (float(item[-3:]) > 1.5): doc = doc.replace(item, ' HIGHCRT ' + item)
    doc = re.sub(' +', ' ', doc)
    for counter in range(0,3): doc = doc.replace('HIGHCRT HIGHCRT', 'HIGHCRT')
    
    # --- HBA1C between 6.5 and 9.5?
    doc = re.sub('hb\s?a1\s+c', 'hba1c', doc, flags=re.S)
    doc = re.sub('hgb\s?a1\s+c', 'hba1c', doc, flags=re.S)
    doc = re.sub('hg\s?a1\s+c', 'hba1c', doc, flags=re.S)
    doc = re.sub('hemoglobin\s+a1\s+c', 'hba1c', doc, flags=re.S)
    doc = re.sub('hemoglobin\s+a1\s', 'hba1c ', doc, flags=re.S)
    doc = re.sub(' a1\s+cs?', ' hba1c', doc, flags=re.S)
    doc = re.sub('glycated hemoglobin', 'hba1c', doc, flags=re.S)
    doc = re.sub('glycosylated hemoglobin', 'hba1c', doc, flags=re.S)
    doc = re.sub('glycohemoglobin', 'hba1c', doc, flags=re.S)
    doc = re.sub('hba1c\s+\d{1,2}\/\d{1,2}\/\d{2,4} ', 'hba1c ', doc, flags=re.S)
    doc = re.sub('hba1c\s+\d{1,2}\/\d{1,2} ', 'hba1c ', doc, flags=re.S)
    doc = re.sub('hba1c\s+in\s+\d{1,2}\/\d{1,2} ', 'hba1c ', doc, flags=re.S)
    doc = re.sub('(hba1c.{0,10}) :', '\\1 ', doc, flags=re.S)
    doc = re.sub('(hba1c)(\s?\(\s?)(\d\\.\d)(\d?\s?\)\s)', '\\1 \\3 ', doc)
    doc = re.sub('hba1c\s?=\s?', 'hba1c ', doc)
    doc = re.sub('(hba1c)(\s+\\.\s+)(\d\\.\d)', '\\1 \\3', doc, flags=re.S)
    for item in set(re.findall('hba1c[\w\s]{0,20} \d\\.\d', doc)):
        hba1c = float(item[-3:])
        if (6.5 <= hba1c and hba1c <= 9.5): doc = doc.replace(item, item + ' GLYHMG ')
#    for item in set(re.findall('hba1c \\( \d\\.\d', doc)):
#        hba1c = float(item[-3:])
#        if (6.5 <= hba1c and hba1c <= 9.5): doc = doc.replace(item, item + ' GLYHMG ')
    for item in set(re.findall('hba1c[\w\s]{0,20} \d ', doc)):
        hba1c = float(item[-2:])
        if (6.5 <= hba1c and hba1c <= 9.5): doc = doc.replace(item, item + 'GLYHMG ')

    # --- can make decisions?
    dic = dict(csv.reader(open('./lexicon/mental.txt')))
    for key in dic:
        doc = re.sub(key, 'MNTCAP ' + key, doc)

    doc = re.sub('non MNTCAP', 'non', doc)
    
    # --- illicit drugs?
    dic = dict(csv.reader(open('./lexicon/illicit.txt')))
    for key in dic: doc = re.sub(key, 'JUNKIE ' + key, doc)

    doc = re.sub(' no JUNKIE', ' no', doc)
    doc = re.sub('JUNKIE(.{0,20}negative)', 'XXX', doc)
    
    # --- alcohol?
    doc = re.sub('(heavy drink)', 'ALCABS \\1', doc)
    doc = re.sub('(drink\w* heavily)', 'ALCABS \\1', doc)
    doc = re.sub('(binge drink)', 'ALCABS \\1', doc)
    doc = re.sub('(alcoholism)', 'ALCABS \\1', doc)
    doc = re.sub('(intoxicat)', 'ALCABS \\1', doc)
    doc = re.sub('(heavy alcohol)', 'ALCABS \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(alcohol abus)', 'ALCABS \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(alcohol binge)', 'ALCABS \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(alcohol depend)', 'ALCABS \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(alcohol withdraw)', 'ALCABS \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(sober )', 'ALCSTP \\1', doc)
    doc = re.sub('(stopped.{0,15} drink)', 'ALCSTP \\1', doc)
    doc = re.sub('(quit.{0,15} drink)', 'ALCSTP \\1', doc)
    doc = re.sub('(drink.{0,15} remote)', 'ALCSTP \\1', doc)
    doc = re.sub('(remote.{0,15} drink)', 'ALCSTP \\1', doc)
    doc = re.sub('(recovering alcoholic)', 'ALCSTP \\1', doc)
    doc = re.sub('(drink.{0,15} years ago)', 'ALCSTP \\1', doc)
    doc = re.sub('(alcohol.{0,15} remote)', 'ALCSTP \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(remote.{0,15} alcohol)', 'ALCSTP \\1', doc, flags=re.IGNORECASE)
    doc = re.sub('(alcohol.{0,15} years ago)', 'ALCSTP \\1', doc, flags=re.IGNORECASE)
    
    # --- ketoacidosis
    doc = re.sub('(ketones.{0,5} positive)', 'KETACD \\1', doc)
    doc = re.sub('(ketoacidosis)', 'KETACD \\1', doc)
    doc = re.sub('(metabolic acidosis)', 'KETACD \\1', doc)
    doc = re.sub('(diabetic acidosis)', 'KETACD \\1', doc)
    doc = re.sub('( not.{0,30})(KETACD )', '\\1', doc)
    
    # --- kidney problems
    doc = re.sub('(renal insufficiency)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal disease)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal failure)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal impairment)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal transplant\w*)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal.{0,20} therapy)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal diet)', '\\1 KIDDAM', doc)
    doc = re.sub('(kidney disease)', '\\1 KIDDAM', doc)
    doc = re.sub('(kidney failure)', '\\1 KIDDAM', doc)
    doc = re.sub('(kidney transplant\w*)', '\\1 KIDDAM', doc)
    doc = re.sub('(kidney diet)', '\\1 KIDDAM', doc)
    doc = re.sub('(worse.{0,20} renal function)', '\\1 KIDDAM', doc)
    doc = re.sub('(worse.{0,20} kidney function)', '\\1 KIDDAM', doc)
    doc = re.sub('(deteriorat.{0,20} renal function)', '\\1 KIDDAM', doc)
    doc = re.sub('(deteriorat.{0,20} kidney function)', '\\1 KIDDAM', doc)
    doc = re.sub('(loss of.{0,10} renal function)', '\\1 KIDDAM', doc)
    doc = re.sub('(loss of.{0,10} kidney function)', '\\1 KIDDAM', doc)
    doc = re.sub('(\w*dialysis)', '\\1 KIDDAM', doc)
    doc = re.sub('(dialyzed)', '\\1 KIDDAM', doc)
    doc = re.sub('(renal medications?)', '\\1 KIDMED', doc)
    doc = re.sub('(proteinuria)', '\\1 KIDDAM', doc)
    doc = re.sub('(nephrotic syndrome)', '\\1 KIDDAM', doc)
    doc = re.sub('(nephrosclerosis)', '\\1 KIDDAM', doc)
    doc = re.sub('(nephropathy)', '\\1 KIDDAM', doc)
    dic = dict(csv.reader(open('./lexicon/kidmed.txt')))
    for key in dic: doc = re.sub(key, key + ' KIDMED', doc)
    
    # --- diabetic complications
    doc = re.sub('(diabet.{0,60} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,50} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,40} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,30} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,20} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,10} \w+pathy)', '\\1 DMCMPL', doc)
    doc = re.sub('(\w+pathy) (.{0,60}diabet)', '\\1 DMCMPL \\2', doc)
    doc = re.sub('(\w+pathy) (.{0,50}diabet)', '\\1 DMCMPL \\2', doc)
    doc = re.sub('(\w+pathy) (.{0,40}diabet)', '\\1 DMCMPL \\2', doc)
    doc = re.sub('(\w+pathy) (.{0,30}diabet)', '\\1 DMCMPL \\2', doc)
    doc = re.sub('(\w+pathy) (.{0,20}diabet)', '\\1 DMCMPL \\2', doc)
    doc = re.sub('(\w+pathy) (.{0,10}diabet)', '\\1 DMCMPL \\2', doc)
    for counter in range(0,6): doc = doc.replace('DMCMPL DMCMPL', 'DMCMPL')
    doc = re.sub('(diabet.{0,20} complicat\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,20} ulcer\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(\w*foot ulcer\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(\w*foot infection\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(extremity.{0,10} ulcer\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabet.{0,20} blister\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(gangren\w+)', '\\1 DMCMPL', doc)
    doc = re.sub('(necrotic)', '\\1 DMCMPL', doc)
    doc = re.sub('(skin necrosis)', '\\1 DMCMPL', doc)
    doc = re.sub('(skin abscess\w*)', '\\1 DMCMPL', doc)
    doc = re.sub('(scleroderm\w+)', '\\1 DMCMPL', doc)
    doc = re.sub('(vitiligo)', '\\1 DMCMPL', doc)
    doc = re.sub('(cellulitis)', '\\1 DMCMPL', doc)
    doc = re.sub('(acanthosis nigricans)', '\\1 DMCMPL', doc)
    doc = re.sub('(diabeticorum)', '\\1 DMCMPL', doc)
    doc = re.sub('(xanthomatosis)', '\\1 DMCMPL', doc)
    doc = re.sub('(digital sclerosis)', '\\1 DMCMPL', doc)
    doc = re.sub('(amputat\w+)', '\\1 DMCMPL', doc)
    for counter in range(0,3): doc = doc.replace('DMCMPL DMCMPL', 'DMCMPL')
    
    doc = re.sub('(without.{0,15} erythema or \w+)', '', doc)
    doc = re.sub('(w/o.{0,15} erythema or \w+)', '', doc)
    doc = re.sub('( no .{0,15}erythema or \w+)', ' ', doc)
    doc = re.sub('(without.{0,15} erythema)', '', doc)
    doc = re.sub('(w/o.{0,15} erythema)', '', doc)
    doc = re.sub('( no .{0,15}erythema)', ' ', doc)
    doc = re.sub('( non ?erythema\w*)', ' ', doc)
    doc = re.sub('(erythema\w*)', '\\1 DMCMPL', doc)
    
    # --- abdminal surgery, intestine resection, bowel obstruction
    doc = re.sub('(abdo.{0,30}tomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(abdo.{0,30}plasty)', '\\1 ABDMNL', doc)
    doc = re.sub('(hysterectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(prostatectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(appendectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(ileocecectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(hernioplasty)', '\\1 ABDMNL', doc)
    doc = re.sub('(colectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(colostomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(gastrectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(splenectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(pancreatectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(cholecystectomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(enterolithotomy)', '\\1 ABDMNL', doc)
    doc = re.sub('(laparo)', 'ABDMNL \\1', doc)
    doc = re.sub('(gallstone)', 'ABDMNL \\1', doc)
    doc = re.sub('(gall stone)', 'ABDMNL \\1', doc)
    doc = re.sub('(duct stone)', 'ABDMNL \\1', doc)
    doc = re.sub('(cholelithiasis)', 'ABDMNL \\1', doc)
    doc = re.sub('(small bowel obstruction\w*)', '\\1 ABDMNL', doc)
    doc = re.sub('(small intestine obstruction\w*)', '\\1 ABDMNL', doc)
    doc = re.sub('(small intestinal obstruction\w*)', '\\1 ABDMNL', doc)
    doc = re.sub('(obstruction.{0,10} small bowel)', '\\1 ABDMNL', doc)
    doc = re.sub('(obstruction.{0,10} small intestine)', '\\1 ABDMNL', doc)
    dic = dict(csv.reader(open('./lexicon/surgery.txt')))
    for key in dic:
        doc = re.sub('(abdo.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(colon.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(intestin.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(bowel.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(ovarian.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(hernia.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(gall\s?bladder.{0,15} '+key+')', '\\1 ABDMNL', doc)
        doc = re.sub('(biliary.{0,15} '+key+')', '\\1 ABDMNL', doc)
    for counter in range(0,3): doc = doc.replace('ABDMNL ABDMNL', 'ABDMNL')

    doc = re.sub('(headache.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(migraine.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(arthriti.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(rheuma.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(swell.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(rash.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(hives.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('(cough.{0,50}) aspirin', '\\1 XXX', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}headache)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}migraine)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}arthriti)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}rheuma)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}swell)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}rash)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}hives)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('aspirin (.{0,50}cough)', 'XXX \\1', doc, flags=re.S)
    doc = re.sub('not take aspirin', 'XXX', doc)
    
    dic = dict(csv.reader(open('./lexicon/prevent.txt')))
    for key in dic:
        doc = re.sub('('+key+'.{0,50} aspirin)', '\\1 ASPFMI', doc, flags=re.S)
        doc = re.sub('(aspirin) (.{0,50}'+key+')', '\\1 ASPFMI \\2', doc, flags=re.S)
    for counter in range(0,5): doc = doc.replace('ASPFMI ASPFMI', 'ASPFMI')

    # --- separate poorly tokenized tags
    doc = re.sub('([a-z])([A-Z]+)', '\\1 \\2', doc)
    doc = re.sub('([A-Z]+)([a-z])', '\\1 \\2', doc)
        
    days = 0
    previous = datetime(2000,1,1)
    for item in reversed(re.findall(' this is record date \d\d\d\d\d\d\d\d \\. ', doc)):
        current = datetime(int(item[21:25]), int(item[25:27]), int(item[27:29]))
        difference = (previous - current).days
        if (difference > 0): days = days + difference
        if (days <= 61): 
            doc = doc.replace(item, ' record within 6 months . \n' + item)
            doc = doc.replace(item, ' record within 3 months . \n' + item)
            doc = doc.replace(item, ' record within 2 months . \n' + item)
        elif (days <= 92): 
            doc = doc.replace(item, ' record within 6 months . \n' + item)
            doc = doc.replace(item, ' record within 3 months . \n' + item)
        elif (days <= 183): 
            doc = doc.replace(item, ' record within 6 months . \n' + item)
        previous = current

    doc = re.sub(' +', ' ', doc)

    f = open(main + file,'w')
    f.write(doc)
    f.close()

    cut = doc.find(' record within 6 months')
    if (cut >= 0): doc = doc[cut:]
    f = open(sixmonths + file,'w')
    f.write(doc)
    f.close()

    cut = doc.find(' record within 3 months')
    if (cut >= 0): doc = doc[cut:]
    f = open(threemonths + file,'w')
    f.write(doc)
    f.close()
    
    cut = doc.find(' record within 2 months')
    if (cut >= 0): doc = doc[cut:]
    f = open(twomonths + file,'w')
    f.write(doc)
    f.close()
