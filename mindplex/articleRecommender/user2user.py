class User2UserBased:
    def __init__(self,path) -> None:
        self.path=path
            
    def top_10_content_ids_finder(self,
                   user_uninteracted_content_ids,
                   similar_user_ids,
                   mapping_userId_to_index,
                   userId,
                   user_to_user_similarity,
                   ratings
                   ):
        average_ratings={}
        for content_id in user_uninteracted_content_ids:
            total_rating=0
            temp=0
            for user_id in similar_user_ids:
                rating=ratings.loc[user_id,content_id]
                if rating==0:continue
                temp+=rating 
                index1=mapping_userId_to_index[userId]
                index2=mapping_userId_to_index[user_id]
                try:
                    similarity_score=user_to_user_similarity[(index1,index2)]
                except:
                    similarity_score=user_to_user_similarity[(index2,index1)]
                total_rating+=(rating*similarity_score)
                
                
            weighted_average=total_rating/temp 
            average_ratings[content_id]=weighted_average
        top_10=sorted(average_ratings.items(),key=lambda x:x[1])[:10]
        top_10_content_ids=[content_id for content_id,rating in top_10]
        return top_10_content_ids
    
        
            