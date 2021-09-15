from spot_handler.api_handler import spot_api
from spot_handler.db_handler import db_handler
import json

class org():
    def __init__(self, orgid):
        self.accounts = []
        self.orgid = orgid
        self.actual_costs = 0
        self.running_hours = 0
        self.savings = 0
        self.potential_cost = 0
        self.name = None
        self.days = []
        self.months = []

class day():
    def __init__(self, timestamp):
        self.account_id = ''
        self.savings = 0
        self.actual_costs = 0
        self.running_hours = 0
        self.savings = 0
        self.potential_cost = 0
        self.timestamp = timestamp
        self.datapoints = []
        self.data = None
        self.number_of_days = 0

class account():
    def __init__(self, account_id):
        self.account_id = account_id
        self.savings = 0
        self.actual_costs = 0
        self.running_hours = 0
        self.savings = 0
        self.potential_cost = 0
        self.timestamp = None
        self.datapoints = []
        self.data = None


def get_od_statistics(orgid):
    orgid = "6060798" + str(orgid)
    this_db_instance = db_handler(orgid)
    this_db_instance.write_to_log('connected to database {}'.format(this_db_instance.org_db))
    query = '''
    SELECT * from aws_ec2_instances
    '''
    org_cursor = this_db_instance.org_db.cursor()
    org_cursor.execute(query)
    all_orgs = org_cursor.fetchall()
    print ('yay')
    return all_orgs
    pass


def get_all_billings_per_month_per_account(org_obj, month, next_month):
    # orgid = org_obj.get('Org ID')
    orgid = "6060798" + str(org_obj)
    this_db_instance = db_handler(orgid)
    this_db_instance.write_to_log('connected to database {}'.format(this_db_instance.core_db))
    spot_session = spot_api(token=this_db_instance.user_token)
    this_org = org(orgid)
    # this_org.name = org_obj.get('Name')
    this_org.name = this_db_instance.org_name
    accounts = [acc[0] for acc in this_db_instance.orgAccounts]
    this_db_instance.write_to_log('org accounts {}'.format(','.join(accounts)))


    body = {
        "accountIds": accounts,
        "fromDate" : "{}T00:00:00.000Z".format(month),
        "toDate" :  "{}T23:59:59.000Z".format(next_month)
    }
    for t_account in accounts:
        url = 'https://api.spotinst.io/aws/costs?accountId={ACCOUNT_ID}&fromDate={FROM_DATE}&toDate={TO_DATE}&aggregationPeriod={AGGREGATION_PERIOD}'.format(
            ACCOUNT_ID = t_account,
            FROM_DATE = body.get('fromDate'),
            TO_DATE = body.get('toDate'),
            AGGREGATION_PERIOD = 'daily'
        )
        result = None
        i = 0
        while not result or result.status_code != 200:
            result = spot_session.rest_session.get(
                url=url
            )
            if result.status_code != 200:
                i += 1
                spot_session = spot_api(this_db_instance.user_tokens[i])
                this_db_instance.write_to_log('tried token {0} and failed with code {1}'.format(this_db_instance.user_tokens[i],result.status_code))

        temp_response = json.loads(result.text)['response']['items']
        for x in temp_response:
            if x.get('timestamp'):
                if not any(a.timestamp == x.get('timestamp') for a in this_org.days):
                    this_org.days.append(day(x.get('timestamp')))
                this_day = [d for d in this_org.days if d.timestamp == x.get('timestamp')][0]
                this_day.savings += float(x.get('spot').get('potentialCosts')) - float(x.get('spot').get('actualCosts'))
                this_day.actual_costs += x.get('spot').get('actualCosts')
                this_day.running_hours += x.get('spot').get('runningHours')

    return this_org