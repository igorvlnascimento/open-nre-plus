"""
    Author: Geeticka Chauhan
    Based upon the code: https://github.com/sunilitggu/DDI-extraction-through-LSTM/blob/master/process2.py
"""
import glob
from pyexpat import ExpatError
from typing import Text
from xml.dom import minidom
import json
from ast import literal_eval

import pandas as pd
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from tqdm import tqdm

relation_dict = {0: 'usage', 1: 'result', 2: 'model-feature', 3: 'part_whole', 4: 'topic', 5: 'compare'}
rev_relation_dict = {val: key for key, val in relation_dict.items()}

def write_relations_json(path):
    json_file = open(path+'/semeval2018_rel2id.json', 'w')
    json.dump(rev_relation_dict, json_file)

def tokenize(nlp, sentence, model="spacy"):
    if model == "spacy":
        doc = nlp(sentence)
        tokenized = []
        for token in doc:
            tokenized.append(token.text)
        return tokenized
    elif model == "stanza":
        doc = nlp(sentence)
        tokenized = [token.text for sent in doc.sentences for token in sent.tokens]
        return tokenized

# given sentence dom in DDI corpus, get all the information related to the entities 
# present in the dom
def get_entity_dict(sentence):
    if '<abstract>' in sentence:
        abstract_start = sentence.find('<abstract>')
        abstract_end = sentence.find('</abstract>')
        sentence = sentence[abstract_start:abstract_end]
        
        sentence = sentence[sentence.find('>')+1:]
        
        
    if '<title>' in sentence:
        title_start = sentence.find('<title>')
        title_end = sentence.find('</title>')
        sentence = sentence[title_start:title_end]
        
        sentence = sentence[sentence.find('>')+1:]
    #print("sentence:",sentence)
    entity_dict = {}
    while sentence.find('<entity') != -1:
        entity_start = sentence.find("<entity")
        entity_end = sentence.find("</entity>")
        id_end = sentence.find('>')
        entity_id = sentence[entity_start+12:id_end-1]
        
        entity_name = sentence[id_end+1:entity_end]
        #print("entity_name:",entity_name)
        
        #if entity_id not in pairs:
        sentence = sentence[:entity_start] + sentence[id_end+1:]
        charOffset = ["{}-{}".format(len(sentence[:entity_start]), len(sentence[:entity_start])+len(entity_name)-1)]
        #print("charOffset:",charOffset)
        entity_end = sentence.find("</entity>")
        sentence = sentence[:entity_end] + sentence[entity_end+9:]
        print("sentence:",sentence)
        if '<entity' in sentence[:entity_end]:
            break
        #print("sentence2:",sentence)
        #print("entity_id:",entity_id)
        entity_dict[entity_id] = {'id': entity_id, 'word': entity_name, 'charOffset':charOffset}
    # entities = sentence_dom.getElementsByTagName('entity')
    # entity_dict = {}
    # for entity in entities:
    #     id = entity.getAttribute('id')
    #     word = entity.childNodes[0].data
        #if id in pairs:
    #     #type = entity.getAttribute('type')
    #     #charOffset = entity.getAttribute('charOffset')
    #     #charOffset = charOffset.split(';') # charOffset can either be length 1 or 2 
    #     # because we have cases like loop, potassium-sparing diuretics
    #     # where loop diuretics and potassium-sparing diuretics is the entity
    #     entity_dict[id] = {'id': id, 'word': word}
    return entity_dict, sentence


def get_pairs(entity_dict, entity_pairs):
    pairs = []
    entity_list = [key for key in entity_dict]
    for entity in entity_list:
        if entity in entity_pairs:
            pairs.append((entity_pairs[entity]['relation'], entity, entity_pairs[entity]['e2']))
    return pairs

