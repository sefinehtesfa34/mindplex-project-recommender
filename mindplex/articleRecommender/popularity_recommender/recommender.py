class PopularityRecommender:
    
    def __init__(self, popularity_df, items_df=None):
        self.popularity_df = popularity_df
        self.compute_popular_items()
        self.items_df = items_df
        
    def compute_popular_items(self):
        self.popularity_df=self.popularity_df.groupby('contentId')['eventStrength']\
                                    .sum()\
                                    .sort_values(ascending=False)\
                                    .reset_index()
        
    def recommend_items(self, topn=10):
        recommendations_df = self.popularity_df\
                               .sort_values('eventStrength', ascending = False) \
                               .head(topn)

        return recommendations_df
    