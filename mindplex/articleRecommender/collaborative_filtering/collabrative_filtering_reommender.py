import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from keras.layers import Dense,Input,Embedding,Flatten,Dot,Concatenate
from keras.models import Model
from sklearn.model_selection import train_test_split
import tensorflow as tf 
import numpy as np 
class CollaborativeFiltering:
    def __init__(self,users_interaction_df,userId) -> None:
        self.users_interaction_df=users_interaction_df
        self.userId=userId
        self.model_trainer()
    def model_trainer(self):        
        contentId_to_int={contentId:index for index,contentId in enumerate(set(self.users_interaction_df.contentId))}
        int_to_contentId={index:contentId for index,contentId in enumerate(set(self.users_interaction_df.contentId))}
        userId_to_int={userId:index for index,userId in enumerate(set(self.users_interaction_df.userId))}
        
        self.users_interaction_df.contentId=self.users_interaction_df.contentId.apply(lambda x: contentId_to_int[x])
        self.users_interaction_df.userId=self.users_interaction_df.userId.apply(lambda x:userId_to_int[x])
        
        train, test = train_test_split(\
            self.users_interaction_df, \
            test_size=0.2, \
            random_state=42)
        
        n_items=len(list(set(self.users_interaction_df.contentId.unique())))
        n_users=len(list(set(self.users_interaction_df.index.unique())))
        
        users_input = Input(shape=[1], name="self.users_interaction_df-Input")
        self.users_interaction_df_embedding = Embedding(\
                    n_items+1, 5, \
                    name="self.users_interaction_df-Embedding")\
                    (users_input)
                    
        self.users_interaction_df_vec = Flatten(name="Flatten-self.users_interaction_df")(self.users_interaction_df_embedding)
        user_input = Input(shape=[1], name="User-Input")
        user_embedding = Embedding(n_users+1, 5, name="User-Embedding")(user_input)
        user_vec = Flatten(name="Flatten-Users")(user_embedding)
        concatenated = Concatenate()([self.users_interaction_df_vec, user_vec])
        fully_con1 = Dense(256, activation='relu')(concatenated)
        fully_con2 = Dense(128, activation='relu')(fully_con1)
        fully_con3 = Dense(128, activation='relu')(fully_con2)
        out = Dense(1)(fully_con3)
        
        model = Model([user_input, users_input], out)
        model.compile(optimizer='adam',loss="mse",metrics="accuracy")
        history = model.fit([train.userId, train.contentId], train.eventStrength, epochs=10, verbose=1)
        #Here we can save the model when it perfoms well after retrain it.
        model.evaluate([test.userId, test.contentId], test.eventStrength)
        users_interactions = np.array(list(set(self.users_interaction_df.contentId)))
        
        id_user = userId_to_int[self.userId]
        
        user = np.array([id_user for _ in range(len(users_interactions))])
        predictions = model.predict([user, users_interactions])
        
        predictions = np.array([a[0] for a in predictions])
        
        self.recommended_ids = (-predictions).argsort()[:10]
        
        self.recommended_ids=[int_to_contentId[x] for x in self.recommended_ids]
        
        