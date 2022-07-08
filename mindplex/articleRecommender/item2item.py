class Item2ItemBased:
    def __init__(self,path) -> None:
        self.path=path
    
    def top_10_content_ids_finder(self,
                   user_uninteracted_content_ids,
                   similar_item_ids,
                   mapping_itemId_to_index,
                   itemId,
                   item_to_item_similarity,
                   ):
        
        similarity_scores=[]
        user_uninteracted_content_ids=set(user_uninteracted_content_ids)
        for item_id in similar_item_ids:
            if item_id not in user_uninteracted_content_ids:continue
            index1=mapping_itemId_to_index[item_id]
            index2=mapping_itemId_to_index[itemId]
            try:
                similarity_score=item_to_item_similarity[(index1,index2)] 
            except:
                similarity_score=item_to_item_similarity[(index2,index1)]
            similarity_scores.append((similarity_score,item_id))
        similarity_score=sorted(similarity_scores,reverse=True)
        top_10_content_ids=[content_id for _,content_id in similarity_scores[:10]]
        return top_10_content_ids
    