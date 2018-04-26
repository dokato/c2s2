import re
import os
import sklearn

from medicalcase import MedicalCase, load_whole_dataset
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

    def predict(self, data = None):
        """
        Predict from list of MedicalCases.
        """
        print('prediction of {}'.format(self.tag))
        if data is None:
            data = self.data
        ii=0
        for mc in data:
            try:
                flag = self._textual_detection(mc.text)
            except ValueError:
                flag = None
            if flag is None:
                # machine learning voodoo
                flag = self._model_detection(mc.text)
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
            pred = self.clf.predict(vctpptxt)
            return True if pred[0] == 1 else False
        else:
            return False


class DiscoverAlcohol(Discover):
    """Discover ALCOHOL-ABUSE clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverAlcohol, self).__init__(data)
        self.tag = 'ALCOHOL-ABUSE'

    def _textual_detection(self, txt, margin_left = -50, margin_right = 50):
        """
        Returns true if condition met, False if not met, None if not sure.
        """
        flag = None
        expr = 'alcohol'
        idx = txt.index(expr)
        fragment = txt[idx + margin_left:idx + margin_right].replace('\n', ' ')
        #print fragment
        regexnoalc = re.compile(' no .*alcohol')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('alcohol .* no ')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('alcohol use (status)*:')
        if len(regexnoalc.findall(fragment)) > 0:
            m = next(regexnoalc.finditer(fragment))
            fg = fragment[m.end():m.end()+20].translate(None, string.punctuation).strip().split()
            if fg[0] in ['none', 'moderate', 'denies', 'rare']:
                return False
        regexnoalc = re.compile('occasional')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('does not drink')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('denies alcohol')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('does not use')
        if len(regexnoalc.findall(fragment)) > 0:
            return False
        regexnoalc = re.compile('does not use')
        if len(regexnoalc.findall(fragment)) > 0:
            return False

        regexalc = re.compile('drinks')
        if len(regexalc.findall(fragment)) > 0:
            return True

        return flag


class DiscoverHBA1C(Discover):
    """Discover for HBA1C clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverHBA1C, self).__init__(data)
        self.tag = 'HBA1C'

    def _textual_detection(self, txt, margin_left = -20, margin_right = 50):
        """
        Returns true if condition met, False if not met, None if not sure.
        """
        flag = None
        expr = 'hba1c'
        
        idx = txt.index(expr)
        fragment = txt[idx + margin_left:idx + margin_right]
        print fragment
        return flag

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

    def _textual_detection(self, txt, margin_left = -20, margin_right = 50):
        """
        Returns true if condition met, False if not met, None if not sure.
        """
        flag = None
        expr = 'creatinine'
        
        idx = txt.index(expr)
        fragment = txt[idx + margin_left:idx + margin_right].replace('\n', ' ')
        
        # Trying to detect numerical value
        regexnum = re.compile("[0-9]+\.?[0-9]*")
        endvec = [(m.end() - (-margin_left + len(expr)), fragment[m.start():m.end()]) for m in regexnum.finditer(fragment)]
        if len(endvec) > 0:
            absends = sorted([(abs(x[0]), e) for e, x in enumerate(endvec)])
            creatinine_value = float(endvec[absends[0][1]][1])
            if creatinine_value < 10: # only such a creatinine values make sense in our scale
                flag = not self.creatinine_low <= creatinine_value <= self.creatinine_high
        # If numerical value not present we try to detect abnormal creatinine indicators
        if flag is None:
            creatine_text_indicators = [('increased', True), ('elevated', True), ('notable', True),
                                        ('normal', False)]
            for cti, fl in creatine_text_indicators:
                if cti in fragment:
                    flag = fl
        return flag


class DiscoverKeto(Discover):
    """Discover for KETO-1YR clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverKeto, self).__init__(data)
        self.tag = 'KETO-1YR'

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

class DiscoverEnglish(Discover):
    """Discover for ENGLISH clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverEnglish, self).__init__(data)
        self.tag = 'ENGLISH'


class DiscoverKeto(Discover):
    """Discover for KETO-1YR clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverKeto, self).__init__(data)
        self.tag = 'KETO-1YR'

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

class DiscoverDrug(Discover):
    """Discover for DRUG-ABUSE clinical trial"""
    def __init__(self, data):
        """
        Args:
          data (list <MedicalCase>)
        """
        super(DiscoverDrug, self).__init__(data)
        self.tag = 'DRUG-ABUSE'


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
    mcdata = load_whole_dataset()
    #dh = DiscoverCreatinine(mcdata)
    #dh.predict()
    for tag in TAGS_LABELS:
        disc = TAG_TO_CLASSES[tag](mcdata)
        disc.predict()
    for mc in mcdata:
        print mc.name, mc.annots
        mc.build_tags(noprint=True, save=True)