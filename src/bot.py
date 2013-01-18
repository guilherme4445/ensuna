import Skype4Py
import time
import random
import pickledb
from plugins import *
#from plugins import define
#http://skype4py.sourceforge.net/doc/html/Skype4Py.chat.ChatMessage-class.html

THEMES = ['general', 'science']

class SkypeBot:
	def __init__(self):
		self.skype = Skype4Py.Skype()
		if self.skype.Client.IsRunning == False:
			self.skype.Client.Start()
		self.skype.Attach()
		self.skype.OnMessageStatus = self.RunFunction

		self.listen = False
		self.start = time.clock()
		self.currentQuestion = 'No question currently active'
		self.currentHint = ''
		self.currentAnswer = ''
		self.mode = ''
		self.context = ''

		self.db = pickledb.load('data.db', False)
		self.scoreboard = self.db.get('scores')
		self.questions = self.db.get('science')
		self.wordlist = self.db.get('wordlist')
		self.eightBall = self.db.get('8ball')
		self.counters = self.db.get('counters')
		self.owner = self.db.get('owner')
		self.admin = self.db.get('admin')
		self.catalogue = self.db.get('catalogue')

	def RunFunction(self, Message, Status):
		if Status == 'SENT' or Status == 'RECEIVED':
			cmd = Message.Body.split(' ')[0]
			if cmd in self.functions.keys():
				self.context = Message
				self.functions[cmd](self)
			elif self.listen:
				self.ParseAnswer(Message, Message.Body)

	def CounterPick(self):
		champ = self.context.Body.split(' ')[1:]
		if len(champ) > 1: 
			champ = "{0} {1}".format(champ[0].title(), champ[1].title())
		elif len(champ) == 1:
			champ = champ[0].title()
		else:
			self.context.Chat.SendMessage('/me Counterpick: Usage - !counter <champion>')
			return
		try:
			counter = self.counters[champ]
			temp = "Champions that counter {0}:\n".format(champ)
			for champ in counter:
				temp += (champ + '\n')
			self.context.Chat.SendMessage('/me ' + temp)
		except KeyError:
			self.context.Chat.SendMessage('/me Champion not found')

	def CatalogueAdd(self):
		try:
			#category exists and input is correct
			category = self.context.Body.split(' ')[1]
			urls = self.context.Body.split(' ')[2:]
			for url in urls:
				self.catalogue[category].append(url)
			self.CatalogueUpdate()
		except KeyError:
			#category does not exist
			self.catalogue[category] = [url]
			self.CatalogueUpdate()
		except IndexError:
			#incorrect input
			self.context.Chat.SendMessage('/me Catalogue Add: Usage - !cadd <category> <url> <url2...>\nUse !cata to get a list of all catalogues')

	def CatalogueGet(self):
		try:
			category = self.context.Body.split(' ')[1]
			temp = ""
			for url in self.catalogue[category]:
				temp += (url + '\n')
			self.context.Chat.SendMessage(temp)
		except IndexError:
			self.context.Chat.SendMessage('/me Catalogue Get: Usage - !cget <category>')
		except KeyError:
			self.context.Chat.SendMessage('/me Error: category ({0}) does not exist, use !cata command to get a list of all catalogues'.format(category))

	def CatalogueGetAll(self):
		temp = 'Current catalogues: '
		for item in self.catalogue.keys():
			temp += (item + ', ')
		self.context.Chat.SendMessage(temp[:-2])

	def CatalogueUpdate(self):
		self.context.Chat.SendMessage('/me Catalogue updated.')
		self.db.set('catalogue', self.catalogue)
		self.db.dump()

	def PrintCommands(self):
		temp = 'Commands: '
		for item in self.functions.keys():
			temp += (item + ', ')
		self.context.Chat.SendMessage(temp[:-2])

	def GetAdmins(self):
		self.context.Chat.SendMessage('/me ' + str(self.admin))

	def GetDefinition(self):
		try:
			self.context.Chat.SendMessage('/me ' + define.Definition(self.context.Body.split(' ')[1]))
		except IndexError:
			self.context.Chat.SendMessage('Dictionary: Usage - !define <term>')

	def GetGoogle(self):
		self.context.Chat.SendMessage('/me ' + google.Lookup(self.context.Body[8:]))

	def PrintRules(self):
		self.context.Chat.SendMessage('/me' + ' 1. Accept your first answer, no re-wording or retries of questions allowed.\n2. Rules cannot be circumvented by any reply 8b gives.')

	def RepeatQuestion(self):
		self.context.Chat.SendMessage('/me Q: ' + self.currentQuestion + '\nHINT: ' + self.currentHint)

	def EightBall(self):
		self.context.Chat.SendMessage('/me ' + random.choice(self.eightBall))

	def GetAnswer(self):
		self.context.Chat.SendMessage('/me The answer was: ' + self.currentAnswer)
		if self.mode == 'shuffle':
			self.SetShuffle()
		else:
			self.SetQuestion()

	def SetTheme(self):
		if self.context.FromHandle in self.admin:
			try: 
				theme = self.context.Body.split(' ')[1]
				if theme in THEMES: 
					self.questions = self.db.get(theme)
					self.context.Chat.SendMessage('Trivia theme changed to: ' + theme)
				else:
					self.context.Chat.SendMessage('Invalid trivia theme. Valid themes are: ' + str(THEMES))
			except IndexError:
				self.context.Chat.SendMessage('Please provide a theme name - !theme <theme>')

	def GetScore(self):
		try:
			self.context.Chat.SendMessage('/me ' + self.context.FromHandle + "'s score: " + str(self.scoreboard[self.context.FromHandle]))
		except KeyError:
			self.scoreboard[self.context.FromHandle] = 0
			self.context.Chat.SendMessage('/me ' + self.context.FromHandle + ' not recognized, added to scoreboard')

	def GetLead(self):
		topPlayers = sorted(self.scoreboard, key=self.scoreboard.get, reverse=True)[:5]
		temp = "Top 5 Players:\n"
		for player in topPlayers:
			temp += ('{0}: {1}\n'.format(player, self.scoreboard[player]))
		self.context.Chat.SendMessage(temp)

	def GetUptime(self):
		seconds = int(time.clock()-self.start)
		hours, remainder = divmod(seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		self.context.Chat.SendMessage('{0}h:{1}m:{2}s'.format(hours, minutes, seconds))

	def SetShuffle(self):
		self.listen = True
		self.mode = 'shuffle'
		self.currentAnswer = random.choice(self.wordlist)
		temp = list(self.currentAnswer)
		random.shuffle(temp)
		self.currentQuestion = ''.join(temp)
		self.context.Chat.SendMessage('/me Shuffle: ' + self.currentQuestion)

	def SetQuestion(self):
		if self.currentQuestion == "No question currently active" or self.context.FromHandle in self.admin:
			self.listen = True
			self.mode = 'trivia'
			self.currentQuestion = random.choice(self.questions.keys())
			self.currentAnswer = str(self.questions[self.currentQuestion])
			self.Hint()
			self.context.Chat.SendMessage('/me Q: ' + self.currentQuestion + '\nHINT: ' + self.currentHint)

	def EndQuestion(self):
		self.context.Chat.SendMessage('/me Stopping trivia questions...')
		self.currentQuestion = 'No question currently active'
		self.currentHint = ''
		self.currentAnswer = ''
		self.listen = False

	def ParseAnswer(self, Message, query):
		if query.lower() == self.currentAnswer.lower():
			try:
				self.scoreboard[Message.FromHandle] = int(self.scoreboard[Message.FromHandle]) + 1
			except KeyError:
				self.scoreboard[Message.FromHandle] = 1
			Message.Chat.SendMessage("/me {0}[{1}] is Correct! A: {2}".format(Message.FromHandle, str(self.scoreboard[Message.FromHandle]), self.currentAnswer))
			self.SaveScores()
			if self.mode == 'shuffle':
				self.SetShuffle()
			else:
				self.SetQuestion()
		else:
			pass

	def GetUser(self):
		self.context.Chat.SendMessage('/me ' + self.context.FromHandle)

	def Hint(self):
		answer = self.currentAnswer
		numberOfHints = int(0.75*len(answer))
		indexes = []
		temp = []
		for x in xrange(len(answer)) : indexes.append(x)
		repl = random.sample(indexes, numberOfHints)
		for char in answer:
			if answer.index(char) in repl or char in ['\'', ',', ' ', '-', '.']:
				temp.append(char)
			else:
				temp.append('_')
		for x in xrange(len(temp)): temp[x] = temp[x] + ' '
		self.currentHint = "".join(temp)

	def SaveScores(self):
		self.db.set('scores', self.scoreboard)
		self.db.dump()

	functions = {
	"!question":	SetQuestion, 
	"!shuffle":		SetShuffle, 
	"!8b":			EightBall, 
	"!answer":		GetAnswer, 
	"!stop":		EndQuestion, 
	"!repeat":		RepeatQuestion, 
	"!theme":		SetTheme, 
	"!score":		GetScore, 
	"!lead":		GetLead, 
	"!define":		GetDefinition, 
	"!uptime":		GetUptime,
	"!admins":		GetAdmins,
	"!commands":	PrintCommands,
	"!counter":		CounterPick,
	"!google":		GetGoogle,
	"!user":		GetUser,
	"!cadd":		CatalogueAdd,
	"!cget":		CatalogueGet,
	"!cata":		CatalogueGetAll
	}

if __name__ == "__main__":
	ensuna = SkypeBot()
	while True:
		time.sleep(1)