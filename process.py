import csv, json
from collections import OrderedDict
from datetime import datetime



'''Using a set to find all the campaigns that have the object_type video'''

f2 = open('source2.csv')
csv_f2 = csv.reader(f2)

video_set = set()
for row in csv_f2:
    if row[0]!='campaign':
        if row[1] == 'video':
            video_set.add(row[0])


'''
Loading the source1.csv into a dict in the following way:

{campaign:{date:{spend: float, impressions: int, actions: [{}]}}

I'm converting each date to a python datetime object
'''
f = open('source1.csv')
csv_f = csv.reader(f)

source_map = OrderedDict()
dates_map = OrderedDict()
current = ''
first = True

for row in csv_f:
    if first == True:
        current = row[0]
        first = False
    each_date_map = {}
    if row[1]!='date':
        if current == row[0]:
            each_date_map['spend'] = float(row[2])
            each_date_map['impressions'] = int(row[3])
            each_date_map['actions'] = json.loads(row[4])
            dates_map[datetime.strptime(row[1], '%m/%d/%Y')] = each_date_map
        else:
            source_map[current] = dates_map
            current = row[0]
            dates_map = OrderedDict()
            each_date_map['spend'] = float(row[2])
            each_date_map['impressions'] = int(row[3])
            each_date_map['actions'] = json.loads(row[4])
            dates_map[datetime.strptime(row[1], '%m/%d/%Y')] = each_date_map

'''
All unique campaigns in February
'''
unique_campaigns = 0
source_map.pop('campaign')
for campaigns in source_map:
    campaign = source_map[campaigns]
    for camp in campaign:
        if(camp.month == 2):
            unique_campaigns+=1
            break

'''
Total number of conversions on plants
As per the assumption, I've only counted actions with types x or y for both conversions and views
'''
total_conversions = 0
for campaigns in source_map:
    if 'plants' in campaigns:
        campaign = source_map[campaigns]
        for camp in campaign:
            daily_record = campaign[camp]
            actions = daily_record['actions']
            for elem in filter(lambda x: 'conversions' in x['action'], actions):
                action = {k: v for k, v in elem.items() if 'action' not in k}
                if 'x' in action.keys() or 'y' in action.keys():
                    total_conversions+= next(iter(action.values()))

'''
audience, asset combination had the least expensive conversionsaudience, asset combination had the least expensive conversions:

Created a new map with keys in the format - audience_asset
The assets_map dict stores in the information in the following way:

{key:{spend: float, conversions: int}}

To calculate the combination with the least expensive conversions, I simply calculate the ration of conversions/spend
and return the highest ratio
'''
assets_map = OrderedDict()
for campaigns in source_map:
    campaign = source_map[campaigns]
    campaigns = campaigns.split('_')
    asset_key = campaigns[1]+'_'+campaigns[2]
    each_asset_map = {}
    for records in campaign:
        daily_record = campaign[records]
        actions = daily_record['actions']
        spend = daily_record['spend']
        for elem in filter(lambda x: 'conversions' in x['action'], actions):
            action = {k: v for k, v in elem.items() if 'action' not in k}
            if 'x' in action.keys():
                if 'conversions' in each_asset_map.keys():
                    each_asset_map['conversions'] = each_asset_map['conversions'] + next(iter(action.values()))
                else:
                    each_asset_map['conversions'] = next(iter(action.values()))
            if 'y' in action.keys():
                if 'conversions' in each_asset_map.keys():
                    each_asset_map['conversions'] += next(iter(action.values()))
                else:
                    each_asset_map['conversions'] = next(iter(action.values()))
        if 'spend' in each_asset_map.keys():
            each_asset_map['spend'] += spend
        else:
            each_asset_map['spend'] = spend

    if asset_key in assets_map.keys():
        old_map = assets_map[asset_key]
        old_map['spend'] += each_asset_map['spend']
        old_map['conversions'] += each_asset_map['conversions']
        assets_map[asset_key] = old_map
    else:
        assets_map[asset_key] = each_asset_map

least_expensive = 0.0
least_expensive_combination = ''
for key in assets_map:
    ratio = assets_map[key]['conversions']/assets_map[key]['spend']
    if ratio > least_expensive:
        least_expensive_combination = key
        least_expensive = ratio

'''
Total cost per video
'''
views = 0
amount = 0
for campaigns in source_map:
    if campaigns in video_set:
        campaign = source_map[campaigns]
        for records in campaign:
            daily_record = campaign[records]
            actions = daily_record['actions']
            amount += daily_record['spend']
            for elem in filter(lambda x: 'views' in x['action'], actions):
                action = {k: v for k, v in elem.items() if 'action' not in k}
                if 'x' in action.keys():
                    views += next(iter(action.values()))
                if 'y' in action.keys():
                    views += next(iter(action.values()))

total_cost_views = views/amount

print(unique_campaigns)
print(total_conversions)
print(least_expensive_combination, least_expensive)
print(total_cost_views)

