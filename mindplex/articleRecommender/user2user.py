import pickle
import numpy as np
from django_pandas.io import read_frame

from articleRecommender.matrixfactorization import MatrixFactorization
class User2UserBased:
    def __init__(self,path) -> None:
        self.path=path 
    
    def scheduler(self,pivot_ratings,path):
        latent_features=15
        learning_rate=0.001
        epochs=100
        instance=MatrixFactorization(pivot_ratings,latent_features,
                                     learning_rate,
                                     epochs,path=path)    
        instance.train()
        
        
            