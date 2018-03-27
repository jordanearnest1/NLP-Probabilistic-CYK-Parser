import sys
import math
# from math import log
import numpy as np
from nltk.tree import *


def load_grammar(filename):
    '''
    load grammar that following CNF
    return a dict = {(A, (B, C)): prob, (A, a): prob}
    A, B and C represent non-terminal rules and a is lexicon
    prob is normalized probability
    '''

    gram_prob_dict = {}
    pos_dict = {}

    grammar_file = open(filename, 'r').readlines() 
    for elem in grammar_file: 
        text_lst = elem.split() 
        if len(text_lst) == 4: 
            gram_prob_dict[(text_lst[1],(text_lst[2], text_lst[3]))] = int(text_lst[0]) 
            pos_dict[text_lst[1]] = pos_dict.get(text_lst[1], 0) + 1   
        elif len(text_lst) == 3: 
            gram_prob_dict[tuple(text_lst[1:])] = int(text_lst[0])
            pos_dict[text_lst[1]] = pos_dict.get(text_lst[1], 0) + 1

    for gram_key in gram_prob_dict.keys():  
        for pos_key in pos_dict.keys():  
            if gram_key[0] == pos_key:
                gram_prob_dict[gram_key] = np.log(gram_prob_dict[gram_key]/pos_dict[pos_key])
    return gram_prob_dict
run_grammar = load_grammar('example.gr')



def parse(words, grammar):
    invalidParse = False
    sentenceLen = len(words)

    score = [[{} for i in range(sentenceLen+1)] for j in range(sentenceLen)]  

    backpointer = [[{} for i in range(sentenceLen+1)] for j in range(sentenceLen)]

    terminal_lst = []
    nonterminal_lst = []

    for key in grammar.keys():
        if type(key[1]) == tuple:
            nonterminal_lst.append(key)
        elif type(key[1]) != tuple:
            terminal_lst.append(key)

    for i, word in enumerate(words): 
        for key in grammar.keys():
            if word == key[1]:
                score[i][i+1][key[0]] = math.exp(grammar[key])
                # print(grammar[key])


    for span in range(2, sentenceLen + 1):
        for start in range(0, sentenceLen - span + 1):
            end = start + span 
            for split in range(start + 1, end): 
                for A,B in nonterminal_lst: 
                    if B[0] in score[start][split] and B[1] in score[split][end]: 
                        prob1 = score[start][split][B[0]]
                        # prob1 = math.log(prob1)
                        prob2 = score[split][end][B[1]]
                        prob3 = (prob1) + (prob2) + (grammar[(A,B)])
                        if A in score[start][end]:
                            if prob3 > score[start][end][A]:
                                score[start][end][A] = prob3
                                backpointer[start][end][A] = (split, B[0], B[1])   
                        else:
                            score[start][end][A] = prob3
                            backpointer[start][end][A] = (split, B[0], B[1])
    maxScore = 0
    if len(score[0][-1]) == 0:
        invalidParse = True

    for k,v in score[0][-1].items():
        maxScore = v
        # print(maxScore)
    return invalidParse, maxScore, backpointer
    


#... A => B,C, arr1 is for B and arr2 is for C
def addBranch(words, backpointer, arr1, arr2):

    [start1, end1, symb1] = arr1
    [start2, end2, symb2] = arr2

    # for first non-terminal/terminal
    if (end1-start1==1):
        tree1 = Tree(symb1,[words[start1]])
    else:
        B = backpointer[start1][end1][symb1]

        
        split, R1,R2 = B
        split1a = [start1, split]
        split1b = [split, end1]

        tree1 = Tree(symb1, addBranch(words, backpointer, [start1, split, R1], [split, end1, R2]))


    # for second non-terminal/terminal
    if (end2-start2==1):
        tree2 = Tree(symb2,[words[start2]])
    else:
        C = backpointer[start2][end2][symb2]
        split, R1,R2 = C
        split1a = [start2, split]
        split1b = [split, end2]

        tree2 = Tree(symb2, addBranch(words, backpointer, [start2, split, R1], [split, end2, R2]))

    return [tree1, tree2]





def pretty_print(words, backpointer):

    #... start at the root of the tree
    foundRoot = False
    sentLen = len(backpointer)
    for key,value in backpointer[0][-1].items():
        if key=="S": #... this is the root, REQUIRED symbol
            foundRoot = True
            split, B,C = value 
            tree = Tree(key, addBranch(words, backpointer, [0,split,B], [split,sentLen,C]))
            break


    if foundRoot:
        tree.pretty_print()
    else:
        #... This grammar could not match the provided sentence.
        print ("Cannot find root")
        return

    return tree



def main():
    if len(sys.argv) != 4:
        print(('Wrong number of arguments?: %d\nExpected python parser.py ' +
               'grammar.gr lexicon.txt sentences.txt') % (len(sys.argv)-1))
        exit(1)
    
    grammar_file = sys.argv[1]
    lexicon_file = sys.argv[2]
    sentences_file = sys.argv[3]
    
    
    #... we're assuming that lexicon.txt is line-separated with each line containing
    #... exactly one token that is permissible. The rules for these tokens is contained
    #... in grammar.gr
    lexicon = set()
    with open(lexicon_file) as f:
        for line in f:
            lexicon.add(line.strip())
    print("Saw %d terminal symbols in the lexicon" % (len(lexicon)))


    grammar = load_grammar(grammar_file)


    # non_terminals = get_non_terminals(grammar, lexicon)

    with open(sentences_file) as f:
        for line in f:
            words = line.strip().split()
            invalidParse, score, backpointer = parse(words, grammar)
            if invalidParse:
                print ("Grammar couldn't parse this sentence")
            else:
                print('%f\t%s' % (score, pretty_print(words,backpointer)))

   
if __name__ == '__main__':
    main()