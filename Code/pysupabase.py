from supabase import create_client
from getapi import ext_api

def create_conn(apifile:str):
    supaapi = ext_api(apifile)
    sb_client = create_client(supaapi['URL'], supaapi['APIKEY'])
    return sb_client