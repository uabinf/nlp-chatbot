import nltk, os.path, pickle, re, requests, sys, tarfile

# Global settings
tagger = None
difficulty = 0

# 
determiners = ('das', 'dem', 'den', 'der', 'des', 'die', 'ein', 'eine', 'einem', 'einer')
pronouns = ('deiner', 'dich', 'dir', 'du', 'er', 'es', 'euch', 'euer', 'ich', 'ihm', 'ihn', 'ihnen', 'ihr', 'ihrer', 'meiner', 'mich', 'mir', 'seiner', 'sie', 'uns', 'unser', 'wir')
prepositions = ('bis', 'durch', 'für', 'gegen', 'ohne', 'um', 'wider', 'aus','ausser', 'außer', 'bei', 'mit', 'nach', 'seit', 'von', 'zu', 'ab', 'während', 'trotz', 'statt', 'anstatt', 
		'außerhalb', 'wegen', 'innerhalb', 'jenseits', 'diesseits', 'an', 'hinter', 'neben', 'über', 'unter', 'vor', 'zwischen', 'entlang')
conjunctions = ('aber', 'beziehungsweise', 'denn', 'oder', 'sondern', 'und', 'als', 'bevor', 'bis', 'dass', 'damit', 'nachdem', 'ob', 'obwohl', 'seit', 'seitdem', 'sobald', 'sofern', 'soweit'
	       'sowie', 'während', 'weil', 'wenn', 'wie', 'wo')
regex_digit = re.compile('\d')
regex_punct = re.compile('[^\w\d]')

def set_difficulty(d):
	difficulty = d

def download_corpus():
	if not os.path.isfile('tiger_release_aug07.corrected.16012013.conll09'):
		print('Downloading TIGER corpus...')
		url = 'http://www.ims.uni-stuttgart.de/forschung/ressourcen/korpora/TIGERCorpus/download/tigercorpus-2.2.conll09.tar.gz'
		r = requests.get(url, allow_redirects=True)

		with open('tigercorpus-2.2.conll09.tar.gz', 'wb') as corpus:
			corpus.write(r.content)

		print('Extracting TIGER corpus...')
		with tarfile.open('tigercorpus-2.2.conll09.tar.gz', 'r:gz') as tarref:
			tarref.extractall('.')

def word_features(sent, i):
	features = {}
	features['num_terms'] = len(sent)

	# Add each term inside window to features
	window = 1
	start = max(i - window, 0)
	end = min(i + window, len(sent) - 1)
	for w in range(start, end + 1):
		word = sent[w][0]
		wr = w - i

		# General features
		features['%+d:is_first' % wr] = w == 0
		features['%+d:is_last' % wr] = w == len(sent) - 1
		features['%+d:is_title' % wr] = word.istitle()
		features['%+d:all_caps' % wr] = word.isupper()
		features['%+d:all_lower' % wr] = word.islower()
		
		# POS-specific features
		features['%+d:determiner' % wr] = word.lower() in determiners
		features['%+d:pronoun' % wr] = word.lower() in pronouns
		features['%+d:digit' % wr] = bool(regex_digit.match(word))
		features['%+d:punct' % wr] = bool(regex_punct.match(word))
	return features

def get_featureset(dataset):
	featureset = []
	for sent in dataset:
		for i in range(0, len(sent)):
			featureset.append((word_features(sent, i), sent[i][1]))
	return featureset

def sent_features(sent):
	return [word_features(sent, i) for i in range(len(sent))]


def get_tagset(dataset):
	tagset = set()
	for sent in dataset:
		for word in sent:
			tagset.add(word[1])
	return tagset

def test_tagger(features):
	global tagger

	# Split into 90:10 training and testing corpus
	cutoff = int(len(features) * 0.1)
	trainset, testset = features[cutoff:], features[:cutoff]

	# Train tagger and perform cross-fold validation
	folds = 1
	size = int(len(trainset) / folds)
	accuracy = []
	print('Performing %d-fold validation on tagger...' % folds)
	for i in range(folds):
		start = i * size
		end = (i + 1) * size

		subtrain = trainset[0:start] + trainset[end:-1]
		subtest = testset[start:end]

		tagger = nltk.classify.NaiveBayesClassifier.train(trainset)
		accuracy.append(nltk.classify.accuracy(tagger, testset) * 100)
	print('Average classification accuracy:', sum(accuracy) / folds)

def init_tagger():
	global tagger

	if not tagger:
		if not os.path.isfile('tagger.pickle'):
			# Download and retrieve corpus sentences
			download_corpus()
			print('Reading corpus sentences...')
			corpus = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09', ['ignore', 'words', 'ignore', 'ignore', 'pos'], encoding='utf-8')

			# Train tagger on corpus
			dataset = corpus.tagged_sents()
			features = get_featureset(dataset)
			tagger = nltk.classify.NaiveBayesClassifier.train(features)

			# Pickle tagger to prevent retraining during each startup
			print('Storing tagger for reuse...')
			with open('tagger.pickle', 'wb') as tagfile:
				pickle.dump(tagger, tagfile, protocol=pickle.HIGHEST_PROTOCOL)
		else:
			# Load previously-trained tagger from file
			print('Loading previously-trained tagger...')
			with open('tagger.pickle', 'rb') as tagfile:
				tagger = pickle.load(tagfile)				

def format_error(word, chance, message):
	return 'Mistake (%s%% certainty) at word \'%s\': %s' % (chance, word, message)

def tag_sentence(tokens):
	# Append empty POS to each word in sentence, classify word-by-word
	tokens = [(tokens[i], '') for i in range(len(tokens))]
	featureset = sent_features(tokens)
	tags = [(tokens[i], tagger.classify(featureset[i])) for i in range(len(featureset))]
	print(tags)
	return tags

def rate_sentence(s):
	global tagger

	# Initialize tagger, get sentence tokens
	init_tagger()
	tokens = nltk.word_tokenize(s)
	tags = tag_sentence(tokens)
	feedback = []
	total = len(tokens)
	correct = total

	# Perform a bunch of checks on sentence, add errors like so
	# feedback.append(format_error('he', 0.95, 'Expected possessive pronoun.'))
	# feedback.append(format_error('donald', 0.99, 'Expected capitalization at start of sentence.'))

	if not feedback:
		feedback.append('No errors were found!')
	
	# At end, give a final sentence score
	feedback.append('%d / %d words correct' % (correct, total))
	feedback.append('Overall score: %s%%' % (100 * (correct / total)))
	return feedback
