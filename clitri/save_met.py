from medicalcase import MedicalCase, load_whole_dataset
from utils import *

###########
meaning_threshold = 1.1
###########

def get_from_mc(mclist):
    """
    Get full text training data from MedicalCase list.
    """
    texts = []
    annots = []
    for mc in mclist:
        texts.append(mc.clean_text)
        if mc.gold is None:
            raise ValueError("It doesn't look like a training data")
        else:
            annots.append(mc.gold)
    return texts, annots

mcdata = load_whole_dataset()
texts, annots = get_from_mc(mcdata)

tags = annots[0].keys()

containers = dict([(x, []) for x in tags])

# Create containers with texts belonging to each tag
for tt, aa in zip(texts, annots):
    for tg in tags:
        if aa[tg] == 'met':
            containers[tg].append(tt)

# Join texts together
longcont = dict()
for tg in tags:
    with open('merged_met/met_merged_' +tg+'.txt','w') as f:
        f.write('\r\n\r\n+++++++++\r\n\r\n'.join(containers[tg]))