# given the metadata, get the individual positions in the sentence and know what to replace them by
def create_positions_dict(e1, e2, other_entities):
    position_dict = {}
    #common_position_e1_e2 = list(set(e1['charOffset']).intersection(e2['charOffset']))
    #if common_position_e1_e2: # there are commonalities between e1 and e2
    #    for pos in common_position_e1_e2:
    #        position_dict[pos] = {'start': 'DRUGEITHERSTART', 'end': 'DRUGEITHEREND'}
    for pos in e1['charOffset']:
        if pos not in position_dict:
            position_dict[pos] = {'start': 'ENTITYSTART', 'end': 'ENTITYEND'}
    for pos in e2['charOffset']:
        if pos not in position_dict:
            position_dict[pos] = {'start': 'ENTITYOTHERSTART', 'end': 'ENTITYOTHEREND'}
    for other_ent in other_entities:
        for pos in other_ent['charOffset']:
            if pos not in position_dict:
                position_dict[pos] = {'start': 'ENTITYUNRELATEDSTART', 'end': 'ENTITYUNRELATEDEND'}
    return position_dict

#given string 12-30, return 12, 30 as a tuple of ints
def parse_position(position):
    positions = position.split('-')
    return int(positions[0]), int(positions[1])
    #if metadata['e1']['charOffset'] and metadata['e2']['charOffset'] have something in common

# given position dictionary, sort the positions from ascending order. Assumes no overlap. 
# will be messed up if there is overlap
# can also check for overlap but not right now
def sort_position_keys(position_dict):
    positions = list(position_dict.keys())
    sorted_positions = sorted(positions, key=lambda x: int(x.split('-')[0]))
    return sorted_positions

# remove any additional whitespace within a line
def remove_whitespace(line):
    return str(" ".join(line.split()).strip())

# We will replace e1 by DRUG, e2 by OTHERDRUG, common between e1 and e2 as EITHERDRUG and other drugs as 
# UNRELATEDDRUG (TODO: edit this)
def tag_sentence(sentence, e1_data, e2_data, other_entities):
    position_dict = create_positions_dict(e1_data, e2_data, other_entities)
    #print("position_dict:",position_dict)
    sorted_positions = sort_position_keys(position_dict)
    new_sentence = ''
    # TODO (geeticka): check for cases when previous ending position and next starting position 
    # are equal or next to each other. Add a space in that case
    # we are inserting a starter and ender tag around the drugs
    for i in range(len(sorted_positions)):
        curr_pos = sorted_positions[i]
        curr_start_pos, curr_end_pos = parse_position(curr_pos)
        if i == 0:
            new_sentence += sentence[:curr_start_pos] + ' ' + position_dict[curr_pos]['start'] + ' ' + \
                    sentence[curr_start_pos: curr_end_pos+1] + ' ' + position_dict[curr_pos]['end'] + ' '
        else:
            prev_pos = sorted_positions[i-1]
            _, prev_end_pos = parse_position(prev_pos)
            middle = sentence[prev_end_pos+1 : curr_start_pos]
            if middle == '':
                middle = ' '
            new_sentence += middle + ' ' + position_dict[curr_pos]['start'] + ' ' + \
                    sentence[curr_start_pos: curr_end_pos+1] + ' ' + position_dict[curr_pos]['end'] + ' '
            if i == len(sorted_positions) - 1 and curr_end_pos < len(sentence) - 1:
                new_sentence += ' ' + sentence[curr_end_pos+1:]
    new_sentence = remove_whitespace(new_sentence)
    
    return new_sentence

# return the entities in the sentence except those in the pair
def get_other_entities(entity_dict, e1, e2):
    blacklisted_set = [e1, e2]
    return [value for key, value in entity_dict.items() if key not in blacklisted_set]

# get the start and end of the entities 
def get_entity_start_and_end(entity_start, entity_end, tokens):
    e_start = tokens.index(entity_start)
    e_end = tokens.index(entity_end) - 2 # because 2 tags will be eliminated
    # only eliminate the entity_start and entity_end once because DRUGUNRELATEDSTART will get
    # eliminated many times
    new_tokens = []
    entity_start_seen = 0
    entity_end_seen = 0
    for x in tokens:
        if x == entity_start:
            entity_start_seen += 1
        if x == entity_end:
            entity_end_seen += 1
        if x == entity_start and entity_start_seen == 1:
            continue
        if x == entity_end and entity_end_seen == 1:
            continue
        new_tokens.append(x)
    return (e_start, e_end), new_tokens

# given the entity starting and ending word index, and entity replacement dictionary, 
# update the dictionary to inform of the replace_by string for eg ENTITY
def get_entity_replacement_dictionary(e_idx, entity_replacement, replace_by):
    key = str(e_idx[0]) + ":" + str(e_idx[1])
    entity_replacement[key] = replace_by
    return entity_replacement

# from the tokenized sentence which contains the drug tags, extract the word positions
# and replacement dictionary for blinding purposes
def get_entity_positions_and_replacement_dictionary(tokens):
    entity_replacement = {}
    e1_idx = []
    e2_idx = []

    tokens_for_indexing = tokens
    for token in tokens:
        if token.startswith('ENTITY') and token.endswith('START'):
            ending_token = token[:-5] + 'END'
            e_idx, tokens_for_indexing = get_entity_start_and_end(token, ending_token, tokens_for_indexing)

            replace_by = token[:-5]
            entity_replacement = get_entity_replacement_dictionary(e_idx, entity_replacement, replace_by)
            if token == 'ENTITYSTART' or token == 'ENTITYEITHERSTART':
                e1_idx.append(e_idx)
            if token == 'ENTITYOTHERSTART' or token == 'ENTITYEITHERSTART':
                e2_idx.append(e_idx)
    return e1_idx, e2_idx, entity_replacement, tokens_for_indexing

# TODO: need to edit this 
def get_dataset_dataframe(nlp, directory=None, relation_extraction=True):
    '''
    If relation_extraction is True, then we don't care whether the ddi flag is true or false
    '''
    
    punk_param = PunktParameters()
    abbreviations = ['e.g', 'viz', 'al']
    punk_param.abbrev_types = set(abbreviations)
    tokenizer = PunktSentenceTokenizer(punk_param)
    
    relation_files_to_read = glob.glob(directory + '*.txt')
    entity_pairs = {}
    for file_name in relation_files_to_read:
        lines = open(file_name).readlines()
        for line in lines:
            type = line[:line.find('(')]
            if 'REVERSE' in line:
                e2_id = line[line.find('(')+1:line.find(',')]
                e1_id = line[line.find(',')+1:line.find(',REVERSE)')]
                entity_pairs[e1_id] = {'relation':type, 'e2':e2_id}
            else:
                e1_id = line[line.find('(')+1:line.find(',')]
                e2_id = line[line.find(',')+1:line.find(')')]
                entity_pairs[e1_id] = {'relation':type, 'e2':e2_id}
    
    data = []
    total_files_to_read = glob.glob(directory + '*.xml')
    print('total_files_to_read:' , len(total_files_to_read) , ' from dir: ' , directory)
    for file in tqdm(total_files_to_read):
        lines = open(file).readlines()
        for line in lines:
            print("line:",line)
            if '</entity>' in line:
                sentences = tokenizer.tokenize(line)
                #print("sentences:",sentences)
                for sentence in sentences:
                    entity_dict, sentence = get_entity_dict(sentence)
                    
                    pairs = get_pairs(entity_dict,entity_pairs)
                    
                    print("entity_dict:",entity_dict)
                    print("sentence:",sentence)
                    print("pairs:",pairs)
                    
                    # pegar lista de pares de entidade e relação e verificar se há pares nas sentenças

                    for pair in pairs:
                        #pair_id = pair.getAttribute('id')
                        #ddi_flag = pair.getAttribute('ddi')
                        e1_id = pair[1]
                        e2_id = pair[2]
                        
                        other_entities = get_other_entities(entity_dict, e1_id, e2_id)
                        
                        try:
                            e1_data = entity_dict[e1_id]
                            e2_data = entity_dict[e2_id]
                        except KeyError:
                            # TODO: tratar os coreference resolution
                            continue
                        
                        tagged_sentence = tag_sentence(sentence, e1_data, e2_data, other_entities)
                        tokens = tokenize(nlp, tagged_sentence, model="stanza")

                        e1_idx, e2_idx, entity_replacement, tokens_for_indexing = \
                                get_entity_positions_and_replacement_dictionary(tokens)
                        # TODO (geeticka): for unifying purposes, can remove the e1_id and e2_id
                        metadata = {'e1': {'word': e1_data['word'], 'word_index': e1_idx, 'id': e1_id},
                                    'e2': {'word': e2_data['word'], 'word_index': e2_idx, 'id': e2_id},
                                    'entity_replacement': entity_replacement}
                        tokenized_sentence = " ".join(tokens_for_indexing)

                        relation_type = pair[0].lower()
                        if not not relation_type: # not of empty string is True, but we don't want to append
                            data.append([str(sentence), str(e1_data['word']), str(e2_data['word']),
                                str(relation_type), metadata, str(tokenized_sentence)])

    df = pd.DataFrame(data,
            columns='original_sentence,e1,e2,relation_type,metadata,tokenized_sentence'.split(','))
    return df


