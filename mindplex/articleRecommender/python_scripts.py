import csv
import pandas as pd 

import numpy as np # 
#Article database python scripts
# df=pd.read_csv("articles.csv")
# with open("articles.csv") as article:
# ...:     reader=csv.reader(article)
# ...:     for index,row in enumerate(reader):
# ...:         Article.objects.get_or_create(
# ...:         authorId=row[5],
# ...:         authorResidence=row[2],
# ...:         communtId=row[6],
# ...:         content=row[4],
# ...:         contentId=row[1],
# ...:         source=row[7],
# ...:         timestamp=1.2*9,
# ...:         title=row[3])

df = pd.read_csv("interactions.csv")
print(df.shape)
print(df.columns)
print(df.eventType.unique())

# ['VIEW' 'FOLLOW' 'BOOKMARK' 'LIKE' 'COMMENT CREATED']
# print(df.eventType.unique())

# userId=models.CharField(max_length=100,default='')
#     location=models.CharField(max_length=100)
#     eventType=models.CharField(max_length=100,choices=CHOiCES ,default='')
#     contentId=models.ForeignKey(Article, db_column='contentId',on_delete=models.CASCADE)
#     communityId=models.CharField(max_length=100)
#     source=models.CharField(max_length=100,default='')
#     timestamp=models.IntegerField(default=0)
# df["eventType"]=df.eventType.map({"VIEW":"VIEW","LIKE":"LIKE","FOLLOW":"FOLLOW","BOOKMARK":"COMMENT-BEST-POSITIVE","COMMENT CREATED":"COMMENT-AVERAGE-POSITIVE"})
# df=df[["timestamp","eventType","contentId","personId"]]
# source=["Wikipedia","Google","Facebook","Instagram","LinkedIn","Yahoo"]
# df["source"]=np.random.choice(source,72312)
# location=["Ethiopia","America","England","Japan","German","Eritrea"]
# df["location"]=np.random.choice(location,72312)
# df["communityId"]=np.random.randint(12345,45678,72312)
# id_range=list(range(100))
# df["contentId"]=np.random.choice(id_range,72312) #Because it is a foreing key field
# pd.DataFrame.to_csv(df[:100],'interactions.csv',index=False)
print(df.shape)
print(df.columns)
print(df.head())

#interactions database script
# In [20]: with open("interactions.csv") as interact:
#     ...:     reader=csv.reader(interact)
#     ...:     pk=1
#     ...:     for index,row in enumerate(reader):
#     ...:         pk+=1
#     ...:         if pk>=25:
#     ...:             pk=1
#     ...:         Interactions.objects.get_or_create(
#     ...:         userId=row[3],
#     ...:         location=row[5],
#     ...:         eventType=row[1],
#     ...:         contentId=Article.objects.get(id=pk),
#     ...:         communityId=row[6],
#     ...:         source=row[4],
#     ...:         timestamp=123*index,
#     ...:         )
#     ...: 
#     ...: 
# id
# authorId
# authorResidence
# communtId
# content
# contentId
# source
# timestamp
# title
# {"userId"
# "location"
# "eventType" 
# "contentId" 
# "communityId"
# "source" 
# "timestamp"
# } 
