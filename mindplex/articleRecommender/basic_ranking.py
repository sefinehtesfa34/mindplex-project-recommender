import pandas as pd 
import numpy as np 
import tensorflow as tf 
import tensorflow_recommenders as tfrs 
from typing import Dict,Text
from articleRecommender.tensorflow_dataset import ListofRatings


unique_user_ids=None
unique_content_ids=None
total_ratings =None

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
        global unique_content_ids
        global unique_user_ids
        global total_ratings
        
        ratings=self.createTfds()
        instance=ListofRatings(ratings)
        ratings=instance.returnListOfRatings()
        
        for rating in ratings:
            unique_userIds.append(rating["userId"].decode("utf-8"))
            unique_contentIds.append(rating["contentId"].decode("utf-8"))
        
        unique_content_ids=np.unique(unique_contentIds)
        unique_user_ids =np.unique(unique_userIds)
                
        total_ratings=self.createTfds() 



tf.random.set_seed(42)
shuffled = total_ratings.shuffle(10, seed=42, reshuffle_each_iteration=False)
train = shuffled.take(80)
test = shuffled.skip(80).take(20)

task =  tfrs.tasks.Ranking(
        loss = tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.RootMeanSquaredError()]
        )

class RankingModel(tf.keras.Model):
      
      def __init__(self):
        super().__init__()
        embedding_dimension = 32
        # Compute embeddings for users.
        self.user_embeddings = tf.keras.Sequential([
          tf.keras.layers.StringLookup(
            vocabulary=unique_user_ids, mask_token=None),
          tf.keras.layers.Embedding(len(unique_user_ids) + 1, embedding_dimension)
        ])
    
        # Compute embeddings for movies.
        self.item_embeddings = tf.keras.Sequential([
          tf.keras.layers.StringLookup(
            vocabulary=unique_content_ids, mask_token=None),
          tf.keras.layers.Embedding(len(unique_content_ids) + 1, embedding_dimension)
        ])
    
        # Compute predictions.
        self.ratings = tf.keras.Sequential([
          # Learn multiple dense layers.
          tf.keras.layers.Dense(256, activation="relu"),
          tf.keras.layers.Dense(64, activation="relu"),
          # Make rating predictions in the final layer.
          tf.keras.layers.Dense(1)
      ])
    
      def call(self, inputs):
    
        user_ids,content_ids = inputs
    
        user_embedding = self.user_embeddings(user_ids)
        item_embedding = self.item_embeddings(content_ids)
    
        return self.ratings(tf.concat([user_embedding, item_embedding], axis=1))
      

class RatingsBaseModel(tfrs.models.Model):
  def __init__(self):
    super().__init__()
    self.ranking_model: tf.keras.Model = RankingModel()
    self.task: tf.keras.layers.Layer = task

  def call(self, features: Dict[str, tf.Tensor]) -> tf.Tensor:
    return self.ranking_model(
                (features["userId"], features["contentId"])
                )  
  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    labels = features.pop("rating")
    # call() is called using self(features) 
    rating_predictions = self(features)

    # The task computes the loss and the metrics.
    return self.task(labels=labels, predictions=rating_predictions)






