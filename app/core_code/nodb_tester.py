from nodb import NoDB
import json

nodb = NoDB()
nodb.bucket = 'yoavs3bucket'
nodb.index = "name"

# Save an object!
user = json.loads(
    '''
    {
        "name": "Jeff",
        "age": 19
     }
    '''
)
nodb.save(user) # True

# Load our object!
user = nodb.load("Jeff")
print(user['age']) # 19