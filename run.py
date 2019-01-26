#!/usr/bin/env python3
import os
import sys
import time
import re
from datetime import datetime, timedelta

from telethon import TelegramClient, events, utils

# Config Class
from telegram_interceptor import sanitized as conf

import logging
logging.basicConfig(level=logging.WARNING)


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


session = os.environ.get('TG_SESSION', 'printer')
if conf.API_ID:
    api_id = conf.API_ID
else:
    get_env('TG_API_ID', 'Enter your API ID: ', int)
if conf.API_HASH:
    api_hash = conf.API_HASH
else:
    get_env('TG_API_HASH', 'Enter your API hash: ')
proxy = conf.PROXY  

# Create and start the client so we can make requests (we don't here)
client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()


# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".

#@client.on(events.NewMessage())
#@client.on(events.NewMessage(pattern=r'(?im)^[\s\S]+(EX Raid Eligible)[\s\S]+'))
@client.on(events.NewMessage(pattern=r'(?im)^[\s\S]+('+ conf.FILTER_GYM_NAME +')[\s\S]+'))
async def handler(event):
    sender = await event.get_sender()
    name = utils.get_display_name(sender)
    
    gym_name = None
    start_time = None
    end_time = None
    is_egg = None
    egg_level = None
    is_hatched = None
    hatched_mon = None
    hatched_level = None
    coords = None
    
    full_string = None
    #await client.forward_messages(513861616, event.message, event.chat)
    #print(event.text)
    #print('{} Data Filtered: \n{}'.format(datetime.now(),event.text))
    print('{} There is data coming in...'.format(datetime.now()))
    
    pattern = '(?im)(?<=\*\*Gym name\*\*: ).*$'
    match = re.search(pattern,event.text)
    #gymname = match.group(1)
    if match:
        gym_name = match.group()
        #print('{} Gym Name: {}'.format(datetime.now(),gym_name))
    
    pattern = '(?im)(?<=\*\*Start\*\*: ).*$'
    match = re.search(pattern,event.text)
    if match:
        start_time = match.group()
        
    pattern = '(?im)(?<=\*\*End\*\*: ).*$'
    match = re.search(pattern,event.text)
    if match:
        end_time = match.group()
        
    pattern = '(?im)(?<=\*\*Egg\*\* - ).*$'
    match = re.search(pattern,event.text)
    if match:
        is_egg = True
        egg_level = match.group()
    else:
        is_egg = False
    
    
    
    pattern = '(?im).*] \*\*(.*?)\*\* - Level.*$'
    match = re.search(pattern,event.text)
    if match:
        is_hatched = True
        hatched_mon = match.group(1)
    else:
        is_hatched = False
    
    pattern = '(?im).*\*\* - Level: (.*?) - CP: .*$'
    match = re.search(pattern,event.text)
    if match:
        hatched_level = match.group(1) 
        
    pattern = '(?im)(?<=maps\?q=).*$'
    match = re.search(pattern,event.text)
    if match:
        coords = match.group().replace(')','')
        
    if is_egg:
        full_string = 'Level {} Egg hatching at \n[{}](https://maps.google.com/maps?q={})\nStart Time: {}\nEnd Time: {}'.format(egg_level,gym_name,coords,start_time,end_time)
        await client.send_message(conf.FORWARD_ID,full_string,link_preview=False)
    if is_hatched:
        full_string = 'Level {} - **{}** hatched at \n[{}](https://maps.google.com/maps?q={})\nStart Time: {}\nEnd Time: {}'.format(hatched_level,hatched_mon,gym_name,coords,start_time,end_time)
        await client.send_message(conf.FORWARD_ID,full_string,link_preview=False)
        
    if full_string:
        print('{} Sendind Data: {}'.format(datetime.now(),full_string))
    
    
    # Check if this is Ex Raid
    pattern = '(?im)^Will hatch Deoxys, ex pass required to see'
    checkex = re.search(pattern, event.text)
    # This is an ex raid, send to webhook for processing
    if checkex:
        a=0 #[dummpy value]

try:
    print('{} Running Telegram Interceptor...'.format(datetime.now()))
    print('{} (Press Ctrl+C to stop this)'.format(datetime.now()))
    client.run_until_disconnected()
finally:
    client.disconnect()

# Note: We used try/finally to show it can be done this way, but using:
#
#   with client:
#       client.run_until_disconnected()
#
# is almost always a better idea.