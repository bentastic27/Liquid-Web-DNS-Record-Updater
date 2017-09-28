#!/usr/bin/env python3
import urllib
import urllib.request
import base64
import json
from codecs import getreader
from os import environ


# get the settings from environment variables
API_USER = None
if 'STORM_API_USER' in environ.keys():
    API_USER = environ['STORM_API_USER']

API_PASS = None
if 'STORM_API_PASS' in environ.keys():
    API_PASS = environ['STORM_API_PASS']

RECORD_ID = None
if 'STORM_RECORD_ID' in environ.keys():
    RECORD_ID = environ['STORM_RECORD_ID']


def get_result(uri):
    url = "https://api.stormondemand.com" + uri
    
    # get the string for the auth header
    base64string = base64.b64encode(
        bytes('%s:%s' % (API_USER, API_PASS), 'ascii')
    )
    
    # getting the 'result' json string from the api
    request = urllib.request.Request(url)
    request.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))
    result = urllib.request.urlopen(request)
    
    # returning the data structure from the json string
    reader = getreader("utf-8")
    return json.load(reader(result))


def get_current_storm_ip():
    uri = "/v1/Network/DNS/Record/details?id=" + RECORD_ID
    return str(get_result(uri)['rdata'])


def get_current_real_ip():
    with urllib.request.urlopen("https://ip.beansnet.net/") as response:
        return response.read().decode('utf8')


def update_ip(new_ip):
    uri = "/v1/Network/DNS/Record/update?id=" + RECORD_ID
    uri += "&rdata=" + new_ip
    get_result(uri)
    return True


def get_record_id(zone, domain_name):
    uri = "/v1/Network/DNS/Record/list?zone=" + zone
    record_list = get_result(uri)['items']
    # find the record that matches the domain name in question
    for record in record_list:
        if record['name'] == domain_name:
            return str(record['id'])
    # return None if not found
    return None


if __name__ == '__main__':
    # for getting command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", help="Set record ID", type=str, dest='record_id',)
    parser.add_argument("--api-user", help="Set API username", type=str, dest='api_user',)
    parser.add_argument("--api-pass", help="Set API password", type=str, dest='api_pass',)
    parser.add_argument(
        "--get-record-id",
        help="Set mode to return the zone ID\nShould be used with --domain-name and --zone",
        action="store_true",
        dest='get_record_id',
    )
    parser.add_argument("--domain-name", help="Set domain name for --get-record-id", type=str, dest='domain_name')
    parser.add_argument("--zone", help="Set zone for --get-record-id", type=str, dest='zone')
    args = parser.parse_args()
    
    # set globals based on parser, otherwise leave them as is
    if args.record_id:
        RECORD_ID = args.record_id
    if args.api_user:
        API_USER = args.api_user
    if args.api_pass:
        API_PASS = args.api_pass
    
    # variable to set to True if there are errors
    error = False
    
    # making sure the globals are properly set before continuing
    if not API_USER or not API_PASS:
        if not API_USER:
            error = True
            print("*** api user not set ***")
        if not API_PASS:
            error = True
            print("*** api pass not set ***")
    
    # if in get_record_id and either domain name or zone are not set
    if args.get_record_id and (not args.domain_name or not args.zone):
        if not args.domain_name:
            error = True
            print("*** missing domain name ***")
        if not args.zone:
            error = True
            print("*** missing zone ***")
    
    # if we are in "get-record-id" mode, do that
    if args.get_record_id and args.domain_name and args.zone:
        # if error, print help text and exit
        if error:
            parser.print_help()
            exit()   
        print(get_record_id(args.zone, args.domain_name))
        exit()
    
    # finally, if not in "get-record-id" mode and no record id is set
    if not RECORD_ID:
        error = True
        print("*** record id not set ***")
    
    # if error, print help text and exit
    if error:
        parser.print_help()
        exit()
    
    # all is well, continue
    current_real_ip = get_current_real_ip()
    current_storm_ip = get_current_storm_ip()
    
    # update the IP if they do not match
    if current_real_ip != current_storm_ip:
        update_ip(current_real_ip)
