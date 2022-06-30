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
unique_user_ids=None
unique_contentIds=None

class RankingModel(tf.keras.layers.Model):
    def __init__(self) -> None:
        super().__init__()
        embedding_dimension=32
        # Compute embeddings for users.
        self.user_embeddings =  tf.keras.Sequential([
                                tf.keras.layers.StringLookup(
                                vocabulary=unique_user_ids, mask_token=None),
                                tf.keras.layers.Embedding(len(unique_user_ids) + 1, 
                                  embedding_dimension)
                                ])
        # Compute embeddings for contents.
        self.item_embeddings =  tf.keras.Sequential([
                                tf.keras.layers.StringLookup(
                                vocabulary=unique_contentIds, mask_token=None),
                                tf.keras.layers.Embedding(len(unique_contentIds) + 1, 
                                                          embedding_dimension)
                                ])
        
        # Compute predictions.
        self.ratings =  tf.keras.Sequential([
                        # Learn multiple dense layers.
                        tf.keras.layers.Dense(256, activation="relu"),
                        tf.keras.layers.Dense(64, activation="relu"),
                        # Make rating predictions in the final layer.
                        tf.keras.layers.Dense(1)
                        ])
    def call(self, inputs):
        userId, contentId = inputs

        user_embedding = self.user_embeddings(userId)
        movie_embedding = self.item_embeddings(contentId)

        return self.ratings(tf.concat([user_embedding, movie_embedding], axis=1))


    
    