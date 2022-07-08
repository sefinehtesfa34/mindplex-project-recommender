import pickle
from typing import Any, OrderedDict
import numpy as np
import pandas as pd
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articleRecommender.collaborative_filtering.collabrative_filtering_reommender import CollaborativeFiltering
from articleRecommender.content_based.content_based_recommender import ContentBasedRecommender
from articleRecommender.item2item import Item2ItemBased
from articleRecommender.model_relearner import MatrixFactorization
from articleRecommender.models import Article, Interactions
from articleRecommender.data_preprocessor.preProcessorModel import PreprocessingModel
from articleRecommender.user2user import User2UserBased 
from .serializers import  ArticleContentIdSerializer, ArticleSerializer, ContentIdSerializer, InteractionsSerializer
from django_pandas.io import read_frame
import warnings
warnings.filterwarnings("ignore")

eventStrength={
            "LIKE":1.0,
            "VIEW":5.0,
            "FOLLOW":2.0,
            "UNFOLLOW":2.0,
            "DISLIKE":1.0,
            "REACT-POSITIVE":1.5,
            "REACT-NEGATIVE":1.5,
            "COMMENT-BEST-POSITIVE":3.0,
            "COMMENT-AVERAGE-POSITIVE":2.5,
            "COMMENT-GOOD-POSITIVE":2.0,
            "COMMENT-BEST-NEGATIVE":3.0,
            "COMMENT-AVERAGE-NEGATIVE":2.5,
            "COMMENT-GOOD-NEGATIVE":2.0,    
            }

class ArticleView(APIView,PageNumberPagination):
    def get_object(self,authorId):
        try:
            return Article.objects.filter(authorId=authorId)
        except Article.DoesNotExist:
            return Http404
    
    def get(self,request,authorId=None,format=None):
        if authorId:
            article=self.get_object(authorId)
            if article is not Http404:
                result=self.paginate_queryset(article,request,view=self)
                
                serializer=ArticleSerializer(result,many=True)
                return self.get_paginated_response(serializer.data)
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        article=Article.objects.all()
        result=self.paginate_queryset(article,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        return self.get_paginated_response(serializer.data)
    
    
    def post(self,request,format=None):
        serializer=ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,authorId,format=None):
        article=self.get_object(authorId)
        serializer=ArticleSerializer(article,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, authorId, format=None):
        snippet = self.get_object(authorId)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

                
            
class InteractionsView(APIView,PageNumberPagination):
    def get_object(self,userId):
        try:
            return Interactions.objects.filter(userId=userId)
        except Interactions.DoesNotExist:
            return Http404
    
    def post(self,request,format=None):
        serializer=InteractionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,userId,format=None):
        article=self.get_object(userId)
        serializer=InteractionsSerializer(article,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, userId, format=None):
        snippet = self.get_object(userId)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    def get(self,request,userId=None,format=None):
        if userId:
            article=self.get_object(userId)
            if article is not Http404:
                result=self.paginate_queryset(article,request,view=self)
                serializer=InteractionsSerializer(result,many=True)
                return self.get_paginated_response(serializer.data)
            return Response(status=status.HTTP_404_NOT_FOUND)
        article=Interactions.objects.all()
        
        result=self.paginate_queryset(article,request,view=self)
        serializer=InteractionsSerializer(result,many=True)    

        return self.get_paginated_response(serializer.data)
    
        
    def post(self,request,format=None):
        serializer=InteractionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
    def put(self,request,userId,format=None):
        article=self.get_object(userId)
        serializer=InteractionsSerializer(article,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,userId,format=None):
        article=self.get_object(userId)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
 
