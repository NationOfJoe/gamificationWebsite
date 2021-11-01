from . import app
from flask import request, render_template, render_template_string, send_file
from flask_menu import Menu, register_menu
import json
from .core_code.get_monthly_savings.monthly import get_monthly_report , months_map
from .core_code.get_ocean_data.get_ocean_data_script import *
from .core_code.get_ocean_data.tinydb_handler import *
from .core_code.interrupts.interrups import org_interrupts_report

from.constants import init_globals

import datetime

class scoreboard:
    def __init__(self):
        self.team_name = None
        self.score = 0


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



@app.route('/get_ocean_data', methods=['POST'])
def get_ocean_data():
    db_instance = tinydb_handler_class()
    action = request.form.get("action")
    print (action)
    headers = dict(request.headers)
    data = request.form
    print(data)
    account_answer, headroom = get_Ocean_object(data)
    if action == 'Search':
        print(data['oceanid'])
        raw_text = '''
        {
            "oceanId": "%s",
            "oceanData": "%s"
         }
        ''' % (data['oceanid'], account_answer)
        print(raw_text)
        db_instance.save_data(
            ocean_id=data['oceanid'],
            key_name='ocean_data',
            key_value=account_answer or "can'\t say"
        )
        if headroom:
            db_instance.save_data(
                ocean_id=data['oceanid'],
                key_name='headroom',
                key_value=headroom or "can'\t say"
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

def get_scores_in_order(db_instance=None):
    if not db_instance:
        db_instance = tinydb_handler_class()
    scores = []
    score_headlines = ['team_name', 'score', 'oceanid']
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
    return scores

def render_ocean_template(ocean_id=None):

    db_instance = tinydb_handler_class()
    ocean_json_data = db_instance.get_data_by_key(ocean_id, 'ocean_data') or 'None'
    heartbeat = db_instance.get_data_by_key(ocean_id, 'heartbeat') or 'Can\'t say'
    num_vng = db_instance.get_data_by_key(ocean_id, 'VNGs') or 'None'
    headroom = db_instance.get_data_by_key(ocean_id, 'headroom') or 'None'

    scores = get_scores_in_order(db_instance)

    return render_template(
        'ocean_input.html',
        ocean_data = ocean_json_data,
        cluster_status=heartbeat,
        vng=num_vng,
        scores=scores,
        headroom=headroom

    )



@app.route('/scoreboard')
@register_menu(app, '.scoreboard', 'Scoreboard', order=8)
def scoreboard():
    scores = get_scores_in_order()
    return render_template('scoreboard.html', scores=scores)

@app.route('/scoreboard_for_admins')

def scoreboard_admin():
    scores = get_scores_in_order()
    return render_template('scoreboard_for_admins_page.html', scores=scores)

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
def update_team_score(ocean_id=None, team_name=None, score=None):
    db_instance = tinydb_handler_class()
    headers = dict(request.headers)
    args = request.args
    print (args)
    if not score:
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
    else:
        if not ocean_id:
            ocean_id = db_instance.get_data_by_key_team_name(
                team_name=team_name,
                key_name='oceanid'
            )
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
    action = request.form.get("action")
    headers = dict(request.headers)
    print (data)
    oceanid = data['oceanid']
    try:
        team_name = data['teamname']
    except Exception as e:
        team_name = None
        print(e)
    try:
        this_score = data['score']
    except Exception as e:
        this_score = None
        print(e)
    print('oceanid {}'.format(oceanid))
    if action == 'register':
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
    elif action == 'go to team page':
        ocean_id = oceanid
        db_instance = tinydb_handler_class()
        ocean_json_data = db_instance.get_data_by_key(ocean_id, 'ocean_data') or 'None'
        heartbeat = db_instance.get_data_by_key(ocean_id, 'heartbeat') or 'Can\'t say'
        num_vng = db_instance.get_data_by_key(ocean_id, 'VNGs') or 'None'
        headroom = db_instance.get_data_by_key(ocean_id, 'headroom') or 'None'
        team_name = db_instance.get_data_by_key(ocean_id, 'team_name') or 'None'
        return render_template(
            'team_page.html',
            team_name = team_name,
            oceanid = oceanid,
            ocean_data=ocean_json_data,
            cluster_status=heartbeat,
            vng=num_vng,
            headroom=headroom
        )
    elif action == 'score_change':
        update_team_score(
            team_name=team_name,
            ocean_id=oceanid,
            score=int(this_score)
        )
        db_instance.save_to_s3()
        scores = get_scores_in_order()
        return render_template('scoreboard.html', scores=scores)
    elif action == 'score_add':
        if oceanid:
            curr_score = db_instance.get_data_by_key(
            ocean_id=oceanid,
            key_name='score'
        )
        else:
            curr_score = db_instance.get_data_by_key_team_name(
                team_name=team_name,
                key_name='score'
            )
        update_team_score(
            team_name=team_name,
            ocean_id=oceanid,
            score=int(this_score)+int(curr_score)
        )
        db_instance.save_to_s3()
        scores = get_scores_in_order()
        return render_template('scoreboard.html', scores=scores)

