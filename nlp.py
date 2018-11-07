import nltk

# Idea: This is a float from 0..1, if the probability of a given word in a sequence is below this score, then say it is a mistake
difficulty = 0

def format_error(word, chance, message):
	return 'Mistake (%s%% certainty) at word \'%s\': %s' % (chance, word, message)

def set_difficulty(d):
	difficulty = d

def rate_sentence(s):
	tokens = nltk.word_tokenize(s)
	feedback = []
	total = len(tokens)
	correct = total

	# Perform a bunch of checks on sentence, add errors like so
	feedback.append(format_error('he', 0.95, 'Expected possessive pronoun.'))
	feedback.append(format_error('donald', 0.99, 'Expected capitalization at start of sentence.'))

	if not feedback:
		feedback.append('No errors were found!')
	
	# At end, give a final sentence score
	feedback.append('%d / %d words correct' % (correct, total))
	feedback.append('Overall score: %s%%' % (100 * (correct / total)))
	return feedback