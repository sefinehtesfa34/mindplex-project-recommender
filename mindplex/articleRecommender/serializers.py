
from attr import fields
from rest_framework import serializers
from .models import Article,Interactions
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Article
        fields='__all__'

class InteractionsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Interactions
        fields='__all__'
        
class ContentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model=Interactions
        fields=['contentId']

class ArticleContentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model=Article
        fields=["contentId"]
    
        



