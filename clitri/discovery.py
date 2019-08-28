import re
import os, sys
import sklearn
from datetime import timedelta

from medicalcase import MedicalCase, load_whole_dataset, load_test_dataset
from utils import *

class Discover(object):
    """
    Metaclass with skeleton for specific discover classes
    """
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        self.data = data
        cname = self.__class__.__name__
        if cname in DEFAULT_MODELS:
            self.clf = load_pickle(DEFAULT_MODELS[cname])
        else:
            self.clf = None
        self.vectorizer = load_pickle(DEFAULT_VECTORIZER)
        self.time_limit = None # in days

    def _get_text(self, mc):
        '''
        Returns text from medical condition object *mc*.
        The function check time constraints on medical data if provided.
        '''
        if self.time_limit is None or mc.time_splits is None or len(mc.time_splits) == 1:
            return mc.text
        now_ = mc.time_splits[-1][0]
        selected_text = ""
        for ts, ttext in mc.time_splits:
            if not now_ - ts > timedelta(days=self.time_limit):
                selected_text += ttext + ' '
        return selected_text

    def predict(self, data = None):
        """
        Predict from list of MedicalCases.
        """
        print('prediction of {}'.format(self.tag))
        if data is None:
            data = self.data
        ii=0
        for mc in data:
            self.currmc = mc
            try:
                flag = self._textual_detection(self._get_text(mc))
            except ValueError:
                flag = None
            if flag is None:
                # machine learning voodoo
                flag = self._model_detection(self._get_text(mc))
                ii += 1
            mc.annots[self.tag] = MET_LABEL if flag else NOTMET_LABEL
        print('done ({})'.format(ii))

    def _textual_detection(self, txt):
        """
        Detect based on string analysis.
        """
        return None

    def _model_detection(self, txt):
        """
        Detection based on classifier.
        """
        if self.clf is None:
            raise ValueError("Model not specified. Check path in discovery.DEFAULT_MODELS")
        if self.clf.__class__.__name__ != 'HelmholtzClassifier':
            vcttxt = self.vectorizer.transform([txt])
            pred = self.clf.predict(vcttxt)
        else:
            pred = self.clf.predict(txt, self.tag)
        return True if pred[0] == 1 else False

class DiscoverAlcohol(Discover):
    """Discover ALCOHOL-ABUSE clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverAlcohol, self).__init__(data)
        self.tag = 'ALCOHOL-ABUSE'

    def _textual_detection(self, txt, threshold = 3):
        """
        Detect based on string analysis.
        Returns true if condition met, False if not met, None if not sure.
        """
        if txt.count('ALCSTP') > 0:
            return False
        if txt.count('ALCABS') >= threshold:
            return True
        if txt.count('ALCOHOL') > 0:
            if txt.count('ALCOHOL') > 3: return True
            fragment = txt[txt.index('ALCOHOL')-50:txt.index('ALCOHOL')+50]
            for keystop in ['rare', 'occasional', 'none', 'quit']:
                if keystop in fragment:
                    return False
            return True
        return False

class DiscoverHBA1C(Discover):
    """Discover for HBA1C clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverHBA1C, self).__init__(data)
        self.tag = 'HBA1C'


class DiscoverCreatinine(Discover):
    """Discover for CREATININE clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverCreatinine, self).__init__(data)
        self.creatinine_low = 0.6
        self.creatinine_high = 1.5
        self.tag = 'CREATININE'

class DiscoverKeto(Discover):
    """Discover for KETO-1YR clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverKeto, self).__init__(data)
        self.tag = 'KETO-1YR'

    def _textual_detection(self, txt):
        """
        Detect based on string analysis.
        """
        regket = re.compile('KETACD')
        if len(regket.findall(txt)) > 2:
            return True
        return False

class DiscoverAbdominal(Discover):
    """Discover for ABDOMINAL clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverAbdominal, self).__init__(data)
        self.tag = 'ABDOMINAL'

class DiscoverAdvancedCad(Discover):
    """Discover for KETO-1YR clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverAdvancedCad, self).__init__(data)
        self.tag = 'ADVANCED-CAD'

class DiscoverAspMi(Discover):
    """Discover for ASP-FOR-MI clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverAspMi, self).__init__(data)
        self.tag = 'ASP-FOR-MI'


class DiscoverDietSupp(Discover):
    """Discover for DIETSUPP-2MOS clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverDietSupp, self).__init__(data)
        self.tag = 'DIETSUPP-2MOS'
        #self.time_limit = 2*30 # in days

    def _textual_detection(self, txt):
        """
        Detect based on string analysis.
        """
        regket = re.compile('SPLMNT')
        regdfc = re.compile('DFCNCY')
        if len(regket.findall(txt)) + len(regdfc.findall(txt)) > 1:
            return True
        return False

