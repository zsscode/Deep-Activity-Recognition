import numpy as np
import os

from TemporalBase import TemporalBase

from tensorflow.keras.layers import Input, Dense, LSTM
from tensorflow.keras.layers import concatenate, Reshape, Permute
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.models import Model
from tensorflow.keras import regularizers


class Inertial_LSTM( TemporalBase ):
    def __init__( self, imuShape, **kwargs ):
        self.imuShape = imuShape
        kwargs[ 'cnnModelName' ] = None
        super( Inertial_LSTM , self ).__init__( streams = ['inertial'],
                                                **kwargs )


    def defineNetwork( self ):
        imuModel = self.imuBlock( self.imuShape )
        y = LSTM( units             = 128,
                  return_sequences  = False,
                  dropout           = 0.7,
                  recurrent_dropout = 0.3,
                  unroll            = False )( imuModel.outputs[-1] )
        y = Dense( self.classes,
                   kernel_regularizer = regularizers.l2( 0.01 ),
                   activation = 'softmax' )( y )
       
        model = Model( imuModel.inputs, y )
        optimizer = SGD( lr        = 1e-2, 
                         momentum  = 0.9,
                         decay     =1e-4,
                         clipnorm  =1.,
                         clipvalue =0.5 )
        model.compile( loss = 'categorical_crossentropy',
                       optimizer = optimizer,
                       metrics   = [ 'acc' ] ) 
        return model
