from . import views
from django.urls import path


urlpatterns = [
    path('article/',views.ArticleView.as_view(),name='article'),
    path('article/<str:authorId>/',views.ArticleView.as_view()),
    path('interact/',views.InteractionsView.as_view()),
    path('interact/<str:userId>/',views.InteractionsView.as_view()),
    path('popular/<str:userId>/',views.PopularityRecommenderView.as_view()),
    path('content-based/<str:userId>/',views.ContentBasedRecommenderView.as_view()),
    path("collaborative/<str:userId>/",views.CollaborativeFilteringView.as_view() ),
    path("LBR-collaborative/<str:userId>/",views.LocationBasedRecommenderUsingCF().as_view()),
    path("LBR-content-based/<str:userId>/",views.LBRUsingCB.as_view()),
    path("LBR-popular/<str:userId>/",views.LocationBasedRecommenderUsingPBR.as_view()),
    path("user-based/<str:userId>/",views.User2UserView.as_view()),
    path("ranking/<str:userId>/",views.RankingModelView.as_view()),
    path("item-based/<str:userId>/<str:contentId>/",views.Item2ItemBasedView.as_view())    
    ]

