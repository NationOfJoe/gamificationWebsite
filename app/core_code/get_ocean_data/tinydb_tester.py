from tinydb_handler import *

db_instance = tinydb_handler_class()
account_answer = 'aabdfdfsa'
# db_instance.save_data(
#     ocean_id='2',
#     key_name='ocean_data',
#     key_value=account_answer
# )
qq = db_instance.get_data_by_key(
    ocean_id='25',
    key_name='ocean_data',
)
pass