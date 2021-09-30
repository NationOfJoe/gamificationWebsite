from . import app
from flask import request, render_template, render_template_string, send_file
from flask_menu import Menu, register_menu
import json
from .core_code.calculate import calculate_class
from .core_code.get_monthly_savings.monthly import get_monthly_report , months_map
from .core_code.get_monthly_savings.monthly_trend import monthly_trend
from .core_code.get_ocean_data.get_ocean_data_script import *
from .core_code.get_ocean_data.tinydb_handler import *
from .core_code.interrupts.interrups import org_interrupts_report
from .analyserLog.GetFullSpotAnalyserOrg import getAllPotentialSavingsData
from.constants import init_globals

import datetime
from nodb import NoDB

class scoreboard:
    def __init__(self):
        self.team_name = None
        self.score = 0


nodb = NoDB()
nodb.bucket = 'yoavs3bucket'
nodb.index = "oceanId"

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
    db_instance = tinydb_handler_class()
    action = request.form.get("action")
    print (action)
    headers = dict(request.headers)
    data = request.form
    print(data)
    account_answer = get_Ocean_object(data)
    if action == 'Search':
        print(data['oceanid'])
        raw_text = '''
        {
            "oceanId": "%s",
            "oceanData": "%s"
         }
        ''' % (data['oceanid'], account_answer)
        print(raw_text)
        db_data_to_save = json.loads(raw_text)
        db_instance.save_data(
            ocean_id=data['oceanid'],
            key_name='ocean_data',
            key_value=account_answer
        )

    elif action == 'check_status':
        heartbeat = get_Ocean_heartbeat(data)
        db_instance.save_data(
            ocean_id=data['oceanid'],
            key_name='heartbeat',
            key_value=heartbeat
        )

    elif action == 'list_vng':
        vngs=list_vng(data)
        if not vngs:
            num_vng = 0
        else:
            num_vng = vngs.__len__()
        db_instance.save_data(
            ocean_id=data['oceanid'],
            key_name='VNGs',
            key_value=num_vng
        )

    else:
        print ('no valid action')
    db_instance.save_to_s3()
    return render_ocean_template(data['oceanid'])

def render_ocean_template(ocean_id=None):

    db_instance = tinydb_handler_class()
    ocean_json_data = db_instance.get_data_by_key(ocean_id, 'ocean_data') or 'None'
    heartbeat = db_instance.get_data_by_key(ocean_id, 'heartbeat') or 'Can\'t say'
    num_vng = db_instance.get_data_by_key(ocean_id, 'VNGs') or 'None'

    scores = []
    score_headlines = ['team_name', 'score', 'ocean_id']
    scores_raw = db_instance.get_all_data()
    for record in scores_raw:
        temp_score_record = {}
        for headline in score_headlines:
            temp_value = record.get(headline) or None
            temp_score_record.update(
                {
                    headline : temp_value
                }
            )
        scores.append(temp_score_record)

    # scores = [
    #     {'team_name': 'a',
    #      'score': 150},
    #     {'team_name': 'b',
    #      'score': 650},
    #     {'team_name': 'c',
    #      'score': 1500},
# ]

    return render_template(
        'ocean_input.html',
        ocean_data = ocean_json_data,
        cluster_status=heartbeat,
        vng=num_vng,
        scores=scores

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

@app.route('/store', methods=['GET'])
def store():
    headers = dict(request.headers)
    args = request.args
    print (args)
    result = []
    for arg in args:
        result.append("key: %s Value %s" % (arg, args.get(arg)))
    return render_template('store.html', json_data='\r\n'.join(result))


@app.route('/update_team_score', methods=['GET'])
def update_team_score():
    db_instance = tinydb_handler_class()
    headers = dict(request.headers)
    args = request.args
    # print (args)
    # args = request.form
    print (args)
    result = []
    # team_name = args.get('team_name') or None
    # ocean_id = args.get('ocean_id') or None
    team_name = args.get('team_name') or None
    ocean_id = args.get('ocean_id') or None
    print (ocean_id)
    if team_name:
        print(team_name)
        ocean_id = db_instance.get_data_by_key_team_name(
            team_name=team_name,
            key_name='oceanid'
        )
        print(ocean_id)
        if ocean_id:
            score = args.get('score')
            print(score)
            db_instance.save_data(
                ocean_id=ocean_id,
                key_name='score',
                key_value=score
            )
            print('3')
            print ('success')
    elif ocean_id:
        print(ocean_id)
        score = args.get('score')
        print(score)
        db_instance.save_data(
            ocean_id=ocean_id,
            key_name='score',
            key_value=score
        )
    db_instance.save_to_s3()
    return render_ocean_template()

@app.route('/register_team', methods=['POST'])
def register_team():
    db_instance = tinydb_handler_class()
    data = request.form
    headers = dict(request.headers)
    print (data)
    oceanid = data['oceanid']
    print ('oceanid {}'.format(oceanid))
    team_name = data['teamname']
    print ("team name {}".format(team_name))
    db_instance.save_data(
        ocean_id=oceanid,
        key_name='team_name',
        key_value=team_name
    )
    print ('success')
    db_instance.save_to_s3()
    return render_ocean_template(oceanid)
