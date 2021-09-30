from tinydb import TinyDB, Query
import boto3
import json

s3_bucket_name = 'yoavs3bucket'
db_filenames3 = "gamification_db.json"
db_filename_local = 'game_db.json'

class tinydb_handler_class():
    def __init__(self):
        session = boto3.session.Session(region_name='eu-west-2')
        self.this_bucket = session.client('s3', config=boto3.session.Config(signature_version='s3v4'))

        try:
            db_content = self.read_from_s3(db_filenames3)
            with open(db_filename_local, 'w') as file:
                file.write(db_content)
        except Exception as e:
            print (e)

        self.db = TinyDB(db_filename_local)
        self.query = Query()

    def read_from_s3(self, key):
        answer = self.this_bucket.get_object(Bucket=s3_bucket_name, Key=key)
        return (answer['Body'].read().decode('utf8'))

    def save_to_s3(self):
        self.this_bucket.upload_file(db_filename_local, s3_bucket_name, db_filenames3)

    def save_data(self, ocean_id, key_name, key_value):
        # exists = self.db.search(self.query.oceanid == ocean_id)
        # print("exists {}".format(exists))
        # print("db oceanid {}".format(ocean_id))
        # if exists.__len__() == 0:
        #     print('not existing ocean ID')
        #     self.db.insert(
        #         {
        #             'oceanid': ocean_id,
        #             key_name: key_value
        #         }
        #     )
        #     print('created {2} {0} = {1}'.format(key_name, key_value, ocean_id))
        # else:
        #     j = Query()
        #     print ('existing ocean ID')
        #     self.db.update(
        #         {
        #             'oceanid': ocean_id,
        #             key_name: key_value
        #         },
        #          j.oceanid == ocean_id
        #     )
        j = Query()
        self.db.upsert(
            {
                'oceanid': ocean_id,
                key_name: key_value
            },
             j.oceanid == ocean_id
                )
        print('inserted {2} {0} = {1}'.format(key_name, key_value, ocean_id))

    def get_data_by_key(self, ocean_id, key_name):
        try:
            key_value = self.db.search(self.query.oceanid == ocean_id)[0][key_name]
        except:
            key_value = None
        return key_value

    def get_all_data(self):
        result = self.db.all()
        return result

    def get_data_by_key_team_name(self, team_name, key_name):
        k = Query()

        try:
            key_value = self.db.search(self.query.team_name == team_name)[0][key_name]
        except Exception as e:
            key_value = None
        return key_value