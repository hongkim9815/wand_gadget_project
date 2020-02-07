#!/usr/bin/python3
"""
Title   api.py
Author  Kihong Kim (Undergraduate Student, School of Computing, KAIST)
Made    30-Jan-2020
Comment This program is test for compatibility with API of framework on magicoding.io.
"""

import requests
import json
import pprint


if __name__ == "__main__":
    try:
        result = requests.get("http://ec2-13-209-200-6.ap-northeast-2.compute.amazonaws.com"
                              + "/api/Gateway/Wands/%02d/User" % (1))
    except requests.exceptions.ConnectionError:
        print("requests: requests.get() got an exception...")
        exit(0)

    result = result.text
    print(result)
    result = json.loads(result)

    if result['result_state'] is not 1:
        print("requests: requests.get() got an exception...")
        exit(0)

    # print(result)
    result = result['result']
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(result)
    # print(result)
    # print(result['user_info'])
    # print(result['user_info']['user_uid'])
    # print(result['today_mission']['mission_order'])
    # print(result['today_mission']['mission_title'])
    for rt in result['unit_list']:
        for rtt in rt['mission_list']:
            if rtt['mission_order'] == result['today_mission']['mission_order']:
                print(rtt)
                break

    for rt in result['badge_info']:
        print(rt['badge_url'])

