from helmholtz import *
from medicalcase import MedicalCase, load_whole_dataset
from utils import *
import matplotlib.pyplot as plt

###########
meaning_threshold = 1.1
###########

mcdata = load_whole_dataset()
texts, annots = get_training_from_mc(mcdata)

tags = annots[0].keys()

containers = dict([(x, []) for x in tags])

# Create containers with texts belonging to each tag
for tt, aa in zip(texts, annots):
    for tg in tags:
        if aa[tg] == 'met':
            containers[tg].append(tt)

# Join texts together
longcont = dict()
full_doc = []
for tg in tags:
    longcont[tg] = ''.join(containers[tg]).split(' ')
    full_doc.append(longcont[tg])

# Make counters and calculate Helmholtz score
doc_dc = make_count_dict(flat_list(full_doc))
Ldoc = len(flat_list(full_doc))
meanfulldc = dict()
for tg in tags:
    print tg
    cont_dc = make_count_dict(longcont[tg])
    vec_meaning = get_meaning_for_tokens(cont_dc, doc_dc, int(Ldoc*1./len(cont_dc)))
    meanfulldc[tg] = dict([(k,v) for k,v in vec_meaning if v > meaning_threshold])


# calculate and visualize Helmholtz scores

plt.figure()
for e, tg in enumerate(tags):
    notmetvec, metvec = [], []
    for mc in mcdata:
        vm = mc.meaningfulness(meanfulldc[tg])
        if mc.gold[tg] == 'met':
            metvec.append(vm)
        else:
            notmetvec.append(vm)

    plt.subplot(2, 7, e + 1)
    plt.plot([0]*len(notmetvec)+[1]*len(metvec), notmetvec + metvec, 'o')
    plt.title(tg)

plt.show()
