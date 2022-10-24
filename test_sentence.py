from TextFeatureSelection import TextFeatureSelection

#Multiclass classification problem
input_doc_list=['i am very happy','i just had an awesome weekend','this is a very difficult terrain to trek. i wish i stayed back at home.','i just had lunch','Do you want chips?']
target=['Positive','Positive','Negative','Neutral','Neutral']
fsOBJ=TextFeatureSelection(target=target,input_doc_list=input_doc_list)
result_df=fsOBJ.getScore()
print(result_df)


#Binary classification
input_doc_list=['i am content with this location','i am having the time of my life','you cannot learn machine learning without linear algebra','i want to go to mars']
target=[1,1,0,1]
fsOBJ=TextFeatureSelection(target=target,input_doc_list=input_doc_list)
result_df=fsOBJ.getScore()
print(result_df)
