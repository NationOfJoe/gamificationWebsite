from . import app
from flask import request, render_template, render_template_string, send_file
from flask_menu import Menu, register_menu
import json
from .core_code.calculate import calculate_class
from .core_code.get_monthly_savings.monthly import get_monthly_report , months_map
from .core_code.get_monthly_savings.monthly_trend import monthly_trend
from .core_code.get_ocean_data.get_ocean_data_script import *
from .core_code.interrupts.interrups import org_interrupts_report
from .analyserLog.GetFullSpotAnalyserOrg import getAllPotentialSavingsData
from.constants import init_globals

import datetime

Menu(app=app)
init_globals()

@app.route('/')
@app.route('/index')
@register_menu(app, '.index', 'Home', order=1)
def index():
    return render_template('main_menu.html')

@app.route('/ocean_feat')
@register_menu(app, '.ocean_fean', 'check Ocean Features', order=2)
def ocean_feat():
    return render_template('ocean_input.html')

@app.route('/monthly_savings')
@register_menu(app, '.monthly_savings', 'Monthly Savings report', order=3)
def month_report():
    return render_template('monthly_savings_input.html')

@app.route('/monthly_savings_trend')
@register_menu(app, '.monthly_savings_trend', 'Monthly Savings trend report', order=4)
def month_trend_report():
    return render_template('monthly_trend_input.html')

@app.route('/interrupts')
@register_menu(app, '.interrupt_report', 'Interruptions', order=5)
def interrupt_report():
    return render_template('interrupt_input.html')

@app.route('/analyser_input')
@register_menu(app, '.analyser_input', 'Spot Analyser', order=6)
def analyser_input():
    return render_template('analyser_input.html')


@app.route('/get_monthly_savings', methods=['POST'])
def get_monthly_savings():
    global filename
    headers = dict(request.headers)
    data = request.form
    right_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/var/tmp/monthly_results_{}.csv'.format(right_now)
    account_answer = get_monthly_report(filename, data['orgid'], data['from-months'], data['to-months'])

    print(data)

    print (account_answer)

    return render_template(
        'savings_answer.html',
        savings = account_answer
    )

@app.route('/interrupt_report', methods=['POST'])
def get_monthly_interrupts():
    global filename
    headers = dict(request.headers)
    data = request.form
    right_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/var/tmp/interrupts_results_{}.csv'.format(right_now)
    account_answer, org_name = org_interrupts_report(filename, data['orgid'], data['months'])

    print(data)

    chosen_month = '{0} {1}'.format(
        months_map.get(data['months'].split('-')[1]),
        data['months'].split('-')[0]
    )

    print (account_answer)

    return render_template(
        'interrupts_answer.html',
        savings = account_answer,
        month_chosen = chosen_month,
        org_name = org_name
    )

@app.route('/get_ocean_data', methods=['POST'])
def get_ocean_data():
    action = request.form.get("action")
    print (action)
    headers = dict(request.headers)
    data = request.form
    print(data)
    if action == 'Search':
        account_answer = get_Ocean_object(data)
        return render_template(
            'sf_answer.html',
            salesforce_answer = account_answer
        )
    elif action == 'check_status':
        heartbeat = get_Ocean_heartbeat(data)
        return render_template(
            'ocean_input.html',
            cluster_status = heartbeat
        )
    elif action == 'list_vng':
        heartbeat = get_Ocean_heartbeat(data)
        vngs=list_vng(data)
        if not vngs:
            num_vng = 0
        else:
            num_vng = vngs.__len__()
        return render_template(
            'ocean_input.html',
            cluster_status = heartbeat,
            vng=num_vng
        )
    else:
        print ('no valid action')
        return render_template(
            'ocean_input.html',
            cluster_status = None
        )


@app.route('/monthly_trend', methods=['POST'])
def get_monthly_savings_trend():
    global filename
    global progress
    progress = 0
    headers = dict(request.headers)
    data = request.form
    print (data)
    right_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/var/tmp/monthly_trend_results_{}.csv'.format(right_now)
    account_answer = monthly_trend(filename, data['orgid'])

    print(data)

    print (account_answer)

    return render_template(
        'savings_trend_answer.html',
        savings = account_answer
    )

@app.route('/analyser_calc', methods=['POST'])
def get_analyser_report():
    global filename
    headers = dict(request.headers)
    global progress
    progress = 0
    data = request.form
    right_now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = '/var/tmp/analyser_report_{}.csv'.format(right_now)
    account_answer, fields, org_name, filename = getAllPotentialSavingsData(filename, data['orgid'])

    print(data)

    print (account_answer)

    return render_template(
        'analyser_answer.html',
        savings = account_answer,
        fields = fields,
        org_name = org_name,
        filename = filename.split('/')[-1]
    )

@app.route('/download_csv', methods=['get'])
def download_csv():

    global filename
    print (filename)
    results_file_name = 'results.csv'
    results_file_name_raw = request.args.get('file_name')
    if results_file_name_raw:
        results_file_name = results_file_name_raw
    return send_file(
        filename,
        attachment_filename=results_file_name,
        cache_timeout=1,
        as_attachment=True
    )

@app.route('/calculate', methods=['POST'])
def calculate():
    headers = dict(request.headers)
    data = request.form

    headers_tbl = ['Basic']

    if 'standard' in data.keys():
        headers_tbl.append('standard')
    if 'aggressive' in data.keys():
        headers_tbl.append('aggressive')
    if 'veryaggressive' in data.keys():
        headers_tbl.append('veryaggressive')

    calculator = calculate_class(data)
    calculator.do_calc(headers_tbl)
    json_report = json.dumps(calculator.report)
    print (','.join(data.keys()))

    return render_template(
        'report.html',
        customer_name=calculator.customer_name,
        suggestions = calculator.aabb,
        aa=int(round(calculator.ri_ec2, 0)),
        # bb=int(round(calculator.total_potential, 0)),
        bb = calculator.tier,
        total_savings = int(round(12 * calculator.total_potential, 0)),
        spot_save = int(round(calculator.total_cost, 0)),
        json_data_report = json_report,
        headers_tbl=headers_tbl

    )

@app.route('/tiers')
@register_menu(app, '.tiers', 'Saving Tiers', order=7)
def sf_input():
    return render_template('inputs.html')

@app.route('/store', methods=['POST'])
def store():
    headers = dict(request.headers)
    data = request.form
    print("this is some data")
    print (data)
    return render_template('store.html', json_data=data)