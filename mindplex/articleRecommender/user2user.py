import pickle
import numpy as np
from django_pandas.io import read_frame

from articleRecommender.matrixfactorization import MatrixFactorization
class User2UserBased:
    def __init__(self,path) -> None:
        self.path=path
          
    def preprocessor(self,interactions,eventStrength):
    
        interactions_df=read_frame(interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        
        interactions_df['eventType'] = interactions_df['eventType'].apply(lambda x: eventStrength.get(x,0))
        interactions_df=interactions_df.rename(columns={"eventType":"eventStrength"})
        interactions_df=interactions_df.iloc[1:,:]
        average=interactions_df["eventStrength"].mean()
        ratings=interactions_df.pivot_table(index="userId",
                                            columns="contentId",
                                            values="eventStrength")\
                                            .fillna(average)
        self.ratings=ratings 
        return ratings
    
    
    def scheduler(self):
        latent_features=15
        learning_rate=0.001
        epochs=100
        
        
        instance=MatrixFactorization(self.ratings,latent_features,
                                     learning_rate,
                                     epochs,path=self.path)    
        instance.train()
    def top_10_content_ids_finder(self,
                   user_uninteracted_content_ids,
                   similar_user_ids,
                   mapping_userId_to_index,
                   userId,
                   user_to_user_similarity,
                   ratings
                   ):
        average_ratings={}
        for content_id in user_uninteracted_content_ids:
            total_rating=0
            temp=0
            for user_id in similar_user_ids:
                rating=ratings.loc[user_id,content_id]
                temp+=rating 
                index1=mapping_userId_to_index[userId]
                index2=mapping_userId_to_index[user_id]
                
                
                try:
                    similarity_score=user_to_user_similarity[(index1,index2)]
                except:
                    similarity_score=user_to_user_similarity[(index2,index1)]
                total_rating+=(rating*similarity_score)
                
                
            weighted_average=total_rating/temp 
            average_ratings[content_id]=weighted_average
        top_10=sorted(average_ratings.items(),key=lambda x:x[1])[:10]
        top_10_content_ids=[content_id for content_id,rating in top_10]
        return top_10_content_ids
    
        
            