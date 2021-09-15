# Spot Analazer for all accounts of orgs

from spot_handler.api_handler import spot_api
from spot_handler.db_handler import db_handler
from spot_handler.csv_handler import csv_handler

def order_dict_item_by_fields(dict_item, fields):
    '''
    :param dict dict_item:
    :param list fields:
    :return:
    '''
    sorted_list = [None] * fields.__len__()
    for i, field in enumerate(fields):
        sorted_list[i] = dict_item.get(field)
    return sorted_list

def sort_all_fields(fields):
    fields = order_fields(fields, 'Account ID', 1)
    fields = order_fields(fields, 'Org ID', 0)
    fields = order_fields(fields, 'Account Name', 2)
    fields = order_fields(fields, 'Total Savings', 3)
    # print(fields)
    return fields

def order_fields(fields, value , position):
    '''
    :param list fields:
    :return:
    '''
    t = None
    for i, field in enumerate(fields):
        if field == value:
            t = fields[position]
            fields[position] = value
            fields[i] = t
    return fields



def getAllPotentialSavingsData(filename, orgid_raw):
    if orgid_raw.__contains__(','):
        orgid_raw = orgid_raw.replace(' ', '')
        orgs = orgid_raw.split(',')
    else:
        orgs = [orgid_raw]
    accountLists = []
    all_fields = []
    org_names = []
    for org in orgs:
        account_list, fields, org_name = getAllPotentialSavingsDataOneOrg(filename, org)
        for account in account_list:
            # print (accountLists)
            accountLists.append(account)

        new_fields = [f for f in fields if f not in all_fields]
        for new_field in new_fields:
            all_fields.append(new_field)

        org_names.append(org_name)
    org_names_str = ','.join(org_names)
    account_lists = []

    for it in accountLists:
        print ('it')
        print (it)
        for x in all_fields:

            if x not in it.keys():
                it.update({
                    x : 0
                })
        account_lists.append(order_dict_item_by_fields(it, all_fields))

    accountDists = [q for q in accountLists]

    csv_instance = csv_handler('1')
    new_filename = filename.replace('analyser_report', org_names_str.replace(',','_').replace(' ','_'))
    csv_instance.analyser_file = open(new_filename, "w")
    csv_instance.write_to_analyser_file(accountDists, all_fields)

    return account_lists, all_fields, org_names_str, new_filename

def getAllPotentialSavingsDataOneOrg(filename, orgid_raw):
    orgid = "6060798" + str(orgid_raw)
    mydb = db_handler(orgid)
    spot_api_instance = spot_api()
    correct_token = spot_api_instance.test_user_tokens(mydb.user_tokens)
    spot_api_instance = spot_api(correct_token)
    orgAccounts = mydb.get_accounts_per_org(orgid)

    # Summary
    fields=[]
    accountDists = []
    print(orgid)

    print("End DB Connection")

    dist_for_xl = {}
    for account in orgAccounts:
        # progress += 1
        # print ('Progress : {}\n'.format(progress))
        # print("Account - " + str(account))
        potentialSavingServices = spot_api_instance.get_all_potential_savings_for_account(account[0])
        dist = {}
        # print (potentialSavingServices)
        # Setting the potential into dictionary
        if potentialSavingServices['items']:
            for saving in potentialSavingServices['items']:
                # print("Saving -"+ saving["resourceType"])
                # print("USD -"+ str(saving["potentialSavings"]))
                if saving["resourceType"] == "TaggedEC2Instance":
                    key = saving["name"]
                else:
                    key = saving["resourceType"]
                if key in dist:
                    dist[key] += int(saving["potentialSavings"])
                else:
                    dist[key] = int(saving["potentialSavings"])

            # Calculating the total savings
            totalSaving = 0
            for key in dist:
              totalSaving += int(dist[key])

            # Setting the extra info
            dist["Total Savings"] = totalSaving
            dist["Account ID"] = account[0]
            dist["Account Name"] = account[2]
            dist["Org ID"] = orgid

            # print(dist)
            accountDists.append(dist)
            dist_for_xl.update({account[0]: potentialSavingServices['items']})

            for key in dist.keys():
                if key not in fields:
                    fields.append(key)
            fields = sort_all_fields(fields)

    # print (accountDists)





    return accountDists, fields, mydb.org_name


