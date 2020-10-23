import numpy as np
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

logger = logging.getLogger("Chain")
logger.setLevel(logging.INFO)


class Chain():
	def __init__(self, chain_file, index_file):
		self.chain_file = chain_file
		self.index_file = index_file


		logger.info("Initializing index: {} ...".format(index_file))
		self.initialize_index()
		logger.info("Done.")

		logger.info("Initializing empty arrays ...")
		self.initialize_arrays()
		logger.info("Done.")
		
	def initialize_arrays(self):
		self._arrays = {}
		for varname, size in self._chain_sizes.items():
			self._arrays[varname] = np.empty(size)
			self._arrays[varname][:] = np.nan

		for key, val in self._arrays.items():
			print(key, val.shape)
	
	def initialize_index(self):
		self._chain_sizes = dict()	

		def parse_index_line(line):
			split_line = line.split()
			if "[" in split_line[0]:
				var_split = split_line[0].split("[")
				varname = var_split[0]
				idxes_str = var_split[1].strip("]").split(",")
				idxes = [int(idx) for idx in idxes_str]	
			else:
				varname = split_line[0]
				idxes = None

			line_start = int(split_line[1])-1
			line_end = int(split_line[2])-1
			if idxes == None:
				idxes = line_end-line_start+1
			else:
				idxes.append(line_end-line_start+1)
			return {'var': varname, 'idx': idxes, 'start': line_start, 'end': line_end}
					
		# Iterate over the lines
		self._var_dicts = []	
		for line in self._readlines_reverse(self.index_file):
			if not line:
				continue

			var_dict = parse_index_line(line)
			self._var_dicts.append(var_dict)
			if var_dict['var'] not in self._chain_sizes.keys():
				self._chain_sizes[var_dict['var']] = var_dict['idx']
		self._var_dicts = list(reversed(self._var_dicts))

	def save(self):
		pass

	def _readlines_reverse(self, filename):
		with open(filename) as qfile:
			qfile.seek(0, os.SEEK_END)
			position = qfile.tell()
			line = ''
			while position >= 0:
				qfile.seek(position)
				next_char = qfile.read(1)
				if next_char == "\n":
					yield line[::-1]
					line = ''
				else:
					line += next_char
				position -= 1
			yield line[::-1]

