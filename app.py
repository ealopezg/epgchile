import requests
import json
from xml.etree.ElementTree import ElementTree, Element, SubElement, tostring
from datetime import datetime, timedelta
import os
from flask import Flask,Response

app = Flask(__name__)

@app.route('/')
def index():
    with open("channels.json") as json_channels:
        channels = json.load(json_channels)
    
    channel_list = ",".join(channels.keys())
    tree = ElementTree()
    tv = Element('tv')
    tree._setroot(tv)
    for channel in channels:
        ch_element = Element('channel',{"id": channels[channel]["TVG-ID"]})
        ch_display_name = SubElement(ch_element,'display-name')
        ch_display_name.text=channels[channel]["Name"]
        tv.append(ch_element)
    date_today = datetime.today()
    dates = []
    for i in range(3):
        dates.append(date_today + timedelta(days=i))
    for date in dates:
        date_start = (date - timedelta(hours=1)).strftime('%s')
        date_end = (date  + timedelta(days=1)).strftime('%s')
        payload = {
            "ca_deviceTypes": "null|401",
            "fields": "Title,Description,Start,End,LiveChannelPid",
            "orderBy": "START_TIME:a",
            "filteravailability": "false",
            "starttime": date_start,
            "endtime": date_end,
            "livechannelpids": channel_list
        }
        r = requests.get('https://contentapi-cl.cdn.telefonica.com/26/default/es-CL/schedules',params=payload)
        programs = r.json()['Content']
        
        

        for program in programs:
            program_params = {
                "start": datetime.utcfromtimestamp(program["Start"]).strftime('%Y%m%d%H%M%S')+" +0000",
                "stop": datetime.utcfromtimestamp(program["End"]).strftime('%Y%m%d%H%M%S')+" +0000",
                "channel": channels[program["LiveChannelPid"]]["TVG-ID"]
            }
            titles = program["Title"].split(" : ")
            pr_element = Element('programme',program_params)
            pr_title = SubElement(pr_element,'title',{"lang":"es"})
            pr_title.text = titles[0]
            if len(titles) > 1:
                pr_subtitle = SubElement(pr_element,'sub-title',{"lang":"es"})
                pr_subtitle.text = " : ".join(titles[1:])
            pr_desc = SubElement(pr_element,'desc',{"lang":"es"})
            pr_desc.text = program["Description"]
            tv.append(pr_element)




    #tree.write("guide.xml",xml_declaration=True,encoding='utf-8',method="xml")
    xmlstr = tostring(tv,xml_declaration=True,encoding='utf-8',method="xml")
    return Response(xmlstr, mimetype='text/xml')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
