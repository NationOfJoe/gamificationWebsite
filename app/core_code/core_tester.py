from csv_handler import csv_handler

csv_instance = csv_handler(core_tester=True)
csv_instance.read_tier_policy()

pot = 12000
behaviour = 'aggressive'
tiers = csv_instance.monthly.get('monthlytiersavings')
temp_list = []
for k,v in tiers.items():
    if v > pot:
        temp_list.append(v)
next_tier_value = min(temp_list)
tier = [t for t, srr in tiers.items() if srr == next_tier_value][0]
tot = csv_instance.monthly.get(behaviour).get(tier)
pct = csv_instance.monthly.get(behaviour + '_pct').get(tier)

pass