import pandas as pd 
import numpy as np 
import tensorflow as tf 
class BasicRanking:
    def __init__(self,data:pd.DataFrame) -> None:
        self.data=data
    def dataFrame_to_dict(self):
        return self.data.to_dict("list")
    
    def createTfds(self):
        ratings_to_dict=self.dataFrame_to_dict()
        return tf.data.Dataset.from_tensor_slices(ratings_to_dict) 
    def findUniqueUserIds(self):
        pass
    def findUniqueItems(self):
        pass 
     
    
    