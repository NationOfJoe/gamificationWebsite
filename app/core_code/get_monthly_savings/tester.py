from calc.app.core_code.get_monthly_savings.monthly_trend import *
from calc.app.core_code.get_monthly_savings.monthly import *

# instance = monthly_trend(
#     'abc.csv',
#     '67573'
# )
instance = get_monthly_report(
    'abc.csv',
    '67573',
    '2021-04',
    '2021-07'
)
pass