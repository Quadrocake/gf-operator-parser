import json

def generate_dashboard_dict(data):
    dashboard_dict = {}
    for item in data['items']:
        dashboard_dict[item['metadata']['name']] = json.loads(item['spec']['json'])
    return(dashboard_dict)

def find_json_key(search_key, input_data):
    if isinstance(input_data, dict):
        for k, v in input_data.items():
            if k == search_key:
                yield v
            else:
                yield from find_json_key(search_key, v)
    elif isinstance(input_data, list):
        for item in input_data:
            yield from find_json_key(search_key, item)

def get_object_names(data):
    dash_list = []
    for item in data['items']:
        dash_list.append(item['metadata']['name'])
    return(dash_list)