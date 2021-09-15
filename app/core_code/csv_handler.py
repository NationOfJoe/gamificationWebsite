import csv
import re
import os

class csv_handler():
    def __init__(self, core_tester=False):
        print (os.getcwd())
        if not core_tester:
            self.monthly_file = open('app/core_code/Internal_Pricing_Model_Monthly.csv', mode='r')
            self.annual_file = open('app/core_code/Internal_Pricing_Model_Annual.csv', mode='r')
        else:
            self.monthly_file = open('Internal_Pricing_Model_Monthly.csv', mode='r')
            self.annual_file = open('Internal_Pricing_Model_Annual.csv', mode='r')
        self.monthly_raw = [a for a in csv.DictReader(self.monthly_file)]
        self.annual_raw = [b for b in csv.DictReader(self.annual_file)]

    def write_to_analyser_file(self, accountDists, fields):
        w = csv.DictWriter(self.analyser_file, sorted(fields), extrasaction="ignore")
        w.writeheader()
        for accoutDist in accountDists:
            w.writerow(accoutDist)
        self.analyser_file.close()

    def read_tier_policy(self):
        self.monthly = {}
        for x in self.monthly_raw:
            category = x.get('category').lower().replace(' ', '').replace('%','_pct')
            self.monthly.update({category: {}})
            temp_dict = {}
            for k,v in x.items():
                if k not in ('category'):
                    temp_dict.update({k: float(re.sub('[^0-9]','', v))})
            self.monthly.update({category: temp_dict})
        self.annual = {}
        for x in self.annual_raw:
            category = x.get('category').lower().replace(' ', '').replace('%','_pct')
            self.annual.update({category: {}})
            temp_dict = {}
            for k,v in x.items():
                if k not in ('category'):
                    temp_dict.update({k: float(re.sub('[^0-9]','', v))})
            self.annual.update({category: temp_dict})

