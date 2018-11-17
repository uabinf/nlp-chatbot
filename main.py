import nlp
import nltk

run = True

def assert_args(n, args, cmd):
	if n == len(args):
		return False
	else:
		print('Invalid number of arguments to %s: %s (expected %s)\n' % (cmd, len(args), n))
		return True

def cmd_difficulty(args):
	if assert_args(1, args, 'difficulty'):
		return

	print('Set difficulty to %s.\n' % args[0])
	nlp.set_difficulty(args[0])

def cmd_help(args):
	if assert_args(0, args, 'help'):
		return

	for c in sorted(command):
		# This formatted printing works fine on my computer but fails on cheaha
		print('!%s %-20.20s %s' % (c[0], c[1] if c[1] else '', c[2]))
	print('')

def cmd_quit(args):
	global run
	if assert_args(0, args, 'quit'):
		return

	print('Now quitting.\n')
	run = False

command = {
	'difficulty':(cmd_difficulty, '[diff]', 'Set the current difficulty.'),
	'help':(cmd_help, '', 'Display this help menu.'),
	'quit':(cmd_quit, '', 'Quit the bot session.'),
}

print('Extracting Context Free Grammar...')
CFG = cfg.beginExtraction()
print('Started a chatbot session.\nType !help for a list of commands or a German sentence to evaluate it.\n')

while run:
	i = input()

	# Check if input was a command, all commands preceded by a !
	if i[0] == '!':
		i = i[1:]
		args = i.split()

		if args[0] in command:
			command[args[0]][0](args[1:])
		else:
			print('Invalid command: %s' % args[0])
	else:
		response = nlp.rate_sentence(i)

		print('Response from bot:')
		for r in response:
			print('\t%s' % r)
		print('')