class PopularityRecommenderView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
        self.eventStrength=eventStrength
        
    def get_object(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
        
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    
    def get(self,request,userId,format=None):
        
        user_interact_contentId=self.get_object(userId)
        
        self.interactions=Interactions.objects.exclude(contentId__in=self.excluded_article_set)
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        interactions_df=interactions_df.set_index("userId")  
      
        self.article=Article.objects.exclude(pk__in=self.excluded_article_set)
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        self.preprocessingModel=PreprocessingModel(
            interactions_df,
            articles_df,
            self.eventStrength
            )
            
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
            
        self.recommended_items=self.preprocessingModel.recommend()
        
        recommended_articles=Article.objects.filter(contentId__in=list(self.recommended_items))
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        

        return self.get_paginated_response(serializer.data)

class ContentBasedRecommenderView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
        self.eventStrength=eventStrength
        
    def get_object(self,userId):
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    
    def get(self,request,userId,format=None):
        
        user_interact_contentId=self.get_object(userId)
        serializer=ContentIdSerializer(user_interact_contentId,many=True)
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        items_to_ignore=Article.objects.filter(pk__in=self.items_to_ignore).only("contentId")
        serializer=ArticleContentIdSerializer(items_to_ignore,many=True)
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        self.interactions=Interactions.objects.all()
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        interactions_df=interactions_df.set_index("userId")  
      
        self.article=Article.objects.all()
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        
        instance_for_content_based_recommeder=ContentBasedRecommender(
            articles_df,
            interactions_df,
            self.eventStrength,
            )
        
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        recommendations_df= instance_for_content_based_recommeder.build_user_profile(userId,items_to_ignore=self.items_to_ignore)
        recommended_articles=recommendations_df.contentId
        recommended_articles=Article.objects.filter(contentId__in=list(recommended_articles))    
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        
        return self.get_paginated_response(serializer.data)


class CollaborativeFilteringView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
    def get(self,request,userId):
        interactions=Interactions.objects.all()
        interactions_df=read_frame(interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        
        interactions_df['eventType'] = interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x,0))
        
        interactions_df=interactions_df.rename(columns={"eventType":"eventStrength"})
        
        collaborative=CollaborativeFiltering(interactions_df,userId=userId)
        recommended_items=collaborative.recommended_ids
        recommended_queryset=Article.objects.filter(contentId__in=recommended_items)
        
        result=self.paginate_queryset(recommended_queryset,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        
        return self.get_paginated_response(serializer.data)
class LocationBasedRecommenderUsingCF(APIView,PageNumberPagination):
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)
            self.eventStrength=eventStrength
            
        def get(self,request,userId):
            user_interactions=Interactions.objects.filter(userId=userId)
            serializer=InteractionsSerializer(user_interactions,many=True)
            location=serializer.data[0].get("location",None)
            if not location:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
            interactions=Interactions.objects.filter(location=location)
            interactions_df=read_frame(interactions,
                            fieldnames=[
                                "userId",
                                "eventType",
                                "contentId__contentId",
                                
                                ])
            
            interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
            interactions_df['eventType'] = interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x,0))
            interactions_df=interactions_df.rename(columns={"eventType":"eventStrength"})
            collaborative=CollaborativeFiltering(interactions_df,userId=userId)
            recommended_items=collaborative.recommended_ids
            recommended_queryset=Article.objects.filter(contentId__in=recommended_items)
            
            result=self.paginate_queryset(recommended_queryset,request,view=self)
            serializer=ArticleSerializer(result,many=True)    
            
            return self.get_paginated_response(serializer.data)
