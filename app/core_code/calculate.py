from .csv_handler import csv_handler
RI_RATE = 0.32
SPOT_RATE = 0.68

class proposal():
    def __init__(self, name):
        self.name = name
        self.precentage = float()
        self.monthly_fee = int()
        self.annual_fee = int()
        self.tier_name = ''



class calculate_class():
    def __init__(self, inputs):
        self.csv_instance = csv_handler()
        self.csv_instance.read_tier_policy()
        self.inputs = inputs
        self.customer_name = self.inputs['customer_name']
        self.report = {'customer name' : self.customer_name}

    def calc_tier(self, potential):
        tiers = self.csv_instance.monthly.get('monthlytiersavings')
        temp_list = []
        for k, v in tiers.items():
            if v > potential:
                temp_list.append(v)
        next_tier_value = min(temp_list)
        tier = [t for t, srr in tiers.items() if srr == next_tier_value][0]
        return tier

    def get_values_from_strategy(self, behaviour, tier):
        print (behaviour + tier)
        tot = self.csv_instance.monthly.get(behaviour).get(tier)
        pct = self.csv_instance.monthly.get(behaviour + '_pct').get(tier)
        return tot, pct

    def do_calc(self, requested_calcs):
        elastic_od = float(self.inputs['ESPM'])/SPOT_RATE
        container_od = float(self.inputs['CSPM'])/SPOT_RATE
        ri_od = (float(self.inputs['RSPM'])*float(self.inputs['per_reservation']))/(RI_RATE*100)
        ri_anti_od = (float(self.inputs['RSPM']) * (100 - float(self.inputs['per_reservation']))) / (RI_RATE * 100)
        self.total_cost = elastic_od + container_od + ri_od + ri_anti_od
        self.report.update({'total_cost': self.total_cost})
        self.ri_ec2 = (ri_od - container_od - elastic_od)*RI_RATE
        self.report.update({'RI on EC2': self.ri_ec2})
        ri_paas = ri_anti_od * RI_RATE
        self.total_potential = container_od + elastic_od + self.ri_ec2 + ri_paas
        self.tier = self.calc_tier(self.total_potential)
        self.report.update({'total_potential' : self.total_potential})
        self.aabb = ','.join(requested_calcs)

        for req in requested_calcs:
            proposals = []
            if req not in ('Basic'):
                temp_proposal = proposal(req)
                self.tier_name = self.tier
                temp_proposal.monthly_fee, temp_proposal.precentage = self.get_values_from_strategy(
                    behaviour=req, tier=self.tier
                )
                temp_proposal.precentage = temp_proposal.precentage/100
                temp_proposal.annual_fee = 12*temp_proposal.monthly_fee
                print (temp_proposal.monthly_fee)
                print(temp_proposal.precentage/100)
                proposals.append(temp_proposal)



