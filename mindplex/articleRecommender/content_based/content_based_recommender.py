
import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import warnings
warnings.filterwarnings("ignore")
class ContentBasedRecommender:
    def __init__(self,articles_df,interactions_df,eventStrength) -> None:
        self.articles_df=articles_df
        self.interactions_df=interactions_df
        self.eventStrength=eventStrength
        stopwords_list = stopwords.words('english') + stopwords.words('portuguese')
        vectorizer = TfidfVectorizer(analyzer='word',
                     ngram_range=(1, 2),
                     min_df=0.003,
                     max_df=0.5,
                     max_features=5000,
                     stop_words=stopwords_list)

        self.item_ids = self.articles_df['contentId'].tolist()
        self.tfidf_matrix = vectorizer.fit_transform(\
                                                self.articles_df['title'] \
                                                + "" + self.articles_df['content'])
    
    def build_user_profile(self,userId,items_to_ignore=[],topn=10):
        #The assumption is that self.interactions_df is userId indexed dataframe
        user_interacted_contentId=self.interactions_df.loc[userId]["contentId"]
        user_profile=[]
        try:
            for contentId in user_interacted_contentId:
                index=self.item_ids.index(contentId)
                profile=self.tfidf_matrix[index:index+1]
                user_profile.append(profile)
        except ValueError:
            index=self.item_ids.index(user_interacted_contentId)
            profile=self.tfidf_matrix[index:index+1]
            user_profile.append(profile)
        user_profile= scipy.sparse.vstack(user_profile)
        self.interactions_df['eventStrength'] = self.interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x))
        
        self.eventStrength=np.array(self.interactions_df.loc[userId]["eventStrength"]).reshape(-1,1)
        user_item_strengths_weighted_avg = np.sum(user_profile\
                                    .multiply(self.eventStrength), axis=0) \
                                    / np.sum(self.eventStrength)
        user_profile_norm = sklearn.preprocessing.normalize(user_item_strengths_weighted_avg)
        cosine_similarities = cosine_similarity(user_profile_norm, self.tfidf_matrix)
        similar_indices = cosine_similarities.argsort().flatten()[-topn:]
        similar_items = sorted([(self.item_ids[index], cosine_similarities[0,index]) for index in similar_indices], 
                               key=lambda x: -x[1])
        
        similar_items_filtered = list(filter(lambda item: item[0] not in items_to_ignore, similar_items))
        recommendations_df = pd.DataFrame(similar_items_filtered, columns=['contentId', 'eventStrengthCB']) \
                                    .head(topn)
        self.recommendations_df=recommendations_df
        print(self.recommendations_df)
        # pandas.Series.argSort() returns the indices that sort the dataFrame.
        list_of_contentIds=[self.item_ids[index] for index in similar_indices ]
        return list_of_contentIds,recommendations_df

    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        