class LBRUsingCB(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
        self.eventStrength=eventStrength
        
    def get_object(self,userId):
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    
    
    def get(self,request,userId,format=None):
        
        user_interact_contentId=self.get_object(userId)
        user_interactions=Interactions.objects.filter(userId=userId)
        serializer=InteractionsSerializer(user_interactions,many=True)
        location=serializer.data[0].get("location",None)
        if not location:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.interactions=Interactions.objects.filter(location=location)
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        interactions_df=interactions_df.set_index("userId")  
      
        self.article=Article.objects.all()
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        
        instance_for_content_based_recommeder=ContentBasedRecommender(
            articles_df,
            interactions_df,
            self.eventStrength,
            )
        
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        recommended_articles=instance_for_content_based_recommeder.build_user_profile(userId)
        
        recommended_articles=Article.objects.filter(contentId__in=recommended_articles)
            
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        
        return self.get_paginated_response(serializer.data)
class LocationBasedRecommenderUsingPBR(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
        
        self.eventStrength=eventStrength
        
    def get_object(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
        
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    
    def get(self,request,userId,format=None):
        
        user_interact_contentId=self.get_object(userId)
        
        user_interactions=Interactions.objects.filter(userId=userId)
        serializer=InteractionsSerializer(user_interactions,many=True)
        location=serializer.data[0].get("location",None)
        if not location:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        self.interactions=Interactions.objects.exclude(contentId__in=self.excluded_article_set)\
                                                    & Interactions.objects.filter(location=location)
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
            
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
    
        self.article=Article.objects.exclude(pk__in=self.excluded_article_set)
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        self.preprocessingModel=PreprocessingModel(
            interactions_df,
            articles_df,
            self.eventStrength
            )
            
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
            
        self.recommended_items=self.preprocessingModel.recommend()
        
        recommended_articles=Article.objects.filter(contentId__in=list(self.recommended_items))
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        

        return self.get_paginated_response(serializer.data)
class User2UserView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
    
    def excludedArticles(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
        
    def mapper(self,ratings):
        mapping_userId_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_user_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_user_ids,mapping_userId_to_index
    
    
    def get(self,request,userId):
        path="similarityIndexWeights"
        similarity_path="similarity"
        ratings_path="ratingsWeight"
        
        self.excludedArticles(userId)
        
        user2user=User2UserBased(path)
        
        
        with open(ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)    
        with open(path,"rb") as weights:
            users_similarity_index,items_similarity_index=pickle.load(weights) 
        
        with open(similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_simialrity=pickle.load(similarity_file)
        
        mapping_index_to_user_ids,mapping_userId_to_index=self.mapper(ratings)
        index=mapping_userId_to_index.get(userId,None)
            
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        # In the sliced array below 1 is added to remove user to himself similarity
        similar_users_index=users_similarity_index[index][1:100]
        similar_user_ids=[]
        for index in similar_users_index:
            similar_user_ids.append(mapping_index_to_user_ids[index])
        
                
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
    
        content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
         
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
        
        
        
        
        top_10_content_ids=user2user.top_10_content_ids_finder(
                user_uninteracted_content_ids,
                similar_user_ids,
                mapping_userId_to_index,
                userId,
                user_to_user_similarity,
                ratings) 
        recommended_articles=Article.objects.filter(contentId__in=top_10_content_ids)
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        
        return self.get_paginated_response(serializer.data)
class Item2ItemBasedView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
    def excludedArticles(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
    def mapper(self,ratings):
        #The index of the ratings data frame would be item ids and the 
        # columns would be user ids
        # The values would be the rating
        
        mapping_item_id_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_item_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_item_ids,mapping_item_id_to_index
        
    def get(self,request,userId,contentId):
        path="similarityIndexWeights"
        similarity_path="similarity"
        ratings_path="ratingsWeight"
        
        self.excludedArticles(userId)
        item2item=Item2ItemBased(path)
        
        with open(ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)

        ratings=ratings.T
        with open(path,"rb") as weights:
            user_similarity,item_similarity=pickle.load(weights) 
        with open(similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_similarity=pickle.load(similarity_file)
        
        mapping_index_to_item_ids,mapping_itemId_to_index=self.mapper(ratings)
        index=mapping_itemId_to_index.get(contentId,None)
        
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        
        similar_items_index=item_similarity[index][:100]
        
        
        similar_item_ids=[]
        for index in similar_items_index:
            similar_item_ids.append(mapping_index_to_item_ids[index])
                 
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
        
        content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
             
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
        
        
        
        top_10_content_ids=item2item.top_10_content_ids_finder(
                user_uninteracted_content_ids,
                similar_item_ids,
                mapping_itemId_to_index,
                contentId,
                userId,
                item_to_item_similarity,
                ratings) 
        
        
        recommended_articles=Article.objects.filter(contentId__in=top_10_content_ids)
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)
        
        return self.get_paginated_response(serializer.data)
                
class LearnerView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
        self.interactions=Interactions.objects.all()
        self.ratings=None
    def preprocessor(self):
    
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(columns={"userId":"userId","eventType":"eventType","contentId__contentId":"contentId"})
        
        interactions_df['eventType'] = interactions_df['eventType'].apply(lambda x: self.eventStrength.get(x,0))
        interactions_df=interactions_df.rename(columns={"eventType":"eventStrength"})
        interactions_df=interactions_df.iloc[1:,:]
        average=interactions_df["eventStrength"].mean()
        ratings=interactions_df.pivot_table(index="userId",
                                            columns="contentId",
                                            values="eventStrength")\
                                            .fillna(average)
        self.ratings=ratings 
        
    def get(self,request):
        self.preprocessor()
        path="similarityIndexWeights"
        
        learner=MatrixFactorization(self.ratings,path=path)
        learner.train()
        return Response(status.HTTP_202_ACCEPTED)
    
    
    
class HybirdRecommenderView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
        
    def excludedArticles(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
    def userIdMapper(self,ratings):
        mapping_userId_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_user_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_user_ids,mapping_userId_to_index
            
    def itemIdMapper(self,ratings):
        #The index of the ratings data frame would be item ids and the 
        # columns would be user ids
        # The values would be the rating
        
        mapping_item_id_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_item_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_item_ids,mapping_item_id_to_index
    def get(self,request,userId,contentId):
        self.userId=userId
        self.contentId=contentId 
        self.path="similarityIndexWeights"
        self.similarity_path="similarity"
        self.ratings_path="ratingsWeight"
        self.excludedArticles(userId)    
        
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
        content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
             
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        self.user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]

        
        
        # If the contentId is None, this means the recommender 
        # is not item-item based, in this case it would be user-user based recommender
        
        top_5_content_ids_with_user2user=self.forUser2UserBased()[:5]
        top_5_content_ids_with_item2item=self.forItem2ItemBased()[:5]
        top_10_content_ids=top_5_content_ids_with_item2item+top_5_content_ids_with_user2user
        
        recommended_articles=Article.objects.filter(contentId__in=top_10_content_ids)
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)
        
        return self.get_paginated_response(serializer.data)
        
        
        
    def forItem2ItemBased(self):
        item2item=Item2ItemBased(self.path)
        
        with open(self.ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)

        ratings=ratings.T
        with open(self.path,"rb") as weights:
            user_similarity,item_similarity=pickle.load(weights) 
        with open(self.similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_similarity=pickle.load(similarity_file)
    
        mapping_index_to_item_ids,mapping_itemId_to_index=self.itemIdMapper(ratings)
        index=mapping_itemId_to_index.get(self.contentId,None)
        
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        
        similar_items_index=item_similarity[index][:100]
        
        
        similar_item_ids=[]
        for index in similar_items_index:
            similar_item_ids.append(mapping_index_to_item_ids[index])
        
        top_10_content_ids=item2item.top_10_content_ids_finder(
                self.user_uninteracted_content_ids,
                similar_item_ids,
                mapping_itemId_to_index,
                self.contentId,
                self.userId,
                item_to_item_similarity,
                ratings)
        return top_10_content_ids
     
    def forUser2UserBased(self):
        user2user=User2UserBased(self.path)
        
        
        with open(self.ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)
        with open(self.path,"rb") as weights:
            user_similarity,item_similarity=pickle.load(weights) 
        with open(self.similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_simialrity=pickle.load(similarity_file)
        mapping_index_to_user_ids,mapping_userId_to_index=self.userIdMapper(ratings)
        index=mapping_userId_to_index.get(self.userId,None)
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        similar_users_index=user_similarity[index][:100]
        similar_user_ids=[]
        for index in similar_users_index:
            similar_user_ids.append(mapping_index_to_user_ids[index])
                
        top_10_content_ids=user2user.top_10_content_ids_finder(
                self.user_uninteracted_content_ids,
                similar_user_ids,
                mapping_userId_to_index,
                self.userId,
                user_to_user_similarity,
                ratings) 
        
            
        return top_10_content_ids
    

class HybirdUser2UserAndContentBased(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
    def excludedArticles(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
    def userIdMapper(self,ratings):
        mapping_userId_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_user_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_user_ids,mapping_userId_to_index
            
    
    def get_object(self,userId):
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    def get(self,request,userId,format=None):
        user_interact_contentId=self.get_object(userId)
        serializer=ContentIdSerializer(user_interact_contentId,many=True)
        
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        items_to_ignore=Article.objects.filter(pk__in=self.items_to_ignore).only("contentId")
        serializer=ArticleContentIdSerializer(items_to_ignore,many=True)
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        self.interactions=Interactions.objects.all()
        
        self.interactions=Interactions.objects.all()
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(
            columns={
                "userId":"userId",
                "eventType":"eventType",
                "contentId__contentId":"contentId"
                }
            )
        interactions_df=interactions_df.set_index("userId")  
        self.article=Article.objects.all()
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        
        
        instance_for_content_based_recommeder=ContentBasedRecommender(
            articles_df,
            interactions_df,
            self.eventStrength,
            )
        
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.cb_recommendations_df=instance_for_content_based_recommeder.build_user_profile(userId,items_to_ignore=self.items_to_ignore)
        
        
        # User2user based recommender
    
        self.userId=userId
        self.path="similarityIndexWeights"
        self.similarity_path="similarity"
        self.ratings_path="ratingsWeight"
        self.excludedArticles(userId)    
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
        content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
        
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        self.user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        

        
        
        self.forUser2UserBased()
        #Combining the results by contentId
        recommendations_df = self.cb_recommendations_df.merge(self.cf_recommendations_df,
                                   how = 'outer', 
                                   left_on = 'contentId', 
                                   right_on = 'contentId').fillna(0.0)
        self.cb_ensemble_weight = 10.0
        self.cf_ensemble_weight = 100.0
        # print(self.cf_recommendations_df["eventStrengthCF"])
        # print(self.cb_recommendations_df["eventStrengthCB"])
        
        #Computing a hybrid recommendation score based on CF and CB scores
        recommendations_df['eventStrengthHybrid'] = (recommendations_df['eventStrengthCB'] * self.cb_ensemble_weight) \
                                     + (recommendations_df['eventStrengthCF'] * self.cf_ensemble_weight)
        print(recommendations_df['eventStrengthCB'] * self.cb_ensemble_weight)
        print(recommendations_df['eventStrengthCF'] * self.cf_ensemble_weight)
        #Sorting recommendations by hybrid score
        
        recommendations_df = recommendations_df.sort_values('eventStrengthHybrid', ascending=False).head(10)
        top_10_content_ids=recommendations_df.contentId
        
        # print(self.cf_recommendations_df)
        # print(self.cb_recommendations_df)
        
        print(recommendations_df["eventStrengthHybrid"])
        
        hybrid_recommended_articles=Article.objects.filter(contentId__in=top_10_content_ids)
        result=self.paginate_queryset(hybrid_recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)
        return self.get_paginated_response(serializer.data)
        
    def forUser2UserBased(self):
        user2user=User2UserBased(self.path)
        
        
        with open(self.ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)
        with open(self.path,"rb") as weights:
            user_similarity,item_similarity=pickle.load(weights) 
        with open(self.similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_simialrity=pickle.load(similarity_file)
        mapping_index_to_user_ids,mapping_userId_to_index=self.userIdMapper(ratings)
        index=mapping_userId_to_index.get(self.userId,None)
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        similar_users_index=user_similarity[index][:100]
        similar_user_ids=[]
        for index in similar_users_index:
            similar_user_ids.append(mapping_index_to_user_ids[index])
                
        top_10_content_ids=user2user.top_10_content_ids_finder(
                self.user_uninteracted_content_ids,
                similar_user_ids,
                mapping_userId_to_index,
                self.userId,
                user_to_user_similarity,
                ratings) 
        cf_recommendations={}
        for content_id in top_10_content_ids:
            cf_recommendations[content_id]=ratings.loc[self.userId,content_id]
        cf_recommendations_df=pd.DataFrame(cf_recommendations,index=["eventStrengthCF"],columns=top_10_content_ids).T 
        cf_recommendations_df=cf_recommendations_df.reset_index()
        self.cf_recommendations_df=cf_recommendations_df.rename(columns={"index":"contentId"})

class HybridItem2ItemAndContentBased(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.eventStrength=eventStrength
    def excludedArticles(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId).only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
    def itemIdMapper(self,ratings):
        #The index of the ratings data frame would be item ids and the 
        # columns would be user ids
        # The values would be the rating
        
        mapping_item_id_to_index=OrderedDict(zip(ratings.index,list(range(len(ratings.index)))))
        mapping_index_to_item_ids=OrderedDict(zip(list(range(len(ratings.index))),ratings.index))
        return mapping_index_to_item_ids,mapping_item_id_to_index
    
    def get_object(self,userId):
        
        try:
            return Interactions.objects.filter(userId=userId)
            
        except Interactions.DoesNotExist:
            return None 
    def get(self,request,userId,contentId,format=None):
        self.contentId=contentId
        self.userId=userId 
        user_interact_contentId=self.get_object(userId)
        serializer=ContentIdSerializer(user_interact_contentId,many=True)
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        items_to_ignore=Article.objects.filter(pk__in=self.items_to_ignore).only("contentId")
        serializer=ArticleContentIdSerializer(items_to_ignore,many=True)
        self.items_to_ignore=[]
        for dict_val in serializer.data:
            value=list(dict_val.values())[0]
            self.items_to_ignore.append(value)
        self.interactions=Interactions.objects.all()
        self.interactions=Interactions.objects.all()
        interactions_df=read_frame(self.interactions,
                        fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",
                            
                            ])
        interactions_df=interactions_df.rename(
            columns={
                "userId":"userId",
                "eventType":"eventType",
                "contentId__contentId":"contentId"
                }
            )
        
        interactions_df=interactions_df.set_index("userId")  
      
        self.article=Article.objects.all()
        articles_df=read_frame(self.article,fieldnames=[
            "authorId",
            "contentId",
            "content",
            "title"])
        
        
        instance_for_content_based_recommeder=ContentBasedRecommender(
            articles_df,
            interactions_df,
            self.eventStrength,
            )
        
        try:
            assert(user_interact_contentId)
        except AssertionError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        self.cb_recommendations_df=instance_for_content_based_recommeder.build_user_profile(userId,items_to_ignore=self.items_to_ignore)
        self.userId=userId
        self.path="similarityIndexWeights"
        self.similarity_path="similarity"
        self.ratings_path="ratingsWeight"
        self.excludedArticles(userId)    
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
        content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        content_ids=np.unique(content_ids).tolist()
             
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        self.user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]

        
        
        self.forItem2ItemBased() 
        recommendations_df = self.cb_recommendations_df.merge(self.cf_recommendations_df,
                                   how = 'outer', 
                                   left_on = 'contentId', 
                                   right_on = 'contentId').fillna(0.0)
        self.cb_ensemble_weight = 10.0
        self.cf_ensemble_weight = 100.0
        
        #Computing a hybrid recommendation score based on CF and CB scores
        recommendations_df['eventStrengthHybrid'] = (recommendations_df['eventStrengthCB'] * self.cb_ensemble_weight) \
                                     + (recommendations_df['eventStrengthCF'] * self.cf_ensemble_weight)
        
        #Sorting recommendations by hybrid score
        
        recommendations_df = recommendations_df.sort_values('eventStrengthHybrid', ascending=False).head(10)
        top_10_content_ids=recommendations_df.contentId
        print(recommendations_df)    
        
        hybrid_recommended_articles=Article.objects.filter(contentId__in=top_10_content_ids)
        result=self.paginate_queryset(hybrid_recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)
        return self.get_paginated_response(serializer.data)
        
        
    def forItem2ItemBased(self):
        item2item=Item2ItemBased(self.path)
        
        with open(self.ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)

        ratings=ratings.T
        with open(self.path,"rb") as weights:
            _,item_similarity=pickle.load(weights) 
        with open(self.similarity_path,"rb") as similarity_file:
            _,item_to_item_similarity=pickle.load(similarity_file)
    
        mapping_index_to_item_ids,mapping_itemId_to_index=self.itemIdMapper(ratings)
        index=mapping_itemId_to_index.get(self.contentId,None)
        
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        similar_items_index=item_similarity[index]
        
        similar_item_ids=[]
        for index in similar_items_index:
            similar_item_ids.append(mapping_index_to_item_ids[index])
        
        top_10_content_ids=item2item.top_10_content_ids_finder(
                self.user_uninteracted_content_ids,
                similar_item_ids,
                mapping_itemId_to_index,
                self.contentId,
                item_to_item_similarity,
                )
        cf_recommendations={}
        for content_id in top_10_content_ids:
            cf_recommendations[content_id]=ratings.loc[content_id,self.userId]
        cf_recommendations_df=pd.DataFrame(cf_recommendations,index=["eventStrengthCF"],columns=top_10_content_ids).T 
        cf_recommendations_df=cf_recommendations_df.reset_index()
        self.cf_recommendations_df=cf_recommendations_df.rename(columns={"index":"contentId"})

    
    
    
    
    
    
    
    
    