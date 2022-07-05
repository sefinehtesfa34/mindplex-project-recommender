import pickle
import pandas as pd 
from typing import Any, OrderedDict
import numpy as np
from rest_framework.pagination import PageNumberPagination
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articleRecommender.basic_ranking import BasicRanking
from articleRecommender.collaborative_filtering.collabrative_filtering_reommender import CollaborativeFiltering
from articleRecommender.content_based.content_based_recommender import ContentBasedRecommender
from articleRecommender.item2item import Item2ItemBased
from articleRecommender.matrixfactorization import MatrixFactorization
from articleRecommender.models import Article, Interactions
from articleRecommender.data_preprocessor.preProcessorModel import PreprocessingModel
from articleRecommender.ratings_base_model import RatingsBaseModel
from articleRecommender.user2user import User2UserBased

from .serializers import  ArticleSerializer, ContentIdSerializer, InteractionsSerializer
from django_pandas.io import read_frame
import tensorflow as tf
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
        interactions_df.columns=["userId","eventType","contentId"]
        interactions_df=interactions_df.drop([0]).reset_index().drop(["index"],axis=1) 
        
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
        
        recommended_articles=instance_for_content_based_recommeder.build_user_profile(userId)
        
        recommended_articles=Article.objects.filter(contentId__in=recommended_articles)    
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
        
        # When we want to relearn the model, we have to uncomment these lines below.
        
        interactions=Interactions.objects.all()
        user2user.preprocessor(interactions,eventStrength)
        user2user.relearner()
        
        
        with open(ratings_path,"rb") as ratings_weight:
            ratings=pickle.load(ratings_weight)
        
        with open(path,"rb") as weights:
            user_similarity,item_similarity=pickle.load(weights) 
        
        with open(similarity_path,"rb") as similarity_file:
            user_to_user_similarity,item_to_item_simialrity=pickle.load(similarity_file)
        
        mapping_index_to_user_ids,mapping_userId_to_index=self.mapper(ratings)
        index=mapping_userId_to_index.get(userId,None)
            
        if index==None:
            return Response(status.HTTP_400_BAD_REQUEST)
        similar_users_index=user_similarity[index][:100]
        similar_user_ids=[]
        for index in similar_users_index:
            similar_user_ids.append(mapping_index_to_user_ids[index])
        
                
        self.user_uninteracted_items=Interactions.objects.exclude(contentId__in=self.excluded_article_set).only("contentId")
        serializer=ContentIdSerializer(self.user_uninteracted_items,many=True)
        
        content_ids=[list(contentId.values())[0] for contentId in serializer.data] 
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        
        
        
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
        
        content_ids=Article.objects.filter(pk__in=content_ids).only("contentId")
        serializer=ContentIdSerializer(content_ids,many=True)
        user_uninteracted_content_ids=[list(contentId.values())[0] for contentId in serializer.data]
        
        
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
                


    
class RankingModelView(APIView,PageNumberPagination):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
        
        self.eventStrength=eventStrength
        
    def get_object(self,userId):
        self.excluded_article=Interactions.objects.filter(userId=userId)\
                                            .only("contentId")
        serializer=ContentIdSerializer(self.excluded_article,many=True)
        self.excluded_article_set=set()
        for dict in serializer.data:
            self.excluded_article_set.add(list(dict.values())[0])
        
    def get(self,request,userId,format=None):
        self.get_object(userId)
        queryset=Interactions.objects.all()
        
        interactions_df=read_frame(queryset,fieldnames=[
                            "userId",
                            "eventType",
                            "contentId__contentId",                    
                            ]
                        )
        interactions_df=interactions_df.rename(columns={"userId":"userId",
                                                        "eventType":"rating",
                                                        "contentId__contentId":"contentId"})
        ratings=interactions_df.iloc[1:,:]
        ratings["rating"]=interactions_df["rating"]\
            .apply(lambda x:self.eventStrength.get(x,0))
        
        
        ranking = BasicRanking(ratings)
        
        total_ratings=ranking.total_ratings
        unique_user_ids=ranking.unique_user_ids
        unique_content_ids=ranking.unique_content_ids
        model = RatingsBaseModel(unique_user_ids=unique_user_ids, 
                                 unique_content_ids=unique_content_ids)
        
        
        tf.random.set_seed(42)
        
        shuffled = total_ratings.shuffle(10, seed=42, reshuffle_each_iteration=False)
        train = shuffled.take(80)
        test = shuffled.skip(80).take(20)

        cached_train = train.shuffle(10).batch(5).cache()
        cached_test = test.batch(5).cache()
        
        model.compile(optimizer=tf.keras.optimizers.Adagrad(learning_rate=0.001))
        model.fit(cached_train, epochs=3)
        model.evaluate(cached_test, return_dict=True)
        tf.saved_model.save(model, "exported_model")
        loaded = tf.saved_model.load("exported_model")

        # Make predictions
        
        # Loop over all items and filter the top 10 highest rating values
        all_content_ids=np.unique(ratings[~ratings["contentId"]\
            .isin(self.excluded_article_set)]["contentId"])
        
        predicted_ratings=[(loaded({"userId": np.array([userId]), 
                                    "contentId": [contentId]})\
                                        .numpy().tolist()[0],contentId) 
                                        for contentId in all_content_ids]
        top_10_highest_rating_values=sorted(predicted_ratings)[-10:]
        print(top_10_highest_rating_values)
        
        content_ids=[content_id[1] for content_id in top_10_highest_rating_values]
        recommended_articles=Article.objects.filter(contentId__in=content_ids)
        result=self.paginate_queryset(recommended_articles,request,view=self)
        serializer=ArticleSerializer(result,many=True)    
        

        return self.get_paginated_response(serializer.data)
        