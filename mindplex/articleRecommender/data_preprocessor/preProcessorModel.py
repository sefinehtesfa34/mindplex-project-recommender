from sklearn.model_selection import train_test_split
import math

from articleRecommender.popularity_recommender.recommender import PopularityRecommender
class PreprocessingModel:
    def __init__(self,interactions_df,article_df,eventStrength,flag=None):
        self.eventStrength=eventStrength
        self.interactions_df=interactions_df
        self.article_df=article_df
        
        self.preporcessor()
        self.recommended=None
        self.flag=flag
        if self.flag=="popularity":
            self.popularity_model=PopularityRecommender(self.interactions_df,self.article_df)
        
        
    def recommend(self):
        if self.flag=='popularity':
            recommended_items=self.popularity_model.recommend_items()
                
        return recommended_items 
    def preporcessor(self):
        self.interactions_df['eventStrength'] = self.interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x,0))
        def smooth_user_preference(x):
            return math.log(1+x, 2)
    
        
        self.interactions_df = self.interactions_df \
                    .groupby(['userId', 'contentId'])['eventStrength'].sum().apply(smooth_user_preference).reset_index()
        
    def trainTestSpliter(self):
        interactions_train_df, interactions_test_df = train_test_split(self.interactions_df,
                                 
                                   test_size=0.20,
                                   random_state=42,
                                )
        
        self.interactions_full_indexed_df = self.interactions_df.set_index('userId')
        self.interactions_train_indexed_df = interactions_train_df.set_index('userId')
        self.interactions_test_indexed_df = interactions_test_df.set_index('userId')
        

        return interactions_train_df,interactions_test_df
    
        
                
        
class PopularityRecommender:
    
    MODEL_NAME = 'Popularity'
    
    def __init__(self, popularity_df, items_df=None):
        self.popularity_df = popularity_df
        self.compute_popular_items()
        self.items_df = items_df
        
    def compute_popular_items(self):
        self.popularity_df=self.popularity_df.groupby('contentId')['eventStrength']\
                                    .sum()\
                                    .sort_values(ascending=False)\
                                    .reset_index()
        
    def get_model_name(self):
        return self.MODEL_NAME
        
    def recommend_items(self, topn=10, verbose=False):
        print(self.popularity_df)
        recommendations_df = self.popularity_df\
                               .sort_values('eventStrength', ascending = False) \
                               .head(topn)['contentId']

        if verbose:
            if self.items_df is None:
                raise Exception('"items_df" is required in verbose mode')

            recommendations_df = recommendations_df.merge(\
                                    self.items_df, \
                                    how = 'left', 
                                    left_on = 'contentId', 
                                    right_on = 'contentId')[['eventStrength', 'contentId', 'title', 'url', 'lang']]


        return recommendations_df
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
               