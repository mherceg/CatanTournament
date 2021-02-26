#!/usr/bin/env python3
import os

class Result():

	def __init__(self, wins, name, points, total_points, rounds_played=1):
		self.wins = int(wins)
		self.name = name
		self.points = int(points)
		self.total_points = int(total_points)
		self.rounds_played = rounds_played

	def __str__(self):
		return f'{self.name:>16}{self.wins:>13}{self.points:>13}{self.points*1./self.total_points if self.total_points != 0 else -1:>12.3}\t{self.rounds_played:>9}'

def compute():
	res_files = filter(lambda x:x.endswith('.txt'), os.listdir('./results'))
	results = dict()
	for f in list(res_files):
		current_results = set()
		with open(f'results/{f}', 'r') as fin:
			for line in fin:
				r = line.split('\t')
				r = Result(1 if int(r[0]) == 1 else 0, *(r[1:]))
				if r.name in current_results:
					print(f'Played twice in the same round {r.name} {f}')
				current_results.add(r.name)
				if r.name in results:
					a = results[r.name] 
					r = Result(r.wins+a.wins, r.name, r.points+a.points, r.total_points+a.total_points, a.rounds_played+1)
				results[r.name] = r
	v = results.values()
	return list(map(str,sorted(v, key=lambda x:(x.wins, x.points, x.points/x.total_points if x.total_points != 0 else -1), reverse=True)))

if __name__ == '__main__':
	c = compute()
	for l in c:
		print(l)