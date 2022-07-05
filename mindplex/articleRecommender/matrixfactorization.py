import pickle
import os 
import tensorflow as tf  
import numpy as np 
import warnings 
from sklearn.metrics.pairwise import cosine_similarity
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
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
        self.latent_features=latent_features
        self.learning_rate=learning_rate 
        self.weight_initializer=tf.random_normal_initializer(seed=random_seed)
        self.P=tf.Variable(self.weight_initializer((self.num_users,self.latent_features)))
        self.Q=tf.Variable(self.weight_initializer((self.num_items,self.latent_features)))
        self.epochs=epochs
        self.l2_regularizer=l2_regularizer
        
    def loss(self):
        """ 
        Squared error loss
        """
        error=(self.ratings-tf.matmul(self.P,self.Q,transpose_b=True))
        l2_norm=tf.reduce_sum(self.P**2)+tf.reduce_sum(self.Q**2)
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
        self.user_similarity=self.userSimilarity()
        self.item_similarity=self.itemSimilarity()
        
        user_similarity_index=np.argsort(self.user_similarity)[::-1]
        item_similarity_index=np.argsort(self.item_similarity)[::-1]
        unique_user_similarity_ratings=self.optimalSimilarityWeightSaver(self.user_similarity)
        unique_item_similarity_ratings=self.optimalSimilarityWeightSaver(self.item_similarity)
        
        similarity_path="similarity"
        with open(similarity_path,"wb") as user_similarity_file:
            pickle.dump([unique_user_similarity_ratings,unique_item_similarity_ratings],user_similarity_file)
           
        
        with open(self.path,"wb") as weights:
            pickle.dump([user_similarity_index,item_similarity_index],weights)
    
    def optimalSimilarityWeightSaver(self,similarity_type):
        shape=similarity_type.shape
        visited=set()
        unique_similarity_ratings={}
        for index1 in range(shape[0]):
            for index2 in range(shape[0]):
                if (index1,index2) not in visited:
                    unique_similarity_ratings[(index1,index2)]=self.user_similarity[index1][index2]
                    visited.add((index1,index2))
                    visited.add((index2,index1)) 
        return unique_similarity_ratings
    
        
    def userSimilarity(self):
        return cosine_similarity(self.P) 
    def itemSimilarity(self):
        return cosine_similarity(self.Q)
     