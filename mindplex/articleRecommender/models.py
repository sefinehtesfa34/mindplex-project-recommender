from django.db import models

# class ArticleManager(models.Manager):
#     def get_by_natural_key(self, contentId):
#         return self.get(contentId=contentId)

class Article(models.Model):
    authorId=models.CharField(max_length=100)
    authorResidence=models.CharField(max_length=100)
    communtId=models.CharField(max_length=100)
    content=models.TextField()
    contentId=models.CharField(max_length=100)
    source=models.CharField(max_length=100,default='')
    timestamp=models.IntegerField() 
    title=models.CharField(max_length=100)
    
    # objects=ArticleManager()
    class Meta:
        ordering=["timestamp"]
    
    # def natural_key(self):
    #     return self.contentId
        
class Interactions(models.Model):
    CHOiCES=[
        ("LIKE","LIKE"),
        ("VIEW","VIEW"),
        ("UNCOMMENT","UNCOMMENT"),
        ("FOLLOW","FOLLOW"),
        ("UNFOLLOW","UNFOLLOW"),
        ("DISLIKE","DISLIKE"),
        ("REACT-POSITIVE","REACT-POSITIVE"),
        ("REACT-NEGATIVE","REACT-NEGATIVE"),
        ("COMMENT-BEST-POSITIVE","COMMENT-BEST-POSITIVE"),
        ("COMMENT-AVERAGE-POSITIVE","COMMENT-AVERAGE-POSITIVE"),
        ("COMMENT-GOOD-POSITIVE","COMMENT-GOOD-POSITIVE"),
        ("COMMENT-BEST-NEGATIVE","COMMENT-BEST-NEGATIVE"),
        ("COMMENT-AVERAGE-NEGATIVE","COMMENT-AVERAGE-NEGATIVE"),
        ("COMMENT-GOOD-NEGATIVE","COMMENT-GOOD-NEGATIVE")
    ]
    
    userId=models.CharField(max_length=100,default='')
    location=models.CharField(max_length=100)
    eventType=models.CharField(max_length=100,choices=CHOiCES ,default='')
    contentId=models.ForeignKey(Article, db_column='contentId',on_delete=models.CASCADE)
    communityId=models.CharField(max_length=100)
    source=models.CharField(max_length=100,default='')
    timestamp=models.IntegerField(default=0)
    class Meta:
        ordering=["timestamp"]
        unique_together=["userId","contentId","eventType"]


class RecommendationConfiguration(models.Model):
    communityId=models.UUIDField(max_length=100)
    highQuality=models.FloatField()
    content=models.TextField()
    pattern=models.FloatField()
    popularity=models.FloatField()
    random=models.FloatField() 
    timelines=models.FloatField()

    
    
    