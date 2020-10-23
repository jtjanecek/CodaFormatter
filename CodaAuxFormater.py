import os
from models.Chain import Chain

chain_file = '/tmp/yassamri2/Tsukuba/hierarchical/storage/model_07/samples_1_chain1.txt'
index_file = '/tmp/yassamri2/Tsukuba/hierarchical/storage/model_07/samples_1_index.txt'

c = Chain(chain_file, index_file)
c.save()
