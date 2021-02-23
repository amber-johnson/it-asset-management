import re
import requests
import pexpect
from requests import ConnectTimeout

from .models import Powered

from django.conf import settings

PDU_url = "http://hyposoft-mgt.colab.duke.edu:8008/"
GET_suf = "pdu.php"
POST_suf = "power.php"
rack_pre = "hpdu-rtp1-"

SSH_CMD = 'ssh admin8@hyposoft-mgt.colab.duke.edu -p 2222'
SSH_NEWKEY = '(?i)are you sure you want to continue connecting'
ENTER_PASSWORD = '(?i)password'
PROMPT = 'bcman'
PASSWORD = getattr(settings, 'BCMAN_PASSWORD')

def to_prompt():
    child = pexpect.spawn(SSH_CMD)
    i = child.expect([SSH_NEWKEY, ENTER_PASSWORD])
    if i == 0:
        child.sendline('yes')
        child.expect(ENTER_PASSWORD)
    child.sendline(PASSWORD)
    child.expect(PROMPT, timeout=5)

    return child


def is_blade_power_on(hostname, slot):
    child = to_prompt()
    child.sendline('chassis {}'.format(hostname))
    child.expect(PROMPT, timeout=5)
    child.sendline('blade {}'.format(slot))
    child.expect(PROMPT, timeout=5)
    child.sendline('power')
    child.expect(PROMPT, timeout=5)
    child.kill(0)
    return "is ON" in child.before.decode("utf-8")


def set_blade_power(hostname, slot, state):
    child = to_prompt()
    child.sendline('chassis {}'.format(hostname))
    child.expect(PROMPT, timeout=5)
    child.sendline('blade {}'.format(slot))
    child.expect(PROMPT, timeout=5)
    child.sendline('power {}'.format(state))
    child.expect(PROMPT, timeout=5)
    child.kill(0)


def get_pdu(rack, position):
    try:
        split = re.search(r"\d", rack).start()
        rack = rack[:split] + "0" + rack[split:]
        response = requests.get(PDU_url + GET_suf, params={'pdu': rack_pre + rack + position}, timeout=0.5)
        code = response.status_code
        # The following regex extracts the state of each port on the pdu
        # The format is a list of tuples, e.g. [('1', 'OFF'), ('2', 'ON'), ...]
        result = re.findall(r"<td>(\d{1,2})<td><span style=\'background-color:#[0-9a-f]{3}\'>(ON|OFF)", response.text)
        # If there are no matches, the post failed so return the error text
        if len(result) == 0:
            result = response.text
            code = 400
    except ConnectTimeout:
        return "couldn't connect", 400
    return result, code


def post_pdu(rack, position, port, state):
    try:
        split = re.search(r"\d", rack).start()
        rack = rack[:split] + "0" + rack[split:]
        response = requests.post(PDU_url + POST_suf, {
            'pdu': rack_pre + rack + position,
            'port': port,
            'v': state
        }, timeout=0.5)
        # The following regex extracts the result string from the HTML response text
        # If there are no matches, the post failed so return the error text
        result = re.findall(r'(set .*)\n', response.text)
        result = result[0] if len(result) > 0 else response.text

    except ConnectTimeout:
        return "couldn't connect", 400
    return result, response.status_code


def update_asset_power(asset):
    if asset.site.abbr.lower() == 'rtp1' and asset.rack and 'A1' <= asset.rack.rack <= 'E19':
        pdus = asset.pdu_set.all()
        for pdu in pdus:
            states, status_code = get_pdu(pdu.rack.rack, pdu.position)
            if status_code >= 400:
                pdu.networked = False
                continue
            pdu.networked = True
            for state in states:

                try:
                    entry = Powered.objects.filter(asset=asset, pdu=pdu, plug_number=state[0])
                except Powered.DoesNotExist:
                    continue
                entry.update(on=state[1] == 'ON')
            pdu.save()
