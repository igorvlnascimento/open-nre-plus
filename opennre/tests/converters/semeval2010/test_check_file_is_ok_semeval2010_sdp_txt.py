import os
    
def test_should_pass_checking_the_sdp_semeval2010_files_test_dataset_is_not_empty():
    assert open("benchmark/semeval2010/original/semeval2010_test_original.txt", 'r').readlines()[0] == "{'token': ['the', 'most', 'common', 'audits', 'were', 'about', 'waste', 'and', 'recycling', '.'], 'h': {'name': 'audits', 'pos': [3, 4]}, 't': {'name': 'waste', 'pos': [6, 7]}, 'pos': ['DET', 'ADV', 'ADJ', 'NOUN', 'AUX', 'ADP', 'NOUN', 'CCONJ', 'NOUN', 'PUNCT'], 'deps': ['det', 'advmod', 'amod', 'nsubj', 'root', 'prep', 'compound', 'cc', 'conj', 'punct'], 'ner': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], 'sdp': ['audits', 'were', 'about', 'waste'], 'relation': 'Message-Topic(e1,e2)'}\n"

def test_should_pass_checking_the_sdp_semeval2010_files_val_dataset_is_not_empty():
    assert open("benchmark/semeval2010/original/semeval2010_val_original.txt").readlines()[0] == "{'token': ['the', 'inhabitants', 'send', 'messages', 'to', 'each', 'other', 'by', 'placing', 'the', 'message', 'in', 'a', 'capsule', 'and', 'placing', 'the', 'capsule', 'in', 'a', 'message', 'tube', '.'], 'h': {'name': 'message', 'pos': [10, 11]}, 't': {'name': 'capsule', 'pos': [13, 14]}, 'pos': ['DET', 'NOUN', 'VERB', 'NOUN', 'ADP', 'DET', 'ADJ', 'ADP', 'VERB', 'DET', 'NOUN', 'ADP', 'DET', 'NOUN', 'CCONJ', 'VERB', 'DET', 'NOUN', 'ADP', 'DET', 'NOUN', 'NOUN', 'PUNCT'], 'deps': ['det', 'nsubj', 'root', 'dobj', 'dative', 'det', 'pobj', 'prep', 'pcomp', 'det', 'dobj', 'prep', 'det', 'pobj', 'cc', 'conj', 'det', 'dobj', 'prep', 'det', 'compound', 'pobj', 'punct'], 'ner': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], 'sdp': ['message', 'placing', 'capsule'], 'relation': 'Entity-Destination(e1,e2)'}\n"
    
def test_should_pass_checking_the_sdp_semeval2010_files_train_dataset_is_not_empty():
    assert open("benchmark/semeval2010/original/semeval2010_train_original.txt", 'r').readlines()[0] == "{'token': ['the', 'system', 'as', 'described', 'above', 'has', 'its', 'greatest', 'application', 'in', 'an', 'arrayed', 'configuration', 'of', 'antenna', 'elements', '.'], 'h': {'name': 'configuration', 'pos': [12, 13]}, 't': {'name': 'elements', 'pos': [15, 16]}, 'pos': ['DET', 'NOUN', 'SCONJ', 'VERB', 'ADV', 'VERB', 'PRON', 'ADJ', 'NOUN', 'ADP', 'DET', 'VERB', 'NOUN', 'ADP', 'NOUN', 'NOUN', 'PUNCT'], 'deps': ['det', 'nsubj', 'mark', 'relcl', 'advmod', 'root', 'poss', 'amod', 'dobj', 'prep', 'det', 'amod', 'pobj', 'prep', 'compound', 'pobj', 'punct'], 'ner': ['O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'], 'sdp': ['configuration', 'of', 'elements'], 'relation': 'Component-Whole(e2,e1)'}\n"