class DiscoverEnglish(Discover):
    """Discover for ENGLISH clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverEnglish, self).__init__(data)
        self.tag = 'ENGLISH'


class DiscoverDiabetes(Discover):
    """Discover for MAJOR-DIABETES clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverDiabetes, self).__init__(data)
        self.tag = 'MAJOR-DIABETES'

class DiscoverDecisions(Discover):
    """Discover for MAKES-DECISIONS clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverDecisions, self).__init__(data)
        self.tag = 'MAKES-DECISIONS'

class DiscoverMi6Mos(Discover):
    """Discover for MI-6MOS clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverMi6Mos, self).__init__(data)
        self.tag = 'MI-6MOS'
        self.time_limit = 6*30 # in days

    def _decision_tree_detection(self, txt, threshold = 3):
        """
        Detect based on DT model.
        """
        model = load_pickle('models/MI6-dt-4.pkl')
        feats = ['BRPMED',
            'HRTMED',
            'HRTTRT',
            'HRTISC',
            'HRTANG',
            'HRTCAD',
            'ASPFMI',
            'myocardial infarction']
        cnts = []
        import pdb; pdb.set_trace()
        for ff in feats:
            cnts.append(txt.count(ff))
        cnts = np.array(cnts)
        return bool(model.predict([cnts])[0])
    
    def _textual_detection(self, txt, threshold = 4):
        if txt.count('myocardial infarction') + txt.count('ASPFMI') >= threshold:
            return True
        return False

class DiscoverDrug(Discover):
    """Discover for DRUG-ABUSE clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverDrug, self).__init__(data)
        self.tag = 'DRUG-ABUSE'

    def _textual_detection(self, txt, threshold = 1):
        """
        Detect based on string analysis.
        Returns true if condition met, False if not met, None if not sure.
        """
        if txt.count('drug abuse'):
            return True
        if txt.count('JUNKIE') >= threshold:
            return True
        return False

TAG_TO_CLASSES = {
    'CREATININE' : DiscoverCreatinine,
    'ALCOHOL-ABUSE' : DiscoverAlcohol,
    'HBA1C' : DiscoverHBA1C,
    'KETO-1YR' : DiscoverKeto,
    'ABDOMINAL' : DiscoverAbdominal,
    'ADVANCED-CAD' : DiscoverAdvancedCad,
    'ASP-FOR-MI' : DiscoverAspMi,
    'DIETSUPP-2MOS' : DiscoverDietSupp,
    'ENGLISH' : DiscoverEnglish,
    'MAJOR-DIABETES' : DiscoverDiabetes,
    'MAKES-DECISIONS' : DiscoverDecisions,
    'MI-6MOS' : DiscoverMi6Mos,
    'DRUG-ABUSE': DiscoverDrug
}

if __name__ == '__main__':
    if len(sys.argv) == 1:
        mcdata = load_test_dataset()
        for tag in TAGS_LABELS:
            disc = TAG_TO_CLASSES[tag](mcdata)
            disc.predict()
        for mc in mcdata:
            mc.build_tags(noprint=True, save=True, save_folder = 'testoutput/')
    else:
        mcdata = load_test_dataset(annotations = 'test_gold/{}.xml')
        #mcdata = load_whole_dataset()
        tag_to_predict = sys.argv[1]
        disc = TAG_TO_CLASSES[tag_to_predict](mcdata)
        disc.predict()
        fp_vec, fn_vec  = [], []
        tp_vec = []
        for mc in mcdata:
            if mc.gold[tag_to_predict] == NOTMET_LABEL and mc.annots[tag_to_predict] == MET_LABEL:
                fp_vec.append(mc)
            if mc.gold[tag_to_predict] == MET_LABEL and mc.annots[tag_to_predict] == NOTMET_LABEL:
                fn_vec.append(mc)
            if mc.gold[tag_to_predict] == MET_LABEL and mc.annots[tag_to_predict] == MET_LABEL:
                tp_vec.append(mc)
        print('FP')
        print fp_vec
        print len(fp_vec) * 1./len(mcdata)
        print('FN')
        print fn_vec
        print len(fn_vec) * 1./len(mcdata)
        print('TP')
        print tp_vec
        print len(tp_vec) * 1./len(mcdata)