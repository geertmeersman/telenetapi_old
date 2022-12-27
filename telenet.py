import telenetapi 
import json
from datetime import datetime

telenet_session = telenetapi.TelenetSession()
telenet_session.login("xxxxxxxxx@xxxxxxx.xx", "xxxxxxxxxxxxxxxxxxxx")

telenet_json = {}
mobile = telenet_session.mobile()
internet = telenet_session.internet()
userdetails = telenet_session.userdetails()
mob = {}

for product in mobile['mobileusage']:
    product["daysremaining"] = (datetime.strptime(product["nextbillingdate"], "%Y-%m-%dT%H:%M:%S.%f+01:00") - datetime.now().today()).days
    replacing = {}
    for ms in product["unassigned"]["mobilesubscriptions"]:
        replacing[ms["mobile"]] = ms
    product["unassigned"]["mobilesubscriptions"] = replacing

    profiles = {}
    for profile in product["profiles"]:
        replacing = {}
        for ms in profile["mobilesubscriptions"]:
            replacing[ms["mobile"]] = ms
        profile["mobilesubscriptions"] = replacing
        profiles[profile["pid"]] = profile
    product["profiles"] = profiles
    mob[product['identifier']] = product

telenet_json["mobile"] = mob
telenet_json["internet"] = internet
telenet_json["userdetails"] = userdetails

print(json.dumps(telenet_json, indent = 4))
exit()
