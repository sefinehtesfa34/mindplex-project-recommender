from . import views
from django.urls import path


urlpatterns = [
    path('article/',views.ArticleView.as_view(),name='article'),
    path('article/<str:authorId>/',views.ArticleView.as_view()),
    path('interact/',views.InteractionsView.as_view()),
    path('interact/<str:userId>/',views.InteractionsView.as_view()),
    path('recommend/<str:userId>/',views.PopularityRecommenderView.as_view()),
    path('content-based/<str:userId>/',views.ContentBasedRecommenderView.as_view()),
    ]
