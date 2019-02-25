import os

from NetworkBase import NetworkBase

from keras.applications.inception_v3 import InceptionV3
from keras.layers import Input, Dense 
from keras.optimizers import SGD
from keras.models import Model



class Spatial( NetworkBase ):
    
    def __init__( self,
                  restoreModel,
                  dim = 224,
                  classes   = 101,
                  batchSize = 32,
                  rootPath  = '/home/cmranieri/datasets/UCF-101_rgb',
                  modelPath =  '/home/cmranieri/models/ucf101',
                  modelName = 'model-ucf101-rgb',
                  numThreads = 2,
                  maxsizeTrain = 4,
                  maxsizeTest  = 4,
                  lblFilename  = '../classInd.txt',
                  splitsDir    = '../splits/ucf101',
                  split_n = '01',
                  tl = False,
                  tlSuffix = '' ):

        super( Spatial , self ).__init__( restoreModel = restoreModel,
                                          dim          = dim,
                                          timesteps    = None,
                                          classes      = classes,
                                          batchSize    = batchSize,
                                          rootPath     = rootPath,
                                          modelPath    = modelPath,
                                          modelName    = modelName,
                                          numThreads   = numThreads,
                                          maxsizeTrain = maxsizeTrain,
                                          maxsizeTest  = maxsizeTest,
                                          lblFilename  = lblFilename,
                                          splitsDir    = splitsDir,
                                          split_n      = split_n,
                                          tl           = tl,
                                          tlSuffix     = tlSuffix,
                                          stream       = 'spatial' )



    def _defineNetwork( self ):
        input_tensor = Input( shape = ( self._dim, self._dim, 3 ) )
        base_model = InceptionV3( input_tensor = input_tensor,
                                  weights = 'imagenet',
                                  include_top = False,
                                  pooling = 'avg' )
        y = base_model.output
        y = Dense( self._classes, activation='softmax' )( y )
        
        model = Model( inputs = base_model.input, outputs = y )
        for layer in base_model.layers:
                layer.trainable = False

        optimizer = SGD( lr = 1e-2, momentum = 0.9,
                         nesterov=True, decay = 1e-4 )
        model.compile( loss = 'categorical_crossentropy',
                       optimizer = optimizer,
                       metrics   = [ 'acc' ] ) 
        return model
        


if __name__ == '__main__':
    os.environ[ 'CUDA_VISIBLE_DEVICES' ] = '1'
    
    network = Spatial( restoreModel = False )
    #network.evaluate()
    network.train( epochs = 100000 )