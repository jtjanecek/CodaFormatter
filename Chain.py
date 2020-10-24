import h5py
from time import time
import numpy as np
import os
import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')

logger = logging.getLogger("Chain")
logger.setLevel(logging.INFO)


class Chain():
	def __init__(self, chain_file, index_file, output_dir):
		self.chain_file = chain_file
		self.index_file = index_file
		self.output_dir = output_dir

		start_time = time()
		logger.info("Initializing index: {} ...".format(index_file))
		self.initialize_index()
		logger.info("Done.")

		logger.info("Initializing empty arrays ...")
		self.initialize_arrays()
		logger.info("Done.")

		logger.info("Reading chain ...")
		self.read_chain()
		logger.info("Done.")

		logger.info("Total reconstruction time: {:.2f} minutes!".format((time()-start_time)/60))

		self.save()
		
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

	def initialize_arrays(self):
		self._arrays = {}
		for varname, size in self._chain_sizes.items():
			self._arrays[varname] = np.empty(size)
			self._arrays[varname][:] = np.nan

		for key, val in self._arrays.items():
			print(key, val.shape)
	
	def read_chain(self):
		num_var_dicts = len(self._var_dicts)
		ticks = []
	
		chain_start_time = time()
	
		self.__chain_line_num = 0
		with open(self.chain_file, 'r') as fo:
			# Update each variable
			for i, var_dict in enumerate(self._var_dicts):
				start_time = time()
				self._read_chain_variable(fo, var_dict)
				end_time = time()
				ticks.append(end_time-start_time)
				#if i % 500 == 0:
				if True:
					total_estimated_time = np.mean(ticks) * num_var_dicts / 60
					elapsed_time = (time() - chain_start_time) / 60
					logger.info("{:.2f}% complete. Time left: {:.2f} min! Cur chain: {}".format((i+1)*100/num_var_dicts, total_estimated_time - elapsed_time, var_dict))

	def _read_chain_variable(self, fo, var_dict):
		# index to update
		if type(var_dict['idx']) == int:
			cur_idx = [var_dict['idx']]
		else:
			cur_idx = list(var_dict['idx'])
		# To convert ypred[1,1,1,3000] -> ypred[0,0,0,3000] so that 0 based indexing works
		cur_idx = [idx-1 for idx in cur_idx] 
		# Set current idx to update to 0
		cur_idx[-1] = 0
		#logger.info("{} ...".format(var_dict))
		while self.__chain_line_num <= var_dict['end']:
			line = next(fo)
			data = float(line.split()[1])
			idx_to_update = tuple(cur_idx)
			self._arrays[var_dict['var']][idx_to_update] = data

			# Update the current idx and current line number 
			self.__chain_line_num += 1
			cur_idx[-1] += 1

	def save(self):
		logger.info("Saving chain ...")
		output_name = os.path.basename(self.chain_file).split(".")[0]
		output_file = os.path.join(self.output_dir, output_name) + ".hdf5"
		with h5py.File(output_file,'w') as f:
			for key in self._arrays.keys():
				logger.info("Saving key: {}".format(key))
				f[key] = self._arrays[key]
		logger.info("Done.")

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

if __name__ == '__main__':
	import argparse		
	parser = argparse.ArgumentParser(description='Format a JAGS output chain to better format (collapse indices etc)')
	parser.add_argument('--chain', help='JAGS chain file', required=True)
	parser.add_argument('--index', help='JAGS index file', required=True)
	parser.add_argument('--out', help='output directory', required=True)
	cli_args = parser.parse_args()

	# Run
	Chain(cli_args.chain, cli_args.index, cli_args.out)
	
