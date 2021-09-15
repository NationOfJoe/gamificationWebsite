from .get_billing_per_account_again import get_all_billings_per_month_per_account, day
from calendar import monthrange
import datetime
import threading

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
days_this_month_full = monthrange(int(today.split('-')[0]), int(today.split('-')[1]))[1]
days_this_month_now = int(today.split('-')[2])

def get_orgs_trend_from_db(org, from_date, to_date, all_org_data):
    # for org in all_my_orgs:
        try:
            org_data = get_all_billings_per_month_per_account(org, from_date, to_date)
            all_org_data.append(org_data)
            print(org, org_data.name)
        except Exception as e:
            try:
                print(org + ' Failed!   reason : ' + e.msg)
            except:
                print(org + ' Failed!')


def monthly_trend(filename, orgid):
    if orgid.__contains__(','):
        all_my_orgs = orgid.split(',')
    else:
        all_my_orgs = [orgid]
    all_org_data = []
    from_date = '2021-{0:02d}-01'.format(int(today.split('-')[1]))
    print (from_date)
    to_date = today
    print (to_date)

    threads = [threading.Thread(target=get_orgs_trend_from_db,
                                args=(org, from_date, to_date, all_org_data)
                                )
               for org in all_my_orgs]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


    # for org in all_my_orgs:
    #
    #     try:
    #         org_data = _thread.start_new_thread(get_all_billings_per_month_per_account, (org, from_date, to_date))
    #         org_data = get_all_billings_per_month_per_account(org, from_date, to_date)
    #         all_org_data.append(org_data)
    #         print(org, org_data.name)
    #     except Exception as e:
    #         try:
    #             print(org + ' Failed!   reason : ' + e.msg)
    #         except:
    #             print(org + ' Failed!')

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
        f.write('Org Name, Org ID, timestamp, total savings until now, daily_average, savings if daily average until month end, number of days \n')
    for this_org in all_org_data:
        with open(filename ,'a' ) as f:
            for curr_month in this_org.months:
                savings_till_now = round(float(curr_month.savings),2)
                f.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(
                    this_org.name,
                    this_org.orgid,
                    curr_month.timestamp,
                    str(savings_till_now),
                    str(round(float(savings_till_now/days_this_month_now),2)),
                    str(round(float((savings_till_now/days_this_month_now)*days_this_month_full),2)),
                    curr_month.number_of_days
                ))

    all_org_data_sorted = []
    for this_org in all_org_data:

        for curr_month in this_org.months:
            temp_sorted_org_raw = ''
            savings_till_now = round(float(curr_month.savings), 2)
            temp_sorted_org_raw = ('{0},{1},{2},{3},{4},{5},{6}\n'.format(
                this_org.name,
                this_org.orgid,
                curr_month.timestamp,
                str(savings_till_now),
                str(round(float(savings_till_now / days_this_month_now),2)),
                str(round(float((savings_till_now / days_this_month_now) * days_this_month_full),2)),
                curr_month.number_of_days
            ))
            temp_sorted_org = temp_sorted_org_raw.split(',')
            all_org_data_sorted.append(temp_sorted_org)
    return all_org_data_sorted