from spot_handler.api_handler import spot_api
from spot_handler.db_handler import db_handler
import json

def get_Ocean_object(orgid, OceanId):
    orgid = "6060798" + str(orgid)
    spot_handler_instance = spot_api()
    print(orgid)
    print('got here')
    print(OceanId)
    URL="https://api.spotinst.io/ocean/aws/k8s/cluster/{oceanClusterId}".format(oceanClusterId=OceanId)
    resp = json.loads(spot_handler_instance.rest_session.get(
        url=URL
    ).text)['response']['items'][0]
    return str(resp)
    pass