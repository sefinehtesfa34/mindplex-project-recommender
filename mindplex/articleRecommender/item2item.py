class Item2ItemBased:
    def __init__(self,path) -> None:
        self.path=path
    
    def top_10_content_ids_finder(self,
                   user_uninteracted_content_ids,
                   similar_item_ids,
                   mapping_itemId_to_index,
                   itemId,
                   userId,
                   item_to_item_similarity,
                   ratings
                   ):
        average_ratings={}
        for content_id in user_uninteracted_content_ids:
            total_rating=0
            temp=0
            for item_id in similar_item_ids:
                rating=ratings.loc[item_id,userId]
                temp+=rating 
                index1=mapping_itemId_to_index[itemId]
                index2=mapping_itemId_to_index[item_id]
                
                
                try:
                    similarity_score=item_to_item_similarity[(index1,index2)]
                except:
                    similarity_score=item_to_item_similarity[(index2,index1)]
                total_rating+=(rating*similarity_score)
                
                
            weighted_average=total_rating/temp 
            average_ratings[content_id]=weighted_average
    

        top_10=sorted(average_ratings.items(),key=lambda x:x[1])[:10]
        top_10_content_ids=[content_id for content_id,rating in top_10]
        return top_10_content_ids
    
        
            