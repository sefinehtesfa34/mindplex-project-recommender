import pickle
import tensorflow as tf  
import numpy as np 
import warnings 
from sklearn.preprocessing import StandardScaler 
from sklearn.metrics.pairwise import cosine_similarity
warnings.filterwarnings("ignore")
class MatrixFactorization:
    def __init__(self,
                 ratings,
                 latent_features=15,
                 learning_rate=0.001,
                 epochs=50,
                 l2_regularizer=0.04,
                 random_seed=1000,
                 path='weights'
                 ) -> None:
        
        self.pivot_ratings = ratings
        scaler=StandardScaler(with_mean=True,with_std=True)
        scaled_ratings=scaler.fit_transform(ratings)
        self.ratings = tf.convert_to_tensor(scaled_ratings,dtype=tf.float32)
        
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
        self.ratings_path="ratingsWeight"
           
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
        with open(self.ratings_path,"wb") as ratings_weight:
            pickle.dump(self.pivot_ratings,ratings_weight)
        
            
            
    #This function removes the redundant cells of the similarity score
    # For example similarity=cosine_similarity([[1,2,3,4,5],
    #                                            [2,5,3,4,8],
    #                                            [8,5,1,2,7],
    #                                            [9,0,8,9,5]])
    # The output would be Out[7]: 
            # array([[1.        , 0.95580297, 0.72165664, 0.80003622],
            #        [0.95580297, 1.        , 0.83140902, 0.68565262],
            #        [0.72165664, 0.83140902, 1.        , 0.7020156 ],
            #        [0.80003622, 0.68565262, 0.7020156 , 1.        ]])

# Look the redundant cells above 
# The output of the optimalSimilarityWeightSaver function will be 
# {
#    (0,0):1.,(0,1):0.95580297,(0,2):0.72165664,(0,3):0.80003622,
#    (1,1):1.,(1,2):0.83140902,(1,3):0.68565262),
#    (2,2):1.0,(2,3):0.7020156,
#   (3,3):1.0
# }
# The removed are (1,0),(2,0),(3,0),(2,1),(3,1),(3,2)<==redundant
# We can also remove similarities to themselves==>1.0

    
     
    def optimalSimilarityWeightSaver(self,similarity_type):
        shape=similarity_type.shape
        visited=set()
        unique_similarity_ratings={}
        
        for index1 in range(shape[0]):
            for index2 in range(shape[0]):
                if (index1,index2) not in visited:
                    unique_similarity_ratings[(index1,index2)]\
                        =similarity_type[index1][index2]
                    visited.add((index1,index2))
                    visited.add((index2,index1)) 
        return unique_similarity_ratings
    
        
    def userSimilarity(self):
        user_similarity_scaler=StandardScaler(with_mean=True,with_std=True)
        scaled_P=user_similarity_scaler.fit_transform(self.P)
        return cosine_similarity(scaled_P) 
    def itemSimilarity(self):
        item_similarity_scaler=StandardScaler(with_mean=True,with_std=True)
        scaled_Q=item_similarity_scaler.fit_transform(self.Q)
        return cosine_similarity(scaled_Q)
    
     
     
     
     
     
     
     
     