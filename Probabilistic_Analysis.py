# Probabilistic  Model for CLV

#-------------------------LIBRARIES---------------------#
import pandas as pd
import pytimetk as ptk
import lifetimes as lf
from lifetimes.plotting import plot_probability_alive_matrix


#-----Read Data------#

transaction_df2 = pd.read_excel("Data/OnlineRetail.xlsx")

transaction_df2.head()
transaction_df2.info()

transaction_df2.isna().sum()
transaction_df2.dropna(inplace=True)

(transaction_df2[['Quantity']] < 0).sum()

transaction_df2 = transaction_df2[transaction_df2['Quantity'] >= 0]

transaction_df2['InvoiceDate'] = pd.to_datetime(transaction_df2['InvoiceDate']).dt.normalize()

transaction_df2['TotalPrice'] = transaction_df2['Quantity']*transaction_df2['UnitPrice']

transaction_df2.glimpse()

#-----------------------------------------------Probabilistic  Model---------------------------------------------------------------#
#Used for future purchase analysis and curn estimation

summary_stats_pa  = lf.utils.summary_data_from_transaction_data(transaction_df2, customer_id_col='CustomerID',\
                datetime_col='InvoiceDate',monetary_value_col='TotalPrice')    

#check if there is negative monetary transactions
summary_stats_pa[summary_stats_pa['monetary_value']<=0]
summary_stats_pa = summary_stats_pa[summary_stats_pa['monetary_value']>0]


bgf = lf.BetaGeoFitter(penalizer_coef=0.0)

bgf.fit(summary_stats_pa['frequency'],summary_stats_pa['recency'],summary_stats_pa['T'] )

bgf.summary

summary_stats_pa['probability_alive']=bgf.conditional_probability_alive(summary_stats_pa['frequency'],summary_stats_pa['recency'],summary_stats_pa['T'])

plot_probability_alive_matrix(bgf)
plt.show()



ggf = lf.GammaGammaFitter(penalizer_coef=0.0)
ggf.fit(summary_stats_pa['frequency'],summary_stats_pa['monetary_value'] )
ggf.summary

summary_stats_pa['sales_profit']=ggf.conditional_expected_average_profit(summary_stats_pa['frequency'],summary_stats_pa['monetary_value'])


summary_stats_pa['Predicted_CLV']=ggf.customer_lifetime_value(bgf, summary_stats_pa['frequency'],summary_stats_pa['recency'],summary_stats_pa['T'],summary_stats_pa['monetary_value'], time=4, discount_rate=0.01, freq='D')