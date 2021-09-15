from spot_handler.db_handler import db_handler
from spot_handler.api_handler import spot_api


def org_interrupts_report(filename, orgid, month):
    orgid = "6060798" + str(orgid)
    db_handler_instance = db_handler(orgid=orgid, max_query_length=150000)
    spot_api_instance = spot_api(token=db_handler_instance.user_token)
    accounts_from_db = db_handler_instance.orgAccounts
    print(accounts_from_db[0][0])
    print(accounts_from_db[0][2])
    # try:
    #     accounts = [x['accountId'] for x in spot_api_instance.list_accounts().get('response').get('items')]
    #     account_names = [x['name'] for x in spot_api_instance.list_accounts().get('response').get('items')]
    #     print ('account names')
    #     print (','.join([x['name'] for x in spot_api_instance.list_accounts().get('response').get('items')]))
    # except:
    accounts = [x[0] for x in accounts_from_db]
    account_names = [x[2] for x in accounts_from_db]

    all_resp = []
    for acc in accounts:
        print ("trying account : %s " % acc)
        resp = db_handler_instance.get_interruptions_per_region_and_month_customer_table(
            month=month,
            account=acc
        )
        if resp:
            for curr_resp in resp:
                all_resp.append(curr_resp)


    with open(filename, "w") as f:
        f.write('{0},{1},{2},{3},{4},{5}\n'.format(
            'Account ID',
            'Instance ID',
            'Elastigroup ID',
            'Instance Type',
            'Availability Zone',
            'timestamp'
        ))
        for item in all_resp:
            f.write('{0},{1},{2},{3},{4},{5}\n'.format(
                item[1],
                item[2],
                item[4],
                item[7],
                item[8],
                item[12].strftime("%Y-%m-%d_%H-%M-%S")
            ))
    data_sorted = []


    for item in all_resp:
        temp_sorted_raw = ('{0},{1},{2},{3},{4},{5}\n'.format(
            item[1],
            item[2],
            item[4],
            item[7],
            item[8],
            item[12].strftime("%Y-%m-%d_%H-%M-%S")
        ))
        temp_sorted = temp_sorted_raw.split(',')
        data_sorted.append(temp_sorted)

    return data_sorted , db_handler_instance.org_name