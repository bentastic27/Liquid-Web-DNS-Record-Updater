# Liquid-Web-DNS-Record-Updater
A python script to update a dns record to your current internet routable IP. Handy on public facing home servers. This is to be used on domain names whose zone resides on Liquid Web's DNS servers.

## Requirements
* Python 3
* An API user for manage.liquidweb.com with the "network" privilege
* The domain name must be hosted on LW's nameservers in that account

## Usage

The help page (The `-h` or `--help` flags):

```
# python3 ./update_record.py -h

usage: update_record.py [-h] [--record-id RECORD_ID] [--api-user API_USER]
                        [--api-pass API_PASS] [--get-record-id]
                        [--domain-name DOMAIN_NAME] [--zone ZONE]

optional arguments:
  -h, --help            show this help message and exit
  --record-id RECORD_ID
                        Set record ID
  --api-user API_USER   Set API username
  --api-pass API_PASS   Set API password
  --get-record-id       Set mode to return the zone ID Should be used with
                        --domain-name and --zone
  --domain-name DOMAIN_NAME
                        Set domain name for --get-record-id
  --zone ZONE           Set zone for --get-record-id
  ```
  
First, before the script can change the IP for a domain name, you will need to know the record ID. To get it:
  
  ```
  python3 ./update_record.py --get-record-id --api-user API_USER --api-pass API_PASS --domain-name subdomain.domain.com --zone domain.com
  ```
  
This assumes that you are trying to change the IP of subdomain.domain.com and the zone is just domain.com
  
Once you know that, you can throw this command into a cron. On my Raspberry PI, I have it set to run every 30 minutes:

```
0,30 * * * * /usr/bin/python3 /scripts/update_record.py --api-user API-USER --api-pass API-PASS --record-id RECORD-ID
```

At this point it will check for your current routable IP, then compare it to what is current set for the record, and update it via the Storm API if need be.
