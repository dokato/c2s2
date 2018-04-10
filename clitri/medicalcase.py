import re
import xml.etree.cElementTree as ET
from datetime import datetime

from utils import *
from conreader import ConNer

class MedicalCase(object):
    def __init__(self, description_path, annotation_path = None, conner = False):
        """
        Args:
          description_path (str) - description of medical case as txt or xml file
          annotation_path (str) - annotation from XML in PatientMatching format
          conner (str) - path to NER clinical annotations in i2b2 format
        """
        self.text = get_description(description_path) if description_path.endswith('.xml') else get_raw_txt(description_path)
        self.gold = get_annotations(annotation_path) if annotation_path else None
        self.annots = EMPTY_ANNOT
        self.time_splits = []
        self._make_time_splits()
        self.conner = None
        if conner:
            self.conner = self._read_conner(conner)

    def build_tags(self, noprint = False):
        """Build output tags and save them to XML format if *save* is True"""
        root = build_tags(annots)
        if not noprint:
            print ET.tostring(root, 'utf-8')

    def _make_time_splits(self):
        """
        Splits description text into time steps based on "record date" pattern.
        """
        self.time_splits = []
        rex = re.compile("record date[ \n:]*[0-9][0-9][0-9][0-9] - [0-9][0-9] - [0-9][0-9]")
        cuts = [(m.start(), m.end()) for m in rex.finditer(self.text)]
        if len(cuts) > 1:
            for i in range(len(cuts)-1):
                date = datetime.strptime(self.text[cuts[i][1]-14:cuts[i][1]], '%Y - %m - %d')
                txt = self.text[cuts[i][1]:cuts[i+1][0]]
                self.time_splits.append((date, txt))
            date = datetime.strptime(self.text[cuts[i+1][1]-14:cuts[i+1][1]], '%Y - %m - %d')
            txt = self.text[cuts[i+1][1]:]
            self.time_splits.append((date, txt))
        else:
            date = datetime.strptime(self.text[cuts[0][1]-14:cuts[0][1]], '%Y - %m - %d')
            txt = self.text[cuts[0][1]:]
            self.time_splits.append((date, txt))

    def _read_conner(self, path):
        """Returns ConNer object"""
        return ConNer(path)


if __name__ == '__main__':
    import sys
    subj = sys.argv[1]
    mc = MedicalCase(description_path = '01_preprocessed/{}.xml.txt'.format(subj),
        annotation_path= 'train/{}.xml'.format(subj),
        conner = 'condtaggeddata/{}.xml.con'.format(subj))
    print mc.gold
    print mc.time_splits
    print mc.conner.tags