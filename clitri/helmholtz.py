import numpy as np
import scipy.special
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
from sklearn.linear_model import LogisticRegression

lemmatizer = WordNetLemmatizer()

def nfa(m, K, N):
    '''
    Number of False Alarms (from Helmholtz principle).
    Params:
        m - number of occurences of word in paragraph
        K - number of occurences of word in document
        N (int) - ratio of number of words in document per number of words in paragraph
    Returns:
        nfa (float) - number of false alarms
    '''
    return scipy.special.binom(K, m) * 1./(N**(m-1))

def meaning(m, K, N):
    '''
    Meaning (from Helmholtz principle).
    Params:
        m - number of occurences of word in paragraph
        K - number of occurences of word in document
        N (int) - ratio of number of words in document per number of words in paragraph
    Returns:
        meaning (float) - meaning score of words in paragraph
    '''
    return - np.log(nfa(m, K, N))*1./ m

def opt_meaning(m, K, N):
    '''
    Optimized Meaning (from Helmholtz principle).
    Params:
        m - number of occurences of word in paragraph
        K - number of occurences of word in document
        N (int) - ratio of number of words in document per number of words in paragraph
    Returns:
        meaning (float) - meaning score of words in paragraph
    '''
    return -(np.sum(np.log(np.arange(K-m+1, K))) + np.sum(np.log(np.arange(1,m))) - (m-1)*np.log(N))/m

def get_meaning_for_tokens(paragraph_dict, document_dict, ratio_doc_par):
    '''
    Gets meaning for tokens according to Helmholtz principle.
    Params:
        paragraph_dict - dictionary with word count for paragraph
        document_dict  - dictionary with word count for document
        ratio_doc_par  - (int) ratio of number of words in document per number of words in paragraph
    Returns:
        mn (dict) - key is token, value is meaning score (Dadachev et al., 2013)
    '''
    return [(w, opt_meaning(paragraph_dict[w], document_dict[w], ratio_doc_par)) for w in paragraph_dict.keys()]

def activity_stretch(sent_list, word_list):
    '''
    Gets activity strech, which is sentences containing given word.
    Params:
        sent_list - list with sentences
        word_list  - list with words (tokens)
    Returns:
        vec_as (dict) - key is token, value list of indices of sentences containing key
    '''
    vec_as = dict()
    for w in word_list:
        vec_as[w] = [e for e, s in enumerate(sent_list) if w in s]
    return vec_as

def make_count_dict(full_list_tokens):
    return Counter(full_list_tokens)

def flat_list(lst):
    return [item for sublist in lst for item in sublist]

def docseg_helmholtz(docsent, window_size = 4):
    '''
    Helmholtz-based document segmentation algorithm.
    Params:
        docsent - list with lists (sentences) of words (tokens)
        window_size = 4 - int with window size
    Returns:
        gap_score (vector) - gap score vector
    '''
    gapscore = np.zeros(len(docsent))
    # dictionary with all words in document and number of occurences
    doc_cnt_dict = make_count_dict(flat_list(docsent))
    Ldoc = len(flat_list(docsent)) # nr of words per document
    Nsent = len(docsent)           # nr of sentences per document 
    rolldocsent =  docsent + docsent[:window_size]
    for i in range(len(gapscore)):
        paragraph = rolldocsent[i:i + window_size]
        par_dict = make_count_dict(flat_list(paragraph))
        vec_meaning = get_meaning_for_tokens(par_dict, doc_cnt_dict, int(Ldoc/len(par_dict)))
        vec_meaningful = [(k,v) for k,v in vec_meaning if v > 0]
        dc_activity = activity_stretch(paragraph, [k for k,v in vec_meaningful])
        dc_meaningful = dict(vec_meaningful)
        for w in dc_activity:
            if len(dc_activity[w]) <= 1:
                continue
            stretch = i + np.arange(dc_activity[w][0], dc_activity[w][-1])
            stretch = [x - Nsent if x >= Nsent -1 else x for x in stretch]
            for gi in stretch: # we add only to scores between first and last occurence
                gapscore[gi+1] += dc_meaningful[w]
    return gapscore

def get_mu_most_similar(lwords, mu_ms, model):
    '''
    Get most similar words based on given model.
    Params:
        lwords  - list with words
        mu_ms   - level of similarity
        model   - embedding model
    Returns:
        msdict (dict) - key is token, value list of most similar words
    '''
    msdict = dict()
    for word in lwords:
        try:
            msdict[word] = [w_.lower() for w_,v_ in model.most_similar(word, topn=kms) if w_.lower != word and not '_' in w_ and v_ > mu_ms]
        except KeyError:
            msdict[word] = []
    return msdict

def get_k_most_similar(lwords, kms, model):
    '''
    Get most similar words based on given model.
    Params:
        lwords - list with words
        kms       - number of most similar
        model     - embedding model
    Returns:
        msdict (dict) - key is token, value list of most similar words
    '''
    msdict = dict()
    for word in lwords:
        try:
            tmplst = []
            for w_, _ in model.most_similar(word, topn=kms):
                wlem = lemmatizer.lemmatize(w_.lower())
                if wlem != word and not '_' in wlem and not wlem in stopwords.words('english'):
                    tmplst.append(wlem)
            msdict[word] = list(set(tmplst))
        except KeyError:
            msdict[word] = []
    return msdict

