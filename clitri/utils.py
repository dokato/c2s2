import re
import string
import cPickle
import numpy as np 

from xml.etree import cElementTree
from collections import defaultdict

######### Config: ####################
DEFAULT_MODELS = {
    'DiscoverCreatinine' : 'models/model_CREATININE.pkl',
    'DiscoverAlcohol' : 'models/model_ALCOHOL-ABUSE.pkl',
    'DiscoverDrug': 'models/model_DRUG-ABUSE.pkl',
    'DiscoverHBA1C' : 'models/model_HBA1C.pkl',
    'DiscoverKeto' : 'models/model_KETO-1YR.pkl',
    'DiscoverAbdominal' : 'models/model_ABDOMINAL.pkl',
    'DiscoverAdvancedCad' : 'models/model_ADVANCED-CAD.pkl',
    'DiscoverAspMi' : 'models/model_ASP-FOR-MI.pkl',
    'DiscoverDietSupp' : 'models/model_DIETSUPP-2MOS.pkl',
    'DiscoverEnglish' : 'models/model_ENGLISH.pkl',
    'DiscoverKeto' : 'models/model_KETO-1YR.pkl',
    'DiscoverDiabetes' : 'models/model_MAJOR-DIABETES.pkl',
    'DiscoverDecisions' : 'models/model_MAKES-DECISIONS.pkl',
    'DiscoverMi6Mos' : 'models/model_MI-6MOS.pkl'
}

DEFAULT_VECTORIZER = 'models/tfidf_2018_04_24_16_31_17.pkl'#'models/helm_2018_05_01_12_22_28.pkl'

CONFIG_PATH = {
    'preprocessed': 'preproc/02_main/{}.xml.txt',
    'annotations': 'train/{}.xml',
    'conner': 'condtaggeddata/{}.xml.con'
}
######################################

MET_LABEL = 'met'
NOTMET_LABEL = 'not met'

TAGS_LABELS = ['ASP-FOR-MI', 'ABDOMINAL', 'DIETSUPP-2MOS', 'ADVANCED-CAD', 'KETO-1YR', 'MAJOR-DIABETES', 'HBA1C',
'MAKES-DECISIONS', 'ALCOHOL-ABUSE', 'ENGLISH', 'DRUG-ABUSE', 'CREATININE', 'MI-6MOS']

TIME_LIMITED_TAGS = {'DIETSUPP-2MOS' : 2*31, # in days
                     'KETO-1YR' : 366,
                     'MI-6MOS' : 6*31}

EMPTY_ANNOT = dict([(tg, None) for tg in TAGS_LABELS])

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
    for k in tags_dict:
        cElementTree.SubElement(doc, k, met = tags_dict[k])
    return root

def encode_annotations(annotation):
    '''
    Data binarization.
    '''
    return np.array([1 if annotation[x] == 'met' else 0 for x in TAGS_LABELS])

def __simple_text_cleaning(text):
    '''
    Dummy text cleaning.
    Don't use it. Look at *default_text_preprocessing*.
    '''
    a = ' '.join([x.strip() for x in text.split('\n') if len(x) > 0 ])
    a = a.translate(None, string.punctuation)
    a = re.sub( '\s+', ' ', a ).strip()
    a = re.sub(r'[0-9]+', '', a).strip()
    a = re.sub('record within .+months', '', a)
    a = ' '.join([x.strip() for x in a.split(' ') if len(x) > 1 ])
    return a

def default_text_preprocessing(text):
    """
    Default preprocessing used in all model and for predictions.
    """
    return __simple_text_cleaning(text)

def get_tag_encoding(array, tag):
    """
    Args:
      array (np.array) - array m x n, where m is number of examples, n nr of tags
      tag (str) - name of tag from TAGS_LABELS
    Returns:
      (np.array) column vector
    """
    return array[:, TAGS_LABELS.index(tag)]

def save_pickle(obj, name):
    """
    Store to pickle
    """
    if not name.endswith('pkl'):
        name += '.pkl'
    with open(name, 'wb') as fid:
        cPickle.dump(obj, fid)

def load_pickle(name):
    """
    Load from pickle
    """
    if not name.endswith('pkl'):
        name += '.pkl'
    with open(name, 'rb') as fid:
        obj_loaded = cPickle.load(fid)
        return obj_loaded

def get_training_from_mc(mclist, time_limit = None):
    """
    Get full text training data from MedicalCase list.
    It might be limited to specific time frames: time_limit (in days).
    """
    texts = []
    annots = []
    for mc in mclist:
        texts.append(mc.get_timed_text(time_limit))
        if mc.gold is None:
            raise ValueError("It doesn't look like a training data")
        else:
            annots.append(mc.gold)
    return texts, annots