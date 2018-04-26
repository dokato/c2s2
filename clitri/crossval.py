import re
import os, shutil
import subprocess

from medicalcase import MedicalCase
from utils import *

from classifiers import *
from discovery import *

from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import ShuffleSplit
import numpy as no 

### Params:
clf = LinearSVC()
N_cross = 10
###

def load_cross_dataset(subj_names):
    """
    Loads crossvalidation dataset of patients data description.
    """
    mcdata = []
    for subj in subj_names:
        mc = MedicalCase(subj,
            description_path = CONFIG_PATH['preprocessed'].format(subj),
            annotation_path= CONFIG_PATH['annotations'].format(subj),
            conner = CONFIG_PATH['conner'].format(subj))
        mcdata.append(mc)
    return mcdata

ss = ShuffleSplit(n_splits = N_cross, test_size = 0.1)

all_paths = [x[:-4] for x in os.listdir('train/')]

full_scores = dict([(t, []) for t in TAGS_LABELS])
full_scores['Overall'] = []

for spl in ss.split(all_paths):
    test_paths = [ap for e, ap in enumerate(all_paths) if e in spl[1]]
    train_paths = [ap for e, ap in enumerate(all_paths) if e in spl[0]]

    mc_train = load_cross_dataset(train_paths)
    texts, annots = get_training_from_mc(mc_train)

    vectorizer = DEFAULT_VECTORIZER 
    for tag in TAGS_LABELS:
        print('Building: ' + tag)
        build_model(clf, texts, annots, vectorizer, tag, 'models/model')

    mc_test = load_cross_dataset(test_paths)

    for tag in TAGS_LABELS:
        disc = TAG_TO_CLASSES[tag](mc_test)
        disc.predict()

    out_fold_name = 'crossout'
    trn_fold_name = 'crosstrn'

    os.mkdir(out_fold_name)
    os.mkdir(trn_fold_name)

    for mc in mc_test:
        mc.build_tags(noprint=True, save=True, save_folder = out_fold_name)

    for mc in mc_test:
        shutil.copyfile('train/' + mc.name +'.xml', trn_fold_name + '/' + mc.name +'.xml')

    bash_command = "python iaa.py -t 1 {}/ {}/".format(trn_fold_name, out_fold_name)
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    print(output)

    idx = output.index('Overall')
    full_scores['Overall'].append(float(output[idx+8:idx+15].strip()))
    for tg in TAGS_LABELS:
        idx = output.index(tg[0] + tg[1:].lower())
        full_scores[tg].append(float(output[idx+8:idx+15].strip()))

    shutil.rmtree(out_fold_name)
    shutil.rmtree(trn_fold_name)

print('++++++++++++++++++++++++')

for tg in TAGS_LABELS:
    print('{}: {:.3f} (+- {:.3f})'.format(tg, np.mean(full_scores[tg]), np.std(full_scores[tg])/N_cross**0.5))

print('Final score: {:.3f} (+- {:.3f})'.format(np.mean(full_scores['Overall']), np.std(full_scores['Overall'])/N_cross**0.5))