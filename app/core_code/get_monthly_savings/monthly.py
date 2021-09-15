from .get_billing_per_account_again import get_all_billings_per_month_per_account, day
import datetime

months_map = {
    '01' : "January",
    '02' : "February",
    '03' : "March",
    '04' : "April",
    '05' : "May",
    '06' : "June",
    '07' : "July",
    '08' : "August",
    '09' : "September",
    '10' : "October",
    '11' : "November",
    '12' : "December"
}


today = datetime.datetime.now().strftime("%Y-%m-%d")

def get_monthly_report(filename, orgid, from_month, to_month):
    if orgid.__contains__(','):
        all_my_orgs = orgid.split(',')
    else:
        all_my_orgs = [orgid]

    # check for current month:
    now = datetime.datetime.now()
    to_month_month = int(to_month.split('-')[1])
    to_month_year = int(to_month.split('-')[0])
    if to_month_month == now.month and to_month_year == now.year:
        print('current month')
        if now.month == 1:
            to_month = "{0}-{1}".format(str(now.year - 1), '12')
        else:
            to_month = "{0}-{1}".format(str(now.year), str(now.month - 1).zfill(2))
    all_org_data = []
    from_date = '{}-01'.format((from_month))
    print (from_date)
    to_date = '{}-31'.format((to_month))
    print (to_date)
    for org in all_my_orgs:
        try:
            org_data = get_all_billings_per_month_per_account(org, from_date, to_date)
            all_org_data.append(org_data)
            print(org, org_data.name)
        except Exception as e:
            try:
                print(org + ' Failed!   reason : ' + e.msg)
            except:
                print(org + ' Failed!')

    for this_org in all_org_data:
        this_org.days.sort(key=lambda x: x.timestamp, reverse=False)
        for x in this_org.days:
            this_month_title = months_map.get(x.timestamp.split(':')[1]) + '_' + x.timestamp.split(':')[0]
            if not any(a.timestamp == this_month_title for a in this_org.months):
                this_org.months.append(day(this_month_title))
            this_month = [d for d in this_org.months if d.timestamp == this_month_title][0]
            this_month.savings += x.savings
            this_month.actual_costs += x.actual_costs
            this_month.running_hours += x.running_hours
            this_month.number_of_days += 1
        pass

    with open(filename ,'w' ) as f:
        f.write('Org Name, Org ID, timestamp, total savings, total running hours, actual costs, number of days \n')
    for this_org in all_org_data:
        with open(filename ,'a' ) as f:
            for curr_month in this_org.months:
                f.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(
                    this_org.name,
                    this_org.orgid,
                    curr_month.timestamp,
                    str(round(float(curr_month.savings),2)),
                    str(round(float(curr_month.running_hours),2)),
                    str(round(float(curr_month.actual_costs),2)),
                    curr_month.number_of_days
                ))

    all_org_data_sorted = []
    for this_org in all_org_data:

        for curr_month in this_org.months:
            temp_sorted_org_raw = ''
            temp_sorted_org_raw = '{0},{1},{2},{3},{4},{5},{6}'.format(
                this_org.name,
                this_org.orgid,
                curr_month.timestamp,
                str(round(float(curr_month.savings),2)),
                str(round(float(curr_month.running_hours),2)),
                str(round(float(curr_month.actual_costs),2)),
                curr_month.number_of_days
            )
            temp_sorted_org = temp_sorted_org_raw.split(',')
            all_org_data_sorted.append(temp_sorted_org)
    return all_org_data_sorted