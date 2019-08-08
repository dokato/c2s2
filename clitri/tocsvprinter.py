from medicalcase import MedicalCase, load_whole_dataset, load_test_dataset
from utils import *

mcdata = load_whole_dataset()
#mcdata = load_test_dataset(annotations = 'test_gold/{}.xml')

tag = 'MI-6MOS'
expr_to_detect = 'myocardial infarction'

threshold = 3

tp,fp = 0, 0
for mc in mcdata:
    if mc.gold[tag] == MET_LABEL:
        print '+met', mc, mc.text.count(expr_to_detect)
        tp += 1 if mc.text.count(expr_to_detect) >=threshold else 0
    if mc.gold[tag] == NOTMET_LABEL and mc.text.count(expr_to_detect):
        print '-not', mc, mc.text.count(expr_to_detect)
        fp += 1 if mc.text.count(expr_to_detect) >= threshold else 0

print 'tp', tp, 'fp', fp