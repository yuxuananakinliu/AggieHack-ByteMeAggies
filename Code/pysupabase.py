import pandas as pd
from supabase import create_client
from getapi import ext_api

def create_conn(apifile:str):
    '''Create connection to Supabase database via API call'''
    supaapi = ext_api(apifile)
    sb_client = create_client(supaapi['URL'], supaapi['APIKEY'])
    return sb_client

def rolling_query(api_file:str, table_name:str, target_col:str='*', query_limit:int=1000)->pd.DataFrame:
    '''Query data from Supabase in batches, return all columns by default'''
    all_rows = []
    offset = 0
    sb_client = create_conn(api_file)

    while True:
        response = sb_client.table(table_name).select(
            target_col
        ).range(offset, offset+query_limit-1).execute()
        if not response.data:
            break
        all_rows.extend(response.data)
        offset += query_limit

    return pd.DataFrame(all_rows)