from spot_handler.api_handler import spot_api
from spot_handler.db_handler import db_handler
import json

def get_Ocean_object(data):
    orgid = "6060798" + str(data['orgid'])
    OceanId = data['oceanid']
    spot_handler_instance = spot_api()
    URL="https://api.spotinst.io/ocean/aws/k8s/cluster/{oceanClusterId}".format(oceanClusterId=OceanId)
    try:
        raw_resp = json.loads(spot_handler_instance.rest_session.get(
            url=URL
        ).text)['response']['items'][0]
        resp = str(raw_resp)
        if resp.__contains__('autoHeadroomPercentage'):
            print ('it does')
            # headroom = raw_resp['autoHeadroomPercentage']
            headroom = 'aa'
            print('resp %s' % resp)
            print('headroom %s' % headroom)
        else:
            headroom = None
            print ('no headroom')
    except Exception as e:
        print ('Exception is %s' % e)
        resp = None
        headroom = None
    return resp, headroom

def get_Ocean_heartbeat(data):
    orgid = "6060798" + str(data['orgid'])
    OceanId = data['oceanid']
    spot_handler_instance = spot_api()
    URL="https://api.spotinst.io/ocean/k8s/cluster/{oceanClusterId}/controllerHeartbeat".format(oceanClusterId=OceanId)
    resp = json.loads(spot_handler_instance.rest_session.get(
        url=URL
    ).text)['response']['items'][0]['status']
    return str(resp)

def list_vng(data):
    orgid = "6060798" + str(data['orgid'])
    OceanId = data['oceanid']
    spot_handler_instance = spot_api()
    URL="https://api.spotinst.io/ocean/aws/k8s/launchSpec?oceanId={oceanClusterId}".format(oceanClusterId=OceanId)
    resp = json.loads(spot_handler_instance.rest_session.get(
        url=URL
    ).text)['response']['items']
    if resp == []:
        return None
    return (resp)