def make_emb_count_dict(full_list_tokens, most_sim_dc):
    cnt = dict(Counter(full_list_tokens))
    newcnt = dict()
    for k in cnt:
        newcnt[k] = cnt[k]
        similar = most_sim_dc[k]
        for w in similar:
            newcnt[k] += cnt.get(w,0)
    return newcnt

def emb_activity_stretch(sent_list, word_list, most_sim_dc):
    '''
    Embedding activity stretch
    Params:
        sent_list - list with sentences
        word_list - list with words (tokens)
        model     - embedding model
        kms       - number of most similar
    Returns:
        vec_as (dict) - key is token, value list of indices of sentences containing token
                        or *kms* similar to token words
    '''
    vec_as = dict()
    for w in word_list:
        word_and_sim = [w] + most_sim_dc[w]
        vec_as[w] = []
        for ws in word_and_sim:
            vec_as[w].extend([e for e, sent in enumerate(sent_list) if ws in sent])
        vec_as[w] = sorted(list(set(vec_as[w])))
    return vec_as

def remove_similar(mean_words, most_sim_words_dc):
    '''
    To avoid overlapping we remove word which were already counted to not add them twice.
    '''
    copy_mean_words = list(mean_words)
    for w in mean_words:
        if w in copy_mean_words:
            copy_mean_words = [x for x in copy_mean_words if not x in most_sim_words_dc[w]]
    return copy_mean_words

def docseg_emb_helmholtz(docsent, model, kms, window_size = 4):
    '''
    Embedding-Helmholtz-based document segmentation algorithm.
    Params:
        docsent - list with lists (sentences) of words (tokens)
        window_size = 4 - int with window size
        model -
        kms - int
    Returns:
        gap_score (vector) - gap score vector
    '''
    gapscore = np.zeros(len(docsent))
    most_sim_words_dc = get_k_most_similar(list(set(flat_list(docsent))), kms, model)
    # dictionary with all words in document and number of occurences
    doc_cnt_dict = make_emb_count_dict(flat_list(docsent), most_sim_words_dc)
    Ldoc = len(flat_list(docsent)) # nr of words per document
    Nsent = len(docsent)           # nr of sentences per document 
    rolldocsent =  docsent + docsent[:window_size]
    for i in range(len(gapscore)):
        paragraph = rolldocsent[i:i + window_size]
        par_dict = make_emb_count_dict(flat_list(paragraph), most_sim_words_dc)
        vec_meaning = get_meaning_for_tokens(par_dict, doc_cnt_dict, int(Ldoc/len(par_dict)))
        vec_meaningful = [(k,v) for k,v in vec_meaning if v > 0]
        mean_words = [k for k,v in vec_meaningful]
        mean_words = remove_similar(mean_words, most_sim_words_dc)
        dc_activity = emb_activity_stretch(paragraph, mean_words, most_sim_words_dc)
        #dc_activity = activity_stretch(paragraph, [k for k,v in vec_meaningful])
        dc_meaningful = dict(vec_meaningful)
        for w in dc_activity:
            if len(dc_activity[w]) <= 1:
                continue
            stretch = i + np.arange(dc_activity[w][0], dc_activity[w][-1])
            stretch = [x - Nsent if x >= Nsent -1 else x for x in stretch]
            for gi in stretch: # we add only to scores between first and last occurence
                gapscore[gi+1] += dc_meaningful[w]
    return gapscore

class HelmholtzClassifier(object):
    """
    Helmholtz principle based classifier.
    """
    def __init__(self, tags, meaning_threshold = 1.1):
        self. tags = tags
        self.classifiers = dict([(t, None) for t in tags])
        self.meanfulldc = None
        self.meaning_threshold = meaning_threshold

    def meaningfulness(self, text, score_dict, splitter = ' '):
        '''
        Returns meaningfulness.
        Args:
          score_dict (dict) - scores for particular words (key, score) e.g {(cat, 1.1), (frog, 0.4)}
          splitter (str) - how to split text, default: ' '
        Returns:
          numeric value
        '''
        val = 0
        for tok in text.split(splitter):
            if tok in score_dict:
                val += score_dict[tok]
        return val

    def fit(self, X, y):
        '''
        Trains Logistion Regression classifiers using Helmholtz principle features.
        Args:
          *X* (list <str>) - vector of data in textual format
          *y* (list <str>) - list of labels with met or not met condition 
        '''
        texts = X
        annots = y
        tags = self.tags
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
            cont_dc = make_count_dict(longcont[tg])
            vec_meaning = get_meaning_for_tokens(cont_dc, doc_dc, int(Ldoc*1./len(cont_dc)))
            meanfulldc[tg] = dict([(k,v) for k,v in vec_meaning if v > self.meaning_threshold])
        self.meanfulldc = meanfulldc
        # Train LogReg classifiers per each tag
        for tg in tags:
            notmetvec, metvec = [], []
            for tt, aa in zip(texts, annots):
                vm = self.meaningfulness(tt, meanfulldc[tg])
                if aa[tg] == 'met':
                    metvec.append(vm)
                else:
                    notmetvec.append(vm)
            clf = LogisticRegression()
            features = np.array(notmetvec + metvec).reshape(-1, 1)
            clf.fit(features, [0]*len(notmetvec)+[1]*len(metvec))
            self.classifiers[tg] = clf

    def predict(self, text, tag_name):
        """Make prediction based on text for particular tag"""
        if self.meanfulldc is None:
            raise Exception("You need to train me first!")
        helm_score = self.meaningfulness(text, self.meanfulldc[tag_name])
        return self.classifiers[tag_name].predict(helm_score)[0]
