import re
import csv
import os
import shutil

# --- set up spaCy
import spacy
parser = spacy.load('en')

# --- input files
in_dir = 'train/'

# --- output files
out_dir = '01_preprocessed/'
try:
    shutil.rmtree(out_dir)
except OSError:
    pass
os.mkdir(out_dir)

# --- dictionaries
dic1 = dict(csv.reader(open('abbrev.txt')))
dic2 = dict(csv.reader(open('mwe.txt')))

for e,file in enumerate(os.listdir(in_dir)):
    print e,file
    # --- read document
    f = open(in_dir + file, 'r')
    doc = f.read()
    f.close()

    # --- clean document
    doc = re.sub('.*CDATA\[', '', doc, flags=re.S)
    doc = re.sub('\]\]></TEXT>.*', '', doc, flags=re.S)
    doc = re.sub('<[a-zA-Z]+>', ' ', doc)
    doc = doc.replace('gentleman', 'male')
    doc = doc.replace('lady', 'female')
    doc = doc.replace('M.Sc.', '')
    doc = doc.replace('Jr.', '')
    doc = doc.replace('JR.', '')
    doc = doc.replace('&#183;', ' . ')
    doc = doc.replace('&#224;', ' . ')
    doc = doc.replace('&#8211;', ' . ')
    doc = doc.replace('&gt;', ' greater than ')
    doc = doc.replace('&lt;', ' less than ')
    doc = doc.replace('>', ' greater than ')
    doc = doc.replace('<', ' less than ')
    doc = doc.replace('x. ', 'x ')
    doc = doc.replace('.)', '. ')
    doc = re.sub('q\\. ', 'q.', doc)
    doc = re.sub('([a-zA-Z])\\.([a-zA-Z])\\.([a-zA-Z])\\.', '\\1\\2\\3', doc)
    doc = re.sub('([a-zA-Z])\\.([a-zA-Z])\\.', '\\1\\2', doc)
    doc = re.sub('(\\.)([a-zA-Z])', '. \\2', doc)
    doc = re.sub('\n[0-9]+\\.\s', ' . This is a list item. ', doc)
    doc = re.sub('\n[0-9]+\)\s', ' . This is a list item. ', doc)
    doc = re.sub('[\s/]PE:', '\nPHYSICAL EXAMINATION:', doc)
    doc = re.sub('\n([^\n]+): ', '\n . \\1: ', doc)
    doc = re.sub('\n+', ' ', doc)
    doc = re.sub('_+', 'NEW RECORD: ', doc)
    doc = re.sub('\\*+', '.', doc)
    doc = re.sub('\\"', '', doc)
    doc = re.sub('\s+', ' ', doc)
    doc = re.sub(': ', ': . ', doc)
    doc = re.sub('(\d)([a-zA-Z])', '\\1 \\2', doc)
    doc = re.sub('(\d)\-([a-zA-Z])', '\\1 - \\2', doc)
    doc = re.sub(' yo [mM] ', ' yo male ', doc)
    doc = re.sub(' yo [fF] ', ' yo female ', doc)
    doc = re.sub('[xX]\-ray', 'xray', doc)
    doc = re.sub('[aA]\-fib', 'afib', doc)
    doc = re.sub('[aA] fib', 'afib', doc)
    doc = re.sub('[vV]\-fib', 'vfib', doc)
    doc = re.sub('[vV] fib', 'vfib', doc)
    doc = re.sub('(\\. )*\\.', '.', doc)
    doc = re.sub('\s+', ' ', doc)

    # --- parse document
    parsedDoc = parser(doc.decode('utf-8'))

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
            tokenized = ''
            for i, token in enumerate(parse):
                t = token.lower_
                if t in dic1.keys(): t = dic1[t]
                tokenized += t + ' '
            for key in dic2: tokenized = tokenized.replace(' ' + key + ' ',  ' ' + dic2[key] + ' ')
            tokenized = tokenized.strip(' ')
            if tokenized not in ['']: f.write(tokenized.encode('utf-8')+'\n')
    f.close()
