from get_all_potential_savings import *

def get_analyser_report():
    global filename
    global progress
    progress = 0
    data = request.form
    right_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/var/tmp/analyser_report_{}.csv'.format(right_now)
    account_answer, fields, org_name, filename = getAllPotentialSavingsData(filename, data['orgid'])