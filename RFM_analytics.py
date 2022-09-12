###############################################################
# Customer Segmentation with RFM
###############################################################

# 1. Business Problem
# 2. Data Understanding
# 3. Data Preparation
# 4. Calculating RFM Metrics
# 5. Calculating RFM Scores
# 6. Creating & Analyzing RFM Segments
# 7. Functionalizing the Whole Process


###############################################################
# 1. Business Problem
###############################################################
# An e-commerce company wants to segment its customers and determine
# marketing strategies according to these segments.
#
# For this, we will define the behaviors of the customers and create
# groups according to the clusters in these behaviors.
#
# In other words, we will include those who exhibit common behaviors in
# the same groups and we will try to develop special sales and
# marketing techniques for these groups.
#
# Dataset Story
#
# https://archive.ics.uci.edu/ml/datasets/Online+Retail+II
#
# The dataset named Online Retail II includes the sales of an UK-based
# online store between 01/12/2009 - 09/12/2011.
#
# This company sells souvenirs. Think of it like promotional items.
#
# Most of their customers are also wholesalers.
#
# Variables
#
# InvoiceNo: Invoice number. The unique number of each transaction,
# namely the invoice. Aborted operation if it starts with C.
# StockCode: Product code. Unique number for each product.
# Description: Product name
# Quantity: Number of products. It expresses how many of the products on
# the invoices have been sold.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price (in GBP)
# CustomerID: Unique customer number
# Country: Country name. Country where the customer lives.

###############################################################
# 2. Data Understanding
###############################################################

import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

# Data in 2009-2010
df_ = pd.read_excel("datasets/online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()

df.head()

df.shape

df.describe().T


# # How many unique items?
df["Description"].nunique()
#
# # How many of each product are there?
df["Description"].value_counts().head()
#
# # Which is the most ordered product?
df.groupby("Description").agg({"Quantity": "sum"}).head()
#
# # how do you sort the above output?
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
#
# # How many bills in total?
df["Invoice"].nunique()

#
# # NA made an error. The na=False argument was used to resolve this error
df[df["Invoice"].str.contains("C", na=False)].head()
#
df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()
#
# # Which are the most expensive products?
df.sort_values("Price", ascending=False).head()
#
# # How many orders came from which country?
df["Country"].value_counts()
#
# # How much did each country earn?
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False).head()
#
# Which product receives the most returns?
df_c = df[df["Invoice"].str.contains("C", na=False)]
df_c["Description"].value_counts().head()

###############################################################
# 3. Data Preparation
###############################################################

df.isnull().sum()
df.dropna(inplace=True)

df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]
df = df[(df['Price'] > 0)]

df.head()


df["TotalPrice"] = df["Quantity"] * df["Price"]


###############################################################
# 4. Calculating RFM Metrics
###############################################################

df["InvoiceDate"].max()


today_date = dt.datetime(2010, 12, 11)


rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']


###############################################################
# 5. Calculating RFM Scores
###############################################################


rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# 1 1,1,2,3,3,3,3,3,...,5,5

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"].head()

rfm[rfm["RFM_SCORE"] == "11"].head()


###############################################################
# 6. Creating & Analysing RFM Segments
###############################################################

# Nomenclature of RFM groups
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "need_attention"].head()

rfm[rfm["segment"] == "new_customers"].index

new_df = pd.DataFrame()
new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

new_df.to_csv("new_customers.csv")




###############################################################
# 7.  Functionalizing the Whole Process
###############################################################
# The whole process is one function, but there are details that need attention

def create_rfm(dataframe):

    # DATA PREPARATION
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[(dataframe['Quantity'] > 0)]
    dataframe = dataframe[(dataframe['Price'] > 0)]
    dataframe["TotalPrice"] = dataframe["Quantity"] * dataframe["Price"]

    # CALCULATION OF RFM METRICS
    today_date = dt.datetime(2011, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                                'Invoice': lambda num: num.nunique(),
                                                "TotalPrice": lambda price: price.sum()})
    rfm.columns = ['recency', 'frequency', "monetary"]
    rfm = rfm[(rfm['monetary'] > 0)]

    # CALCULATION OF RFM SCORES
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


    rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                        rfm['frequency_score'].astype(str))


    # NAMING OF SEGMENTS
    seg_map = {
        r'[1-2][1-2]': 'hibernating',
        r'[1-2][3-4]': 'at_risk',
        r'[1-2]5': 'cant_loose',
        r'3[1-2]': 'about_to_sleep',
        r'33': 'need_attention',
        r'[3-4][4-5]': 'loyal_customers',
        r'41': 'promising',
        r'51': 'new_customers',
        r'[4-5][2-3]': 'potential_loyalists',
        r'5[4-5]': 'champions'
    }

    rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[["recency", "frequency", "monetary", "segment"]]
    return rfm

df = df_.copy()
rfm_new = create_rfm(df)
rfm_new.head()


# Those who want additional research:
#cron job
#schedule