# to streamline the writing of the dataframe
def write_dataframe(df, directory):
    df.to_csv(directory, sep='\t', encoding='utf-8', index=False)

# to streamline the reading of the dataframe
def read_dataframe(directory):
    df = pd.read_csv(directory, sep='\t')
    def literal_eval_metadata(row):
        metadata = row.metadata
        metadata = literal_eval(metadata)
        return metadata
    df['metadata'] = df.apply(literal_eval_metadata, axis=1)
    # metadata is a dictionary which is written into the csv format as a string
    # but in order to be treated as a dictionary it needs to be evaluated
    return df

# The goal here is to make sure that the df that is written into memory is the same one that is read
def check_equality_of_written_and_read_df(df, df_copy):
    bool_equality = df.equals(df_copy)
    # to double check, we want to check with every column
    bool_every_column = True
    for idx in range(len(df)):
        row1 = df.iloc[idx]
        row2 = df_copy.iloc[idx]
        if row1['original_sentence'] != row2['original_sentence'] or row1['e1'] != row2['e1'] or \
                row1['relation_type'] != row2['relation_type'] or \
                row1['tokenized_sentence'] != row2['tokenized_sentence'] or \
                row1['metadata'] != row2['metadata']: 
                    bool_every_column = False
                    break
    return bool_equality, bool_every_column

# suggested in
# https://stackoverflow.com/questions/10632839/transform-list-of-tuples-into-a-flat-list-or-a-matrix
def flatten_list_of_tuples(a):
    return list(sum(a, ()))

# write the dataframe into the text format accepted by the cnn model
def write_into_txt(df, directory):
    print("Unique relations: \t", df['relation_type'].unique())
    null_row = df[df["relation_type"].isnull()]
    if null_row.empty:
        idx_null_row = None
    else:
        idx_null_row = null_row.index.values[0]
    with open(directory, 'w') as outfile:
        for i in tqdm(range(0, len(df))):
            dict = {}
            head = {}
            tail = {}
            if idx_null_row is not None and i == idx_null_row:
                continue
            row = df.iloc[i]
            relation = rev_relation_dict[row.relation_type]
            metadata = row.metadata
# TODO: need to change below in order to contain a sorted list of the positions
# metadata['e1']['word_index'] returns a list of tuples
            e1 = flatten_list_of_tuples(metadata['e1']['word_index'])
            e2 = flatten_list_of_tuples(metadata['e2']['word_index'])
            e1 = sorted(e1)
            e2 = sorted(e2)
            head["name"] = metadata['e1']['word']
            head["pos"] = [e1[0], e1[1]+1]
            tail["name"] = metadata['e2']['word']
            tail["pos"] = [e2[0], e2[1]+1]
            try:
                tokenized_sentence = row.tokenized_sentence
            except AttributeError:
                tokenized_sentence = row.preprocessed_sentence
            if type(tokenized_sentence) is not str:
                continue
            tokenized_sentence = tokenized_sentence.split(" ")
            dict["token"] = tokenized_sentence
            dict["h"] = head
            dict["t"] = tail
            dict["relation"] = row.relation_type
            outfile.write(str(dict)+"\n")
            #outfile.write(str(relation) + " " + str(e1[0]) + " " + str(e1[-1]) + " " + 
            #              str(e2[0]) + " " + str(e2[-1]) + " " + tokenized_sentence + "\n")
        outfile.close()

# combine txt files of drugbank and medline
def combine(res, outdir, file1, file2, outfilename):
    outfile = outdir + outfilename
    filenames = [res(outdir + file1+'.txt'), res(outdir + file2+'.txt')]
    with open(res(outfile), 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)