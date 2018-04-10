from xml.etree import cElementTree
from collections import defaultdict


tags_labels = ['ASP-FOR-MI', 'ABDOMINAL', 'DIETSUPP-2MOS', 'ADVANCED-CAD', 'KETO-1YR', 'MAJOR-DIABETES', 'HBA1C',
'MAKES-DECISIONS', 'ALCOHOL-ABUSE', 'ENGLISH', 'DRUG-ABUSE', 'CREATININE', 'MI-6MOS']

EMPTY_ANNOT = dict([(tg, None) for tg in tags_labels])

def get_raw_txt(path):
    'gets raw text from a file'
    with open(path, 'r') as f:
        return f.read()

def get_description(path):
    '''
    Returns content of TEXT tag from xml document.
    '''
    file_struct = cElementTree.parse(path)
    texttag = file_struct.find('TEXT')
    return texttag.text

def get_annotations(path):
    """Return a dictionary with all the annotations in the .ann file."""
    annotations = defaultdict(dict)
    annotation_file = cElementTree.parse(path)
    for tag in annotation_file.findall('.//TAGS/*'):
        annotations['tags'][tag.tag.upper()] = tag.attrib['met']
    return annotations['tags']

def build_tags(tags_dict):
    """"""
    root = cElementTree.Element("PatientMatching")
    doc = cElementTree.SubElement(root, "TAGS")

    for k,v in tags_dict:
        cElementTree.SubElement(doc, k, met = v)
    return root