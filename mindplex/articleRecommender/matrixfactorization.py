import pickle
from random import seed
import tensorflow as tf 
import pandas as pd 
import numpy as np 
class MatrixFactorization:
    def __init__(self,
                 interactions_df:pd.DataFrame,
                 latent_features:int,
                 learning_rate:float,
                 epochs:int,
                 l2_regularizer=0.04,
                 random_seed=1000,
                 path=''
                 ) -> None:
        self.interactions_df=tf.convert_to_tensor(interactions_df,dtype=tf.float32)
        self.mast=tf.not_equal(self.interactions_df,0)
        self.num_users,self.num_items=self.interactions_df.shape
        self.tolerable_loss=0.001
        self.path=path 
        self.weight_initializer=tf.random_normal_initializer(seed=seed)
        self.V=tf.Variable(self.weight_initializer((self.num_users,self.latent_features)))
        self.U=tf.Variable(self.weight_initializer((self.num_items,self.latent_features)))
        self.latent_features=latent_features
        self.learning_rate=learning_rate
        self.epochs=epochs
        self.l2_regularizer=l2_regularizer
    def loss(self):
        """ 
        Squared error loss
        """
        error=np.square((self.ratings-tf.matmul(self.V,self.U,transpose_b=True)))
        l2_norm=tf.reduce_sum(np.square(self.V))+tf.reduce_sum(np.square(self.U))
        final_loss=tf.reduce_sum(tf.boolean_mask(error,self.mask))+self.l2_regularizer*l2_norm
        return final_loss 
    def gradientDescent(self):
        with tf.GradientTape() as tape:
            tape.watch([self.V,self.U])
            self.current_loss=self.loss()
            grad_V,grad_U=tape.gradient(self.current_loss,[self.V,self.U])
            self.V.assign_sub(self.learning_rate*grad_V)
            self.U.assign_sub(self.learning_rate*grad_U)
    def train(self):
        for epoch in range(self.epochs):
            self.gradientDescent()
            if self.current_loss<self.tolerable_loss:
                break 
        # Save the model here
        #self.saveModel()
    def saveModel(self):
        with open(self.path,"wb") as file:
            pickle.dump([self.V,self.U],file)
             
            
    
     
    
        
    
    
    