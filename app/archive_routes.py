from . import app
from flask import request, render_template, render_template_string
from flask_menu import Menu, register_menu
import json
from .core_code.calculate import calculate_class
from .sf_bit.salesforce_test import show_account_details

# @app.route('/')
# @app.route('/index')
# def index():
#     # return render_template('inputs.html')
#     return render_template('main_menu.html')

@app.route('/sf_input')
def sf_input():
    # return render_template('inputs.html')
    return render_template('sf_input.html')

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

@app.route('/store', methods=['POST'])
def store():
    headers = dict(request.headers)
    data = request.form
    print("this is some data")
    print (data)
    return render_template('store.html', json_data=data)