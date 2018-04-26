import re, os, copy
import xml.etree.cElementTree as ET
from datetime import datetime

from utils import *
from conreader import ConNer

class MedicalCase(object):
    def __init__(self, name, description_path, annotation_path = None, conner = False):
        """
        Args:
          name (str) - patient name
          description_path (str) - description of medical case as txt or xml file
          annotation_path (str) - annotation from XML in PatientMatching format
          conner (str) - path to NER clinical annotations in i2b2 format
        """
        self.name = name
        self.text = get_description(description_path) if description_path.endswith('.xml') else get_raw_txt(description_path)
        self.text = default_text_preprocessing(self.text)
        self.gold = get_annotations(annotation_path) if annotation_path else None
        self.annots = copy.copy(EMPTY_ANNOT)
        self.time_splits = []
        #self._make_time_splits()
        self.conner = None
        if conner:
            self.conner = self._read_conner(conner)

    def build_tags(self, noprint = False, save = False, save_folder = 'output'):
        """Build output tags and save them to XML format if *save* is True"""
        root = build_tags(self.annots)
        if not noprint:
            print ET.tostring(root, 'utf-8')
        if save:
            strdata = ET.tostring(root, 'utf-8')
            with open(os.path.join(save_folder, self.name + '.xml'), "w") as f:
                f.write(strdata)

    def meaningfulness(self, score_dict, splitter = ' '):
        '''
        Returns meaningfulness.
        Args:
          score_dict (dict) - scores for particular words (key, score) e.g {(cat, 1.1), (frog, 0.4)}
          splitter (str) - how to split text, default: ' '
        Returns:
          numeric value
        '''
        val = 0
        for tok in self.text.split(splitter):
            if tok in score_dict:
                val += score_dict[tok]
        return val

    def _make_time_splits(self):
        """
        Splits description text into time steps based on "record date" pattern.
        """
        self.time_splits = []
        rex = re.compile("record date[ \n:]*[0-9][0-9][0-9][0-9][ \n]+[0-9][0-9][ \n]+[0-9][0-9]")
        cuts = [(m.start(), m.end()) for m in rex.finditer(self.text)]
        if len(cuts) > 1:
            for i in range(len(cuts)-1):
                date = datetime.strptime(self.text[cuts[i][1]-10:cuts[i][1]], '%Y %m %d')
                txt = self.text[cuts[i][1]:cuts[i+1][0]]
                self.time_splits.append((date, txt))
            date = datetime.strptime(self.text[cuts[i+1][1]-10:cuts[i+1][1]], '%Y %m %d')
            txt = self.text[cuts[i+1][1]:]
            self.time_splits.append((date, txt))
        else:
            date = datetime.strptime(self.text[cuts[0][1]-10:cuts[0][1]], '%Y %m %d')
            txt = self.text[cuts[0][1]:]
            self.time_splits.append((date, txt))

    def _read_conner(self, path):
        """Returns ConNer object"""
        return ConNer(path)

    def __repr__(self):
        return "MedicalCase {}".format(self.name)


def load_whole_dataset(path = 'train'):
    """
    Loads whole dataset of patients data description.
    Paths to specific files are defined in CONFIG_PATH constant.
    """
    mcdata = []
    for subj in [x[:-4] for x in os.listdir(path)]:
        mc = MedicalCase(subj,
            description_path = CONFIG_PATH['preprocessed'].format(subj),
            annotation_path= CONFIG_PATH['annotations'].format(subj),
            conner = CONFIG_PATH['conner'].format(subj))
        mcdata.append(mc)
    return mcdata

if __name__ == '__main__':
    import sys
    subj = sys.argv[1]
    mc = MedicalCase(subj,
        description_path = '01_preprocessed/{}.xml.txt'.format(subj),
        annotation_path = 'train/{}.xml'.format(subj),
        conner = 'condtaggeddata/{}.xml.con'.format(subj))
    print mc.gold
    print mc.time_splits
    print mc.conner.tags