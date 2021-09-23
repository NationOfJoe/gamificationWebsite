from tinydb import TinyDB, Query

class tinydb_handler_class():
    def __init__(self):
        self.db = TinyDB('db.json')
        self.query = Query()


    def read_from_s3(self):
        pass

    def save_to_s3(self):
        pass

    def save_data(self, ocean_id, key_name, key_value):
        exists = self.db.search(self.query.oceanid == ocean_id)
        if exists.__len__() == 0:
            self.db.insert(
                {
                    'oceanid': ocean_id,
                    key_name: key_value
                }
            )
        else:
            j = Query()
            self.db.update(
                {
                    'oceanid': ocean_id,
                    key_name: key_value
                },
                 j.oceanid == ocean_id
            )
    def get_data_by_key(self, ocean_id, key_name):
        try:
            key_value = self.db.search(self.query.oceanid == ocean_id)[0][key_name]
        except:
            key_value = None
        return key_value