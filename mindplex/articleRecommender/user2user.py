import pickle
import numpy as np
from django_pandas.io import read_frame

from articleRecommender.matrixfactorization import MatrixFactorization
class User2UserBased:
    def __init__(self,path) -> None:
        self.path=path 
    def preprocessor(self,interactions):
    
        interactions_df=read_frame(interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        
        interactions_df['eventType'] = interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x,0))
        interactions_df=interactions_df.rename(columns={"eventType":"eventStrength"})
        interactions_df=interactions_df.iloc[1:,:]
        average=interactions_df["eventStrength"].mean()
        ratings=interactions_df.pivot_table(index="userId",
                                            columns="contentId",
                                            values="eventStrength")\
                                            .fillna(average)
        
        return ratings
    
    
    def scheduler(self,ratings,path):
        latent_features=15
        learning_rate=0.001
        epochs=100
        instance=MatrixFactorization(ratings,latent_features,
                                     learning_rate,
                                     epochs,path=path)    
        instance.train()
        
        
            