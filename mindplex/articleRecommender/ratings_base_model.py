from typing import Dict, Text
import tensorflow as tf
import tensorflow_recommenders as tfrs

from articleRecommender.ranking_model import RankingModel

task =  tfrs.tasks.Ranking(
        loss = tf.keras.losses.MeanSquaredError(),
        metrics=[tf.keras.metrics.RootMeanSquaredError()]
        )
 
class RatingsBaseModel(tfrs.models.Model):
  def __init__(self,unique_user_ids,unique_content_ids):
    super().__init__()
    self.ranking_model: tf.keras.Model = RankingModel(unique_user_ids=unique_user_ids,unique_content_ids=unique_content_ids)
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
