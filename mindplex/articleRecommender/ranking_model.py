import tensorflow as tf

class RankingModel(tf.keras.Model):
      
      def __init__(self,unique_user_ids,unique_content_ids):
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
