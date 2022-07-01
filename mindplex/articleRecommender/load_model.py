import tensorflow as tf
class LoadModel:
  def __init__(self) -> None:
    self.model = tf.saved_model.load("exported_model")
