#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib
matplotlib.rcParams["figure.figsize"] = (20,10)


# In[3]:


df1 = pd.read_csv("C:\\Users\\prras\\Downloads\\archive (1)\\Bengaluru_House_Data.csv")
df1.head()


# In[4]:


df1.shape


# In[339]:


#data cleaning


# In[5]:


df1.groupby('area_type')['area_type'].agg('count')


# In[6]:


df2 = df1.drop(['area_type','availability','society'],axis='columns')
df2.head()


# In[7]:


df2.isnull().sum()


# In[8]:


df3 = df2.dropna()
df3.isnull().sum()


# In[9]:


df3['balcony'].unique()


# In[10]:


df3['price'].unique()


# In[11]:


df3['size'].unique()


# In[12]:


df3['bhk'] = df3['size'].apply(lambda x: int(x.split(' ')[0])) 


# In[13]:


df3.head()


# In[14]:


df3['bhk'].unique()


# In[15]:


df3[df3.bhk>20]


# In[16]:


df3.total_sqft.unique()


# In[17]:


def is_float(x):
    try:
        float(x)
    except:
     return False
    return True
    
    


# In[18]:


df3[~df3['total_sqft'].apply(is_float)].head(10)


# In[19]:


len(df3.location.unique())


# In[20]:


def convert_sqft_to_num(x):
    tokens = x.split('-')
    if len(tokens) == 2:
        return (float(tokens[0])+float(tokens[1]))/2
    try:
        return float(x)
    except:
        return None


# In[21]:


convert_sqft_to_num('2166')


# In[22]:


convert_sqft_to_num('2100-2850')


# In[23]:


convert_sqft_to_num('34.46sq.Meter')


# In[24]:


df4 = df3.copy()


# In[25]:


df4['total_sqft'] = df4 ['total_sqft'].apply(convert_sqft_to_num)


# In[26]:


df4.head(3)


# In[27]:


df4.loc[30]


# In[28]:


(2100+2850)/2


# In[29]:


df4.head(3)


# In[30]:


#feature enginerring and dimentionality reduction

df5 = df4.copy(1)
df5['price_per_sqft'] = df5['price']*100000/df5['total_sqft']
df5.head()


# In[31]:


len(df5.location.unique())


# In[32]:


df5.location = df5.location.apply(lambda x: x.strip())
location_stats = df5.groupby('location')['location'].agg('count').sort_values(ascending=False)
location_stats


# In[33]:


len(location_stats[location_stats<=10])


# In[34]:


location_stats_less_than_10 = location_stats[location_stats<=10]
location_stats_less_than_10


# In[35]:


len(df5.location.unique())


# In[36]:


df5.location = df5.location.apply(lambda x: 'other' if x in location_stats_less_than_10 else x)


# In[37]:


len(df5.location.unique())


# In[38]:


df5.head(10)


# In[39]:


#outlier detection and removal 

df5[df5.total_sqft/df5.bhk<300].head()


# In[40]:


df5.shape


# In[41]:


df6 = df5[~(df5.total_sqft/df5.bhk<300)]
df6.shape


# In[42]:


df6.price_per_sqft.describe()


# In[43]:


def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft)
        st = np.std(subdf.price_per_sqft)
        reduced_df = subdf[(subdf.price_per_sqft>(m-st)) & (subdf.price_per_sqft<=(m+st))]
        df_out = pd.concat([df_out,reduced_df],ignore_index=True)
    return df_out


# In[44]:


df7 = remove_pps_outliers(df6)
df7.shape
    
    


# In[45]:


def plot_scatter_chart(df,location):
    bhk2 = df[(df.location==location) & (df.bhk==2)]
    bhk3 = df[(df.location==location) & (df.bhk==3)]
    matplotlib.rcParams['figure.figsize'] = (15, 10)
    plt.scatter(bhk2.total_sqft,bhk2.price_per_sqft,color='blue',label='2 BHK', s=50)
    plt.scatter(bhk3.total_sqft,bhk3.price_per_sqft,marker='+',color='green',label='3 BHK',s=50)
    plt.xlabel("Total Square Feet Area")
    plt.ylabel("Price")
    plt.title(location)
    plt.legend()
    
plot_scatter_chart(df7,"Marathahalli")


# In[46]:


df7.price_per_sqft.describe()


# In[ ]:





# In[47]:


def remove_bhk_outlier(df):
    exclude_indices = np.array([])
    for location, location_df in df.groupby('location'):
        bhk_stats = {}
        for bhk, bhk_df in location_df.groupby('bhk'):
            bhk_stats[bhk] = {
                'mean': np.mean(bhk_df.price_per_sqft),
                'std' : np.std(bhk_df.price_per_sqft),
                'count': bhk_df.shape[0]
            }
        for bhk, bhk_df in location_df.groupby('bhk'):
            stats = bhk_stats.get(bhk-1)
            if stats and stats['count']>5:
                exclude_indices = np.append(exclude_indices, bhk_df[bhk_df.price_per_sqft<(stats['mean'])].index.values)
    return df.drop(exclude_indices,axis= 'index')


# In[48]:


df8 = remove_bhk_outlier(df7)
df8.shape


# In[49]:


plot_scatter_chart(df8,"Marathahalli")


# In[ ]:





# In[50]:


import matplotlib
matplotlib.rcParams["figure.figsize"] = (20,10)
plt.hist(df8.price_per_sqft,rwidth=0.8)
plt.xlabel("Price Per Square Feet")
plt.ylabel("Count")


# In[51]:


df8.bath.unique()


# In[52]:


df8[df8.bath>8]


# In[53]:


plt.hist(df8.bath,rwidth=0.8)
plt.xlabel("Number of nathrooms")
plt.ylabel("Count")


# In[ ]:





# In[54]:


df8[df8.bath>df8.bhk+2]


# In[55]:


df9 = df8[df8.bath<df8.bhk+2]
df9.shape


# In[56]:


df10 = df9.drop(['size','balcony','price_per_sqft'],axis='columns')
df10.head()


# In[57]:


df10.head(3)


# In[58]:


#building a machine learning model

pd.get_dummies(df10.location)


# In[59]:


dummies = pd.get_dummies(df10.location)
dummies.head(3)


# In[60]:


df11 = pd.concat([df10,dummies.drop('other',axis='columns')],axis='columns')
df11.head(3)


# In[61]:


df12 = df11.drop('location',axis='columns')
df12.head(2)


# In[62]:


df12.shape


# In[63]:


X = df12.drop('price',axis='columns')
X.head()


# In[64]:


y = df12.price
y.head() 


# In[65]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2,random_state=10)


# In[66]:


from sklearn.linear_model import LinearRegression
lr_clf = LinearRegression()
lr_clf.fit(X_train,y_train)
lr_clf.score(X_test,y_test)


# In[67]:


from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_score

cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)

cross_val_score(LinearRegression(), X, y, cv=cv)


# In[68]:


from sklearn.model_selection import GridSearchCV

from sklearn.linear_model import Lasso
from sklearn.tree import DecisionTreeRegressor

regressor = DecisionTreeRegressor()


# In[69]:


#hyper parameter testing 


from sklearn.linear_model import LinearRegression, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV

def find_best_model_using_gridsearchcv(X, y):
    algos = {
        'linear_regression': {
            'model': LinearRegression(),
            'params': {
                'normalize': [True, False]
            }
        },
        'lasso': {
            'model': Lasso(),
            'params': {
                'alpha':[1,2],
                'selection': ['random', 'cyclic'],
            }
        },
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'params': {
                'criterion': ['mse', 'friedman_mse'],
                'splitter': ['best', 'random']
            }
        }
    }

    scores = []
    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    for algo_name, config in algos.items():
        gs = GridSearchCV(config['model'], config['params'], cv=cv, return_train_score=False)
        gs.fit(X,y)
        scores.append({
            'model' : algo_name,
            'best_score': gs.best_score_,
            'best_params': gs.best_params_
        })
   
    return pd.DataFrame(scores,columns= ['model','best_score','best_params'])

find_best_model_using_gridsearchcv(X,y)


# In[70]:


np.where(x.columns=='HSR Layout')[0][0]


# In[71]:


X.columns


# In[72]:


def predict_price(location, sqft, bath, bhk):
    loc_index = np.where(X.columns==location)[0][0]
    
    x = np.zeros(len(X.columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk
    loc_index = np.where(X.columns == location)[0][0]
    if loc_index >= 0:
        x[loc_index] = 1

    return lr_clf.predict([x])[0]
    
    


# In[73]:



np.where(X.columns=='Marathahalli')[0][0]


# In[74]:


predict_price('Marathahalli',1000,1,1)


# In[80]:


predict_price('Marathahalli',1000,3,3)


# In[79]:


predict_price('HSR Layout',1000,2,2)


# In[77]:


import pickle
with open('Bangalore_house_price_prediction','wb') as f:
    pickle.dump(lr_clf,f)


# In[78]:


import json
columns = {
    'data_columns' : [col.lower() for col in X.columns]
}
with open("columns.json","w") as f:
    f.write(json.dumps(columns))


# In[ ]:





# In[ ]:



