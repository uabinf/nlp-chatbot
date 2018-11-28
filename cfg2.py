
def loadGrammar():
    grammar = {'PPER':{'VVFIN':{'ART':{'NN':{'$.'}}, 'APPR':{'ART':{'NN':{'$.'}}}}}, 
               'ART':{'NN':{'VVFIN':{'ADJA':{'$.':{}}, 'ART':{'NN':{'$.':{}}}}}}, 
               'VVFIN':{'PPER':{'ART':{'NN':{'$.':{}}}}}, 
               'NE':{'VVFIN':{'ART':{'NN':{'$.':{}}},'APPRART':{'NN':{'$.'}}, 'NN':{'$.':{}}}}}
    return grammar

def checkSyntax(sentences, checker, grammar, counter):
    decision = ''
    for word in sentences:
        if word == sentences[0]:
            if word[1] in grammar.keys():
                checker.append('Grammatical')
                sentences.remove(sentences[0])
                grammar = grammar[word[1]]
                counter += 1
                checkSyntax(sentences, checker, grammar, counter)
            else:
                checker.append('Ungrammatical')
                print("Incorrect POS at Position", counter)
                print("Expected POS Tags => ")
                for key in grammar.keys():
                    print(key)
                break
        if 'Ungrammatical' in checker:
            decision = "Ungrammatical Sentence"
        else:
            decision = 'Grammatical Sentence'
    return decision
         
#sentence = [(('Dies', ''), 'NE'), (('ist', ''), 'VVFIN'), (('ein', ''), 'ART'), (('Test', ''), 'NN'), (('.', ''), '$.')]
#checkSyntax(sentence, [], grammar, 0)
