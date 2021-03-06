# -*- coding: utf-8 -*-

import os
import re
import numpy as np
import csv

class InertialLoader:

    def window_data( self, data, window_size ):
        w_data = [ data[ i*window_size : (i+1)*window_size ]
                   for i in range( len(data) // window_size ) ]
        return w_data


    def fix_seq_size( inp, max_len ):
        #Fill with zeros the sequences smaller than max_len
        if( len(inp) < max_len ):
            inp += np.zeros( [max_len-len(inp), 19] ).tolist()
        # Truncate sequences greater than max_len
        inp = inp[:max_len]
        return inp


    def convert_rate( self, data, input_rate, output_rate ):
        out   = list()
        ratio = output_rate / input_rate
        next_idx = 0.0
        for i, line in enumerate(data):
            print(i)
            if i == int( next_idx ):
                out.append( line )
                next_idx += ratio
        return out


    def _read_classes( self, classInd ):
        classNames = list()
        with open( classInd, 'r' ) as f:
            for line in f.readlines():
                classNames.append( line.split(' ')[1].strip('\n') )
        return classNames


    def load_data( self,
                   data_dir    = '',
                   classInd    = '../classes/classIndLyell.txt',
                   window_size = None,
                   max_len     = None,
                   input_rate  = None,
                   output_rate = None ):
        classNames = self._read_classes( classInd )
        data_dict = dict()
        filenames = os.listdir( data_dir )
        for filename in filenames:
            if filename.split('.')[-1] != 'csv': continue
            for classname in classNames:
                if re.findall( classname, filename ): break
            #classname = re.match('(\D+\d+).*', filename).groups()[0]
            with open( os.path.join(data_dir, filename), 'r' ) as f:
                inp = list( csv.reader(f, quoting=csv.QUOTE_NONNUMERIC) )
                if output_rate is not None:
                    inp = self.convert_rate( inp, input_rate, output_rate )
                if max_len is not None:
                    inp = self.fix_seq_size( inp, max_len )
                if window_size is not None:
                    inp = self.window_data( inp, window_size )
                data_dict[ classname + '/' + filename.split('.')[0] ] = inp
        return data_dict
