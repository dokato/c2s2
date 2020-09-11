import re, os, copy
import xml.etree.cElementTree as ET
from datetime import datetime, timedelta

from utils import *
try:
    from conreader import ConNer
except ImportError:
    pass

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
        self.clean_text = get_description(description_path) if description_path.endswith('.xml') else get_raw_txt(description_path)
        self.text = default_text_preprocessing(self.clean_text)
        self.gold = get_annotations(annotation_path) if annotation_path else None
        self.annots = copy.copy(EMPTY_ANNOT)
        self.time_splits = self._make_time_splits()
        self.conner = None
        if conner:
            self.conner = self._read_conner(conner)

    def build_tags(self, noprint = False, save = False, save_folder = 'output'):
        """Build output tags and save them to XML format if *save* is True"""
        root = build_tags(self.annots)
        if not noprint:
            print(ET.tostring(root, 'utf-8'))
        if save:
            strdata = ET.tostring(root, 'utf-8')
            with open(os.path.join(save_folder, self.name + '.xml'), "w") as f:
                f.write(strdata)

    def get_timed_text(self, time_limit):
        """
        Args:
          *time_limit* (int) - in days
        """
        if time_limit is None or self.time_splits is None or len(self.time_splits) == 1:
            return self.text
        now_ = self.time_splits[-1][0]
        selected_text = ""
        for ts, ttext in self.time_splits:
            if not now_ - ts > timedelta(days = time_limit):
                selected_text += ttext + ' '
        return selected_text

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
        for tok in self.clean_text.split(splitter):
            if tok in score_dict:
                val += score_dict[tok]
        return val

    def _make_time_splits(self):
        """
        Splits description text into time steps based on "record date" pattern.
        """
        time_splits = []
        rex = re.compile("this is record date[ \n:].")
        rex_date = re.compile("[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]")
        date_format = '%Y%m%d'
        cuts = [(m.start(), m.end()) for m in rex.finditer(self.clean_text)]
        if len(cuts) > 1:
            for i in range(len(cuts)-1):
                cutting = self.clean_text[cuts[i][0]:cuts[i][0]+40].replace('\n', ' ')
                try:
                    pattdate =  rex_date.findall(cutting)[0]
                except IndexError:
                    return None
                date = datetime.strptime(pattdate, date_format)
                txt = self.clean_text[cuts[i][1]:cuts[i+1][0]]
                time_splits.append((date, default_text_preprocessing(txt)))
            cutting = self.clean_text[cuts[-1][0]:cuts[-1][0]+40].replace('\n', ' ')
            try:
                pattdate =  rex_date.findall(cutting)[0]
                date = datetime.strptime(pattdate, date_format)
                txt = self.clean_text[cuts[-1][1]:]
                time_splits.append((date, default_text_preprocessing(txt)))
            except IndexError:
                return None
        else:
            cutting = self.clean_text[cuts[0][0]:cuts[0][0]+40].replace('\n', ' ')
            pattdate =  rex_date.findall(cutting)[0]
            date = datetime.strptime(pattdate, date_format)
            txt = self.clean_text[cuts[-1][1]:]            
            time_splits.append((date, default_text_preprocessing(txt)))
        return time_splits

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
            annotation_path= CONFIG_PATH['annotations'].format(subj)) 
        #conner = CONFIG_PATH['conner'].format(subj)) - not used in the end
        mcdata.append(mc)
    return mcdata

def load_test_dataset(path = 'test_notags', annotations = ''):
    """
    Loads whole test dataset of patients data description.
    Paths to specific files are defined in CONFIG_PATH constant.
    *annotantions* - 
    """
    mcdata = []
    for subj in [x[:-4] for x in os.listdir(path)]:
        if len(annotations):
            mc = MedicalCase(subj,
                description_path = CONFIG_PATH['test_preprocessed'].format(subj),
                annotation_path = annotations.format(subj))
        else:
            mc = MedicalCase(subj,
                description_path = CONFIG_PATH['test_preprocessed'].format(subj))
        mcdata.append(mc)
    return mcdata

if __name__ == '__main__':
    import sys
    subj = sys.argv[1]
    mc = MedicalCase(subj,
        description_path = 'preproc/02_main/{}.xml.txt'.format(subj),
        annotation_path = 'train/{}.xml'.format(subj)) #conner = 'condtaggeddata/{}.xml.con'.format(subj))
    #print mc.gold
    #print mc.conner.tags
