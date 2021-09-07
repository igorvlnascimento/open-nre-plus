import json
from ast import literal_eval

import pandas as pd

import stanza
import spacy

class ConverterDataset():
    
    def __init__(self, dataset_name, entity_name="ENTITY", nlp_model="stanza"):
        
        self.dataset_name = dataset_name
        self.entity_name = entity_name
        
        #self.write_relations_json()
        
        if nlp_model == "stanza":
            stanza.download('en')
            self.nlp = stanza.Pipeline(lang='en', processors="tokenize,ner", tokenize_no_ssplit=True)
        elif nlp_model == "spacy":
            self.nlp = spacy.load('en_core_web_lg')
        

    def write_relations_json(self, path):
        json_file = open(path+'/' + self.dataset_name + '_rel2id.json', 'w')
        json.dump(self.relation_dict, json_file)

    def tokenize(self, sentence, model="spacy"):
        if model == "spacy":
            doc = self.nlp(sentence)
            tokenized = []
            for token in doc:
                tokenized.append(token.text)
            return tokenized
        elif model == "stanza":
            doc = self.nlp(sentence)
            tokenized = [token.text for sent in doc.sentences for token in sent.tokens]
            return tokenized

    # remove any additional whitespace within a line
    def remove_whitespace(self, line):
        return str(" ".join(line.split()).strip())

    # We will replace e1 by DRUG, e2 by OTHERDRUG, common between e1 and e2 as EITHERDRUG and other drugs as 
    # UNRELATEDDRUG (TODO: edit this)
    def tag_sentence(self, sentence, e1_data, e2_data, other_entities):
        position_dict = self.create_positions_dict(e1_data, e2_data, other_entities)
        sorted_positions = self.sort_position_keys(position_dict)
        new_sentence = ''
        # TODO (geeticka): check for cases when previous ending position and next starting position 
        # are equal or next to each other. Add a space in that case
        # we are inserting a starter and ender tag around the drugs
        for i in range(len(sorted_positions)):
            curr_pos = sorted_positions[i]
            curr_start_pos, curr_end_pos = self.parse_position(curr_pos)
            if i == 0:
                new_sentence += sentence[:curr_start_pos] + ' ' + position_dict[curr_pos]['start'] + ' ' + \
                        sentence[curr_start_pos: curr_end_pos+1] + ' ' + position_dict[curr_pos]['end'] + ' '
            else:
                prev_pos = sorted_positions[i-1]
                _, prev_end_pos = self.parse_position(prev_pos)
                middle = sentence[prev_end_pos+1 : curr_start_pos]
                if middle == '':
                    middle = ' '
                new_sentence += middle + ' ' + position_dict[curr_pos]['start'] + ' ' + \
                        sentence[curr_start_pos: curr_end_pos+1] + ' ' + position_dict[curr_pos]['end'] + ' '
                if i == len(sorted_positions) - 1 and curr_end_pos < len(sentence) - 1:
                    new_sentence += ' ' + sentence[curr_end_pos+1:]
        new_sentence = self.remove_whitespace(new_sentence)
        
        return new_sentence

    # get the start and end of the entities 
    def get_entity_start_and_end(self, entity_start, entity_end, tokens):
        pass

    # given the entity starting and ending word index, and entity replacement dictionary, 
    # update the dictionary to inform of the replace_by string for eg ENTITY
    def get_entity_replacement_dictionary(self, e_idx, entity_replacement, replace_by):
        key = str(e_idx[0]) + ":" + str(e_idx[1])
        entity_replacement[key] = replace_by
        return entity_replacement

    # TODO: need to edit this 
    def get_dataset_dataframe(self, directory=None, relation_extraction=True):
        '''
        If relation_extraction is True, then we don't care whether the ddi flag is true or false
        '''
        pass


    # to streamline the writing of the dataframe
    def write_dataframe(self, df, directory):
        df.to_csv(directory, sep='\t', encoding='utf-8', index=False)

    # to streamline the reading of the dataframe
    def read_dataframe(self, directory):
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
    def check_equality_of_written_and_read_df(self, df, df_copy):
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

    # write the dataframe into the text format accepted by the cnn model
    def write_into_txt(self, df, directory):
        pass