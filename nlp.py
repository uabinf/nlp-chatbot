import nltk, os.path, requests, sys, tarfile

tagger = None
difficulty = 0

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
		features['%+d:digit' % wr] = bool(regex_digit.match(word))
		features['%+d:punct' % wr] = bool(regex_punct.match(word))
		
	return features

def init_tagger():
	if not tagger:
		download_corpus()
		print('Reading corpus sentences...')
		corpus = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09', ['ignore', 'words', 'ignore', 'ignore', 'pos'], encoding='utf-8')
		tagged_sents = corpus.tagged_sents()

		# Split into 90:10 training and testing corpus
		cutoff = int(len(tagged_sents) * 0.1)
		trainset, testset = tagged_sents[cutoff:], tagged_sents[:cutoff]

		# Retrieve tagset
		print('Extracting tagset...')
		tags = set()
		for sent in tagged_sents:
			for word in sent:
				tags.add(word[1])
		print(tags)

		# Train tagger
		# ...

def format_error(word, chance, message):
	return 'Mistake (%s%% certainty) at word \'%s\': %s' % (chance, word, message)

def rate_sentence(s):
	init_tagger()

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