from tinydb_handler import *

db_instance = tinydb_handler_class()
account_answer = 120
# db_instance.save_data(
#     ocean_id='o-e5a7bd02',
#     key_name='score',
#     key_value=account_answer
# )
# qq = db_instance.get_data_by_key_team_name(
#     team_name='ZZZZZ',
#     key_name='oceanid',
# )

# aa = db_instance.read_from_s3('spot_constants_template.json')
# bb = db_instance.save_to_s3()

ss = db_instance.get_all_data()
pass