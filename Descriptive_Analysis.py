# Descriptice Model for CLV

##Libraris
import pandas as pd 
import pytimetk as tk   
import matplotlib.pyplot as plt
import plotly.io as pio

#-----Read Data------#
transaction_df = pd.read_excel("Data/OnlineRetail.xlsx")

transaction_df.head()
transaction_df.info()

transaction_df.isna().sum()
transaction_df.dropna(inplace=True)

(transaction_df[['Quantity']] < 0).sum()

transaction_df = transaction_df[transaction_df['Quantity'] >= 0]

transaction_df['InvoiceDate'] = pd.to_datetime(transaction_df['InvoiceDate']).dt.normalize()

transaction_df['TotalPrice'] = transaction_df['Quantity']*transaction_df['UnitPrice']

#-----------EDA-------------#

transaction_df.glimpse()

transaction_df['TotalPrice'].sum()

#weekly plot of customer spend over one year using pytimetk libraries
fig = (transaction_df[['InvoiceDate','TotalPrice']].summarize_by_time(date_column='InvoiceDate', value_column='TotalPrice', freq='W', agg_func='sum'))\
    .plot_timeseries('InvoiceDate','TotalPrice')
pio.show(fig)

# --------------------Aggregation Models ------------------------------# used to calculate avg clv for a group of customers or a cohort

customerSales_df = transaction_df\
    .groupby(['CustomerID','InvoiceNo']).agg(
                CustomerSpend = ('TotalPrice','sum'),
                timestamp = ('InvoiceDate','max'),
    ).reset_index().groupby('CustomerID').agg(
        TimeDiff = ('timestamp', lambda x: x.max()-x.min()),
        Frequency = ('InvoiceNo', 'nunique'),
        TotalSpend = ('CustomerSpend','sum'),
        AverageSpend = ('CustomerSpend','mean')
    ).reset_index()



customerSales_df.sort_values(by='TotalSpend')

#average for all customers
summary_stats = {
    'average_sales': customerSales_df['AverageSpend'].mean(),
    'average_frequency': customerSales_df['Frequency'].mean(),
    'churnrate': 1- (customerSales_df['Frequency']>3).sum()/len(customerSales_df['Frequency']),
    'max_days': customerSales_df['TimeDiff'].max()
    }

summary_stats = pd.DataFrame([summary_stats])

print(summary_stats)

#Lifetime ClV Calculation

customer_lifespan = 5   #years
profit_margin = 0.15  #profit margin for customers

Customer_Average_Revenue= (summary_stats['average_sales']*summary_stats['average_frequency']*avg_lifetime)
Customer_Average_Profit = Customer_Average_Revenue*profit_margin
summary_stats['Customer_Average_Revenue'] = Customer_Average_Revenue
summary_stats['customer_clv'] = Customer_Average_Profit

summary_stats

print("Expected Revenue over next 5 years {:.2f}, and average profit per customer is expected to be {:.2f}".format(Customer_Average_Revenue.iloc[0], Customer_Average_Profit.iloc[0]))

#--------------------------------------------------Cohort Models-------------------------------------------------------#

customer_lifespan = 5   #years
profit_margin = 0.15  #profit margin for customers
eps_churn_rate = 0.001     #avoid infinty values during calculations

transaction_df['start_month'] = transaction_df.groupby('CustomerID')['InvoiceDate'].transform(lambda x: x.min().strftime('%Y-%m'))


transaction_df.glimpse()

cohort_data = transaction_df\
    .groupby(['start_month','CustomerID','InvoiceNo']).agg(
                CustomerSpend = ('TotalPrice','sum'),
                timestamp = ('InvoiceDate','max'),
    ).reset_index().groupby(['start_month','CustomerID']).agg(
        TimeDiff = ('timestamp', lambda x: x.max()-x.min()),
        Frequency = ('InvoiceNo', 'nunique'),
        TotalSpend = ('CustomerSpend','sum'),
        AverageSpend = ('CustomerSpend','mean')
    ).reset_index()


cohort_summary_stats = cohort_data.groupby(['start_month'])



