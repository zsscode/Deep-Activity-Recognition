import numpy as np
import os
import time

from TrainLoader import TrainLoader
from TestLoader  import TestLoader

from keras.models import load_model



class BaseTemporal:
    
    def __init__( self,
                  restoreModel,
                  dim,
                  timesteps,
                  classes,
                  batchSize,
                  rootPath,
                  modelPath,
                  modelName,
                  numThreads,
                  maxsizeTrain,
                  maxsizeTest ):
        self._dim = dim
        self._timesteps = timesteps
        self._classes   = classes
        self._batchSize = batchSize
        self._rootPath  = rootPath
        self._modelPath = modelPath
        self._modelName = modelName
        self._numThreads = numThreads
        self._maxsizeTrain = maxsizeTrain
        self._maxsizeTest  = maxsizeTest
        
        self._lblFilename = '../classInd.txt'
        self._trainFilenames = np.load( '../splits/trainlist01.npy' )
        self._testFilenames  = np.load( '../splits/testlist01.npy'  )
        self._resultsPath = '../results'
        self._step = 0

        self.loadModel( restoreModel )


    def _defineNetwork( self ):
        raise NotImplementedError( 'Please implement this method' )


    def loadModel( self, restoreModel ):
        print( 'Loading model...' )
        if not restoreModel:
            self.model = self._defineNetwork()
        else:
            self.model = load_model( os.path.join( self._modelPath,
                                                   str(self._modelName) + '.h5' ) )
        print( 'Model loaded!' )
        nparams = self.model.count_params()
        print( str(nparams) + ' parameters.' )



    def _generateTrainLoader( self ):
        return TrainLoader( self._rootPath,
                            self._trainFilenames,
                            self._lblFilename,
                            batchSize = self._batchSize,
                            timesteps = self._timesteps,
                            numThreads = self._numThreads,
                            maxsize = self._maxsizeTrain,
                            tshape = True )

    def _generateTestLoader( self ):
        return TestLoader( self._rootPath,
                           self._testFilenames,
                           self._lblFilename,
                           numSegments = 5,
                           timesteps = self._timesteps,
                           numThreads = self._numThreads,
                           maxsize = self._maxsizeTest,
                           tshape = True )



    def _storeResult( self, filename, data ):
        f = open( os.path.join( self._resultsPath,
                                self._modelName + '_' + filename ), 'a' )
        f.write( data )
        f.close()
    

    def _prepareBatch( self, batch ):
        return batch



    def _saveModel( self ):
        print( 'Saving model...' )
        self.model.save( os.path.join( self._modelPath,
                                       str(self._modelName) + '.h5' ) )
        print( 'Model saved!' )


    def train( self,
               epochs,
               stepsToTrainError = 100,
               stepsToEval = 20000 ):
        train_acc_list  = list()
        train_loss_list = list()
        trainFlag = True

        while self._step < epochs:
            with self._generateTrainLoader() as trainLoader:
                # saves and evaluates every n steps 
                while self._step % stepsToEval or trainFlag:
                    trainFlag = False

                    batch , labels = trainLoader.getBatch()
                    batch = self._prepareBatch( batch )
                    # train the selected batch
                    tr = self.model.train_on_batch( batch,
                                                    labels )
                    batch_loss = tr[ 0 ]
                    batch_acc  = tr[ 1 ]
                    train_acc_list  += [ batch_acc ]
                    train_loss_list += [ batch_loss ]

                    # periodically shows train acc and loss on the batches
                    if not self._step % stepsToTrainError:
                        train_accuracy = np.mean( train_acc_list  )
                        train_loss     = np.mean( train_loss_list )
                        print( 'step %d, training accuracy %g, cross entropy %g'%(
                               self._step, train_accuracy, train_loss ) )
                        self._storeResult( 'train.txt', str(self._step) + ' ' +
                                                       str(train_accuracy) + ' ' +
                                                       str(train_loss) + '\n' )
                        train_acc_list  = list()
                        train_loss_list = list()

                    self._step += 1
            self._saveModel()
            
            # evalutate model
            print( 'STEP %d: TEST'%( self._step ) )
            self.evaluate()
            trainFlag = True



    def evaluate( self ):
        t = time.time()
        test_acc_list  = list()
        i = 0
        print( 'Evaluating...' )
        with self._generateTestLoader() as testLoader:
            while not testLoader.endOfData():
                if i % 200 == 0:
                    print( 'Evaluating video', i )

                testBatch , testLabels = testLoader.getBatch()
                testBatch = self._prepareBatch( testBatch )
                y_ = self.model.predict_on_batch( testBatch )
                mean = np.mean( y_, 0 )
                correct_prediction = np.equal( np.argmax( mean ),
                                               np.argmax( testLabels ) )
                
                if correct_prediction: test_acc_list.append( 1.0 )
                else: test_acc_list.append( 0.0 )
                
                #tst = self.model.test_on_batch( testBatch , testLabels )
                #test_acc_list.append( tst[ 1 ] )
                i += 1
            
        test_accuracy = np.mean( test_acc_list  )
        print( 'Time elapsed:', time.time() - t )
        print( 'test accuracy:', test_accuracy )
        self._storeResult( 'test.txt', str(self._step) + ' ' +
                                      str( test_accuracy ) + '\n' )
        return test_accuracy
        



if __name__ == '__main__':
    os.environ[ 'CUDA_VISIBLE_DEVICES' ] = '0'