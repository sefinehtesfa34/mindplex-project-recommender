import pickle
import tensorflow as tf  
import numpy as np 
import warnings 
warnings.filterwarnings("ignore")
class MatrixFactorization:
    def __init__(self,
                 ratings,
                 latent_features:int,
                 learning_rate:float,
                 epochs:int,
                 l2_regularizer=0.04,
                 random_seed=1000,
                 path=''
                 ) -> None:
        self.ratings=tf.convert_to_tensor(ratings,dtype=tf.float32)
        self.mask=tf.not_equal(self.ratings,0)
        self.num_users,self.num_items=self.ratings.shape
        self.tolerable_loss=0.001
        self.path=path 
        self.weight_initializer=tf.random_normal_initializer(seed=random_seed)
        self.P=tf.Variable(self.weight_initializer((self.num_users,self.latent_features)))
        self.Q=tf.Variable(self.weight_initializer((self.num_items,self.latent_features)))
        self.latent_features=latent_features
        self.learning_rate=learning_rate
        self.epochs=epochs
        self.l2_regularizer=l2_regularizer
    def loss(self):
        """ 
        Squared error loss
        """
        error=np.square((self.ratings-tf.matmul(self.P,self.Q,transpose_b=True)))
        l2_norm=tf.reduce_sum(np.square(self.P))+tf.reduce_sum(np.square(self.Q))
        final_loss=tf.reduce_sum(tf.boolean_mask(error,self.mask))+self.l2_regularizer*l2_norm
        return final_loss
     
    def gradientDescent(self):
        with tf.GradientTape() as tape:
            tape.watch([self.P,self.Q])
            self.current_loss=self.loss()
            grad_V,grad_U=tape.gradient(self.current_loss,[self.P,self.Q])
            self.P.assign_sub(self.learning_rate*grad_V)
            self.Q.assign_sub(self.learning_rate*grad_U)
    def train(self):
        for epoch in range(self.epochs):
            self.gradientDescent()
            if self.current_loss<self.tolerable_loss:
                break 
        # Save the model here
        self.saveModel()
    def saveModel(self):
        with open(self.path,"wb") as file:
            pickle.dump([self.P,self.Q],file)
        
             
            
    
     
    
        
    
    
# import pandas as pd

# df=pd.DataFrame({"userId":["123","456","654","234"],"contentId":["10923","45673","39856","8970"],"ratings":[1,5,3,2]})
# print(df)
# rating_average=df['ratings'].mean()
# data = df.pivot(index='userId',columns='contentId',values='ratings').fillna(rating_average)
# print(data)
# ratings=tf.convert_to_tensor(data,dtype=tf.float32)
# print(ratings)
# mask=tf.not_equal(ratings,0)
# print(mask)