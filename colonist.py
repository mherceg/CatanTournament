import requests
import json

class User():

	def __init__(self, user, total=0):
		self.username = user['username']
		self.rank = user['rank']
		self.points = user['points']
		self.finished = user['finished']
		self.quited = user['quited']
		self.isHuman = user['isHuman']
		self.total = total

	def __str__(self):
		return f'{self.rank}\t{self.username}\t{self.points}\t{self.total}'


def get_result(user_name, order=0):
	s = requests.Session()
	s.get('https://colonist.io')
	r = s.get(f'https://colonist.io/api/profile/{user_name}')
	games = json.loads(r.content)['gameDatas']
	games = sorted(games, key=lambda x: x['startTime'], reverse=True)
	game = games[order]
	players = []
	total = sum([player['points'] for player in game['players']])
	for player in game['players']:
		players.append(User(player, total))
	players.sort(key=lambda x: x.rank)
	return players

def check_user(user_name):
	s = requests.Session()
	for i in range(3):
		s.get('https://colonist.io')
		r = s.get(f'https://colonist.io/api/profile/{user_name}')
		if r.status_code == 200:
			return True
	return False