import h5py
import logging
import argparse
import numpy as np
import glob
import os
from utils.diagnostics import gelman_rubin
from time import time



# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logger = logging.getLogger("AnalyzeConvergence")
logger.setLevel(logging.INFO)

# Setup CLI args
parser = argparse.ArgumentParser(description='Assess chain output for hdf5 files in input directory (one chain per file)')
parser.add_argument('--dir', help='input directory', required=True)
cli_args = parser.parse_args()

# Read in hdf5 files
logger.info("Searching for files ...")
hdf_files = glob.glob(os.path.join(cli_args.dir, "*.hdf5"))
logger.info("Found {} files.".format(len(hdf_files)))

# Open the hdf5 files
ofs = []
for hdf in hdf_files:
	logger.info("Opening {} ...".format(hdf))
	of = h5py.File(hdf, 'r')
	ofs.append(of)


def analyze(open_hdfs, thres=1.05):
	rhats = []
	for var in open_hdfs[0].keys():
	#for var in ['alphaMu', 'alphaDiffExerciseCarryover']:
		logger.info("Reading {} ...".format(var))
		chain_vars = np.array([np.array(of.get(var)) for of in open_hdfs])
		if len(chain_vars.shape) != 2:
			# Collapse middle dimensions
			chain_vars = chain_vars.reshape(chain_vars.shape[0], -1, chain_vars.shape[-1])
			# Iterate over 
			for dim in range(chain_vars.shape[1]):
				varname = "{}_{}".format(var, dim)
				rhat = gelman_rubin(chain_vars[:,dim,:])
				if rhat > thres:
					logger.info("{}: Rhat: {}".format(varname, rhat))
				rhats.append([varname, rhat])	
		else:
			rhat = gelman_rubin(chain_vars)
			if rhat > thres:
				logger.info("{}: Rhat: {}".format(var, rhat))
			rhats.append([var, rhat])	
		
	logger.info("Rhats > {}:".format(thres))
	for varname, rhat in rhats:
		if rhat > thres:
			logger.info("{}: {:.2f}".format(varname, rhat))
	logger.info("Done.")


try:
	start_time = time()
	analyze(ofs)
	logger.info("Took {:.2f} minutes!".format((time() - start_time)/60))
finally:
	for of in ofs:
		of.close()
