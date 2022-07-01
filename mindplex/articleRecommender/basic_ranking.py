import pandas as pd 
import numpy as np 
import tensorflow as tf 
import tensorflow_recommenders as tfrs 
from typing import Dict,Text
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



tf.random.set_seed(42)
ratings=None
shuffled = ratings.shuffle(10, seed=42, reshuffle_each_iteration=False)
train = shuffled.take(80)
test = shuffled.skip(80).take(20)

unique_user_ids=None
unique_contentIds=None
task =  tfrs.tasks.Ranking(
        loss = tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.RootMeanSquaredError()]
        )

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


    
class RatingsBaseModel(tfrs.models.Model):
  def __init__(self):
    super().__init__()
    self.ranking_model: tf.keras.Model = RankingModel()
    self.task: tf.keras.layers.Layer = task

  def call(self, features: Dict[str, tf.Tensor]) -> tf.Tensor:
    return self.ranking_model(
        (features["userId"], features["contentId"]))

  def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
    labels = features.pop("rating")
    rating_predictions = self(features)

    # The task computes the loss and the metrics.
    return self.task(labels=labels, predictions=rating_predictions)

model = RatingsBaseModel()
model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.1))

cached_train = train.shuffle(10).batch(5).cache()
cached_test = test.batch(5).cache()
model.fit(cached_train, epochs=3)
model.evaluate(cached_test, return_dict=True)
tf.saved_model.save(model, "export")



