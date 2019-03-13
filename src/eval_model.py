import Spatial.Spatial as Network
import os
import sys

os.environ[ 'CUDA_VISIBLE_DEVICES' ] = '1'

split = int( sys.argv[1] )
split_f = '{:02d}'.format( split )

network = Network( restoreModel = True,
                   classes      = 20,
                   dataDir      = '/home/cmranieri/datasets/multimodal_dataset_rgb',
                   modelDir     = '/home/cmranieri/models/multimodal',
                   modelName    = 'model-multi-spatial-l' + str(split),
                   lblFilename  = '../classIndMulti.txt',
                   numSegments  = 5,
                   smallBatches = 1,
                   splitsDir    = '../splits/multimodal_10',
                   split_n      = split_f )

#network.train( epochs = 40000 )
network.evaluate()