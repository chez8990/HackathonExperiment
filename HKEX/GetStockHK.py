
# %%
# pip install yfinance --upgrade --no-cache-dir
import yfinance as yf
import datetime


# %%
def GetStockHK(stock_code, start = datetime.datetime.today() - datetime.timedelta(days=30), end = datetime.datetime.today()):
    # The function will return daily stocks prices of recent 30 days
    return(yf.download(str(stock_code) + '.HK', start, end))


# %%
df1 = GetStockHK('0011')


# %%
df1


# %%
col_names = list(df1.columns)
col_names.remove('Volume')


# %%
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
#get_ipython().run_line_magic('matplotlib', 'agg')
#%config InlineBackend.figure_format = 'svg'


# %%
plt.figure()
df1[col_names].plot()


# %%
image = BytesIO()
plt.savefig(image, format='png')
print(base64.b64encode(image.getvalue()))


# %%


