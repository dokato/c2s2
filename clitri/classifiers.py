import re
import os
import datetime
import argparse

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from sklearn.svm import LinearSVC, SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from helmholtz import HelmholtzVectorizer
from xgboost import XGBClassifier
from sklearn.pipeline import Pipeline
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import SelectFromModel

from medicalcase import MedicalCase, load_whole_dataset
from utils import *

class BorutaVoter(object):
    '''
    Dummy empty class to not destroy current pipeline.
    '''
    pass

def build_tfidf(texts, file_to_save = None):
    """
    Create TfIdf and pickle it.
    """
    from sklearn.feature_extraction import text
    stop_words = text.ENGLISH_STOP_WORDS.union(['xxx'])
    #HelmholtzVectorizer()#
    #TfidfVectorizer(max_df=0.5, min_df=1, stop_words='english', use_idf=False, ngram_range=(1,2))
    vectorizer = CountVectorizer(ngram_range=(1,2), stop_words=stop_words)
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
    if isinstance(clf, BorutaVoter):
        build_boruta_voter(trdata, annotations, tfidf_name, label, file_to_save, time)
    else:
        vectorizer = load_pickle(tfidf_name)
        annot_enc = np.array([encode_annotations(ant) for ant in annotations])
        tag_enc = get_tag_encoding(annot_enc, label)
        frsttag, sectag = balancing(tag_enc, method='under')
        X_tr = vectorizer.transform(trdata)
        X_tr = X_tr[np.r_[frsttag,sectag]] # balanced training data
        tag_enc = tag_enc[np.r_[frsttag,sectag]] # balanced labels
        if clf.__class__.__name__ != 'HelmholtzClassifier':
            #clf = Pipeline([
            #        ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
            #        ('classify', clf)
            #        ])
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

def build_boruta_voter(trdata, annotations, tfidf_name, label, file_to_save = None, time = False):
    """
    Building boruta algorithm + ensemble learning.
    """
    from boruta import BorutaPy
    vectorizer = load_pickle(tfidf_name)
    X_tr = vectorizer.transform(trdata)
    annot_enc = np.array([encode_annotations(ant) for ant in annotations])
    tag_enc = get_tag_encoding(annot_enc, label)

    rf = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=5)

    feat_selector = BorutaPy(rf, n_estimators='auto', verbose=2, random_state=1)
    log_clf = LogisticRegression(random_state=42)
    rnd_clf = RandomForestClassifier(random_state=42)
    params = {'n_estimators': 1200, 'max_depth': 3, 'subsample': 0.5,
              'learning_rate': 0.01, 'min_samples_leaf': 1, 'random_state': 42}
    grd_clf = GradientBoostingClassifier(**params)

    voting_clf = VotingClassifier(
        estimators=[('lr', log_clf), ('rf', rnd_clf), ('grd', grd_clf)],
        voting='soft')
    pipe = Pipeline([
        ('feature_selection', feat_selector),
        ('classify', voting_clf)
    ])
    pipe.fit(X_tr.toarray(), tag_enc)
    if file_to_save:
        if time:
            now = str(datetime.datetime.now())[:-7].replace(':','_').replace(' ','_').replace('-','_')
        else:
            now = ''
        clf_name = file_to_save + '_' + now + label
        save_pickle(pipe, clf_name)

if __name__ == '__main__':
    mcdata = load_whole_dataset()
    texts, annots = get_training_from_mc(mcdata)
    parser = argparse.ArgumentParser(description="Builds clf model. Will be stored in 'models' folder.")
    parser.add_argument("-t", "--tfidf", dest="tfidf", default=None, type=str,
                        help="""
                        build tf idf: specify name to save it. Date will be added.
                        To overwrite name it simply tfidf.""")
    #parser.add_argument("-c", "--classifier", dest="classifier", default='XGBClassifier(learning_rate=.05, max_depth=5, n_estimators=70)', type = str, help="classifier to choose")
    parser.add_argument("-c", "--classifier", dest="classifier", default='XGBClassifier(learning_rate=.05, max_depth=5, n_estimators=100)', type = str, help="classifier to choose")
    parser.add_argument("-n", "--name", dest="name", type = str, default='model',
                         help="method of source reconstruction")
    parser.add_argument("-v", "--vectorizer", dest="vectorizer", type = str, default = None,
                         help="if given uses specific vectorizer. Must be in models folder")
    parser.add_argument("-g", "--tag", dest="tag", type = str, default = None,
                         help="Tag to train. If not given, all models will be created.")
    args = parser.parse_args()
    if not args.tfidf is None:
        build_tfidf(texts, 'models/' + args.tfidf)
    else:
        print(args.classifier)
        if args.classifier != 'HelmholtzClassifier':
            code_to_call = args.classifier + "()" if not args.classifier.endswith(')') else args.classifier
            clf = eval(code_to_call)
        else:
            clf = eval(args.classifier + "(TAGS_LABELS)")
        vectorizer = 'models/' + args.vectorizer if args.vectorizer else DEFAULT_VECTORIZER
        if args.tag:
            if args.tag in TIME_LIMITED_TAGS.keys():
                    texts_timed, _ = get_training_from_mc(mcdata, TIME_LIMITED_TAGS[args.tag])
                    build_model(clf, texts_timed, annots, vectorizer, args.tag, 'models/' + args.name)                
            build_model(clf, texts, annots, vectorizer, args.tag, 'models/' + args.name)
        else:
            for tag in TAGS_LABELS:
                if tag == 'KETO-1YR':
                    continue
                print('Building: ' + tag)
                if tag in TIME_LIMITED_TAGS.keys():
                    texts_timed, _ = get_training_from_mc(mcdata, TIME_LIMITED_TAGS[tag])
                    build_model(clf, texts_timed, annots, vectorizer, tag, 'models/' + args.name)
                build_model(clf, texts, annots, vectorizer, tag, 'models/' + args.name)
        print('.')
