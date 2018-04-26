import re
import os
import datetime
import argparse

from sklearn.svm import LinearSVC, SVC

from sklearn.feature_extraction.text import TfidfVectorizer

from medicalcase import MedicalCase, load_whole_dataset
from utils import *

def build_tfidf(texts, file_to_save = None):
    """
    Create TfIdf and pickle it.
    """
    vectorizer = TfidfVectorizer(max_df=0.5, min_df=1, stop_words='english', use_idf=True)
    vectorizer.fit(texts)
    if file_to_save:
        now = str(datetime.datetime.now())[:-7].replace(':','_').replace(' ','_').replace('-','_')
        tfidf_name = file_to_save + '_' + now
        save_pickle(vectorizer, tfidf_name)
    return vectorizer

def build_model(clf, trdata, annotations, tfidf_name, label, file_to_save = None, time = False):
    """
    Create model from given texts *trdata* which are vectorized using *tfidf_name*,
    trained to recognize *label* from *annotations* and saved if specified *file_to_save*.
    """
    vectorizer = load_pickle(tfidf_name)
    annot_enc = np.array([encode_annotations(ant) for ant in annotations])
    tag_enc = get_tag_encoding(annot_enc, label)
    X_tr = vectorizer.transform(trdata)
    if clf.__class__.__name__ != 'HelmholtzClassifier':
        clf.fit(X_tr, tag_enc)
    else:
        clf.fit(trdata, annotations)
    if file_to_save:
        if time:
            now = str(datetime.datetime.now())[:-7].replace(':','_').replace(' ','_').replace('-','_')
        else:
            now = ''
        clf_name = file_to_save + '_' + now + label
        save_pickle(clf, clf_name)

if __name__ == '__main__':
    mcdata = load_whole_dataset()
    texts, annots = get_training_from_mc(mcdata)

    parser = argparse.ArgumentParser(description="Builds clf model. Will be stored in 'models' folder.")
    parser.add_argument("-t", "--tfidf", dest="tfidf", default=None, type=str,
                        help="""
                        build tf idf: specify name to save it. Date will be added.
                        To overwrite name it simply tfidf.""")
    parser.add_argument("-c", "--classifier", dest="classifier", default='SVC', type = str, help="classifier to choose")
    parser.add_argument("-n", "--name", dest="name", type = str, default='model',
                         help="method of source reconstruction")
    parser.add_argument("-v", "--vectorizer", dest="vectorizer", type = str, default = None,
                         help="if given uses specific vectorizer. Must be in models folder")
    parser.add_argument("-g", "--tag", dest="tag", type = str, default = None,
                         help="Tag to train. If not given, all models will be created.")
    args = parser.parse_args()
    if not args.tfidf is None:
        build_tfidf(texts_cl, 'models/' + args.tfidf)
    else:
        if args.classifier != 'HelmholtzClassifier':
            clf = eval(args.classifier + "()")
        else:
            clf = eval(args.classifier + "(TAGS_LABELS)")
        vectorizer = 'models/' + args.vectorizer if args.vectorizer else DEFAULT_VECTORIZER
        if args.tag:
            build_model(clf, texts, annots, vectorizer, args.tag, 'models/' + args.name)
        else:
            for tag in TAGS_LABELS:
                print('Building: ' + tag)
                build_model(clf, texts, annots, vectorizer, tag, 'models/' + args.name)
        print('.')