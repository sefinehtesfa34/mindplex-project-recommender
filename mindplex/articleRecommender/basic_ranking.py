import pandas as pd 
import numpy as np 
import tensorflow as tf 
from articleRecommender.tensorflow_dataset import ListofRatings

class BasicRanking:
    
    def __init__(self,data:pd.DataFrame) -> None:
        self.data=data
        self.unique_userIds_and_contentIds()
        
    def dataFrame_to_dict(self):
        return self.data.to_dict("list")

    def createTfds(self):
        ratings_to_dict=self.dataFrame_to_dict()
        return tf.data.Dataset.from_tensor_slices(ratings_to_dict) 
    def unique_userIds_and_contentIds(self):
        unique_userIds=[]
        unique_contentIds=[] 
        ratings=self.createTfds()
        instance=ListofRatings(ratings)
        ratings=instance.returnListOfRatings()
        
        for rating in ratings:
            unique_userIds.append(rating["userId"].decode("utf-8"))
            unique_contentIds.append(rating["contentId"].decode("utf-8"))
        
        self.unique_content_ids=np.unique(unique_contentIds)
        self.unique_user_ids =np.unique(unique_userIds)        
        self.total_ratings=self.createTfds() 








