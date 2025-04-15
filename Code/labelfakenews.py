from datetime import datetime, timedelta
from pysupabase import rolling_query

# Function to extract 
def extract_type(text:str)->str|None:
    '''Return the disaster type mentioned in the report, None if not specified'''
    if 'earthquake' in text.lower():
        return 'earthquake'
    if 'fire' in text.lower():
        return 'fire'
    if 'flood' in text.lower():
        return 'flood'
    else:
        return None


# Main function for fake report detection
def fake_check(api_file:str, dis_type:str|None, when:str, latit:float, longi:float)->bool:
    '''Search around the disaster report to test whether it is fake, return true for fake reports'''
    when = datetime.fromisoformat(when)
    if dis_type == 'earthquake':
        lar = 0.3
        lor = 0.38
    elif dis_type == 'fire':
        lar = 0.0045
        lor = 0.0057
    elif dis_type == 'flood':
        lar = 0.1
        lor = 0.13
    # If no disaster type specified, search all kind of them
    else:
        lar = 0.3
        lor = 0.38

    where_condition = {
        'timestamp':(when - timedelta(hours=24), '>'),
        'timestamp':(when, '<='),
        'latitude':(latit-lar, '>='),
        'latitude':(latit+lar, '<='),
        'longitude':(longi-lor, '>='),
        'longitude':(longi+lor, '<=')
    }
    if dis_type:
        where_condition['type'] = (dis_type, '=')

    # Search nearby disasters
    nearby = rolling_query(
        api_file, 
        'disaster_set',
        where=where_condition
    )

    if nearby.empty:
        return True
    return False