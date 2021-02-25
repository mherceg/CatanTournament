#!/usr/bin/env python3
import os

class Result():

	def __init__(self, r):
		r = r.split('\t')
		self.wins = 1 if int(r[0]) == 1 else 0
		self.name = r[1]
		self.points = int(r[2])
		self.total_points = int(r[3])

	def __str__(self):
		return f'{self.name}\t{self.wins}\t{self.points}\t{self.points*1./self.total_points}'


res_files = filter(lambda x:x.endswith('.txt'), os.listdir('./results'))
results = dict()
for f in list(res_files):
	current_results = set()
	print(f)
	with open(f'results/{f}', 'r') as fin:
		for line in fin:
			r = Result(line)
			if r.name in current_results:
				print(f'Played twice in the same round {r.name} {f}')
			current_results.add(r.name)
			if r.name in results:
				a = results[r.name] 
				r = Result(f'{r.wins+a.wins}\t{r.name}\t{r.points+a.points}\t{r.total_points+a.total_points}')
			results[r.name] = r
v = results.values()
for k in sorted(v, key=lambda x:(x.wins, x.points, x.points/x.total_points), reverse=True):
	print(k)