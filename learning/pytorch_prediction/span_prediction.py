import mysql.connector
import struct
import word2vec as w2v
import argparse
import matplotlib
import sys
import common.utilities as ut
import numpy as np
import torch

matplotlib.use('Agg')

import models.rnn_models as Model
import data.data_span as Data


if __name__ == "__main__":

    #command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--format',action='store',default='text',type=str)
    parser.add_argument('--embed_file',action='store',type=str)
    args = parser.parse_args(sys.argv[1:])

    #create database connection
    cnx = ut.create_connection('static0512')

    data = Data.DataInstructionEmbedding()

    #data.update_span(cnx, args.format)
    #exit()

    data.prepare_data(cnx,args.format,args.embed_file)

    data.generate_datasets()
    
    data.count_span_dist(data.train_y)
    data.count_span_dist(data.test_y)

    # #get the embedding size
    embedding_size = data.final_embeddings.shape[1]
    model = Model.ModelSpanRelational(embedding_size)
    train = Model.Train(model,data, batch_size = 100)

    train.train(train.mse_loss,1)
    train.validate(train.mse_loss,1)
    
    cnx.close()
    
