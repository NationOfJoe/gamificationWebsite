
from gamification_website.app.core_code.get_ocean_data.get_ocean_data_script import *

data = {
    'orgid': '606079876795',
    'oceanid': 'o-14491d28'
    # 'oceanid': 'o-cc0f3f5d'
}

instance = list_vng(data)
if instance:
    print ('yay')

pass