#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
from urllib.request import urlopen
import xmltodict

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    """ Write the body of the function that will be executed once the intent is recognized. 
    In your scope, you have the following objects : 
    - intentMessage : an object that represents the recognized intent
    - hermes : an object with methods to communicate with the MQTT bus following the hermes protocol. 
    - conf : a dictionary that holds the skills parameters you defined. 
      To access global parameters use conf['global']['parameterName']. For end-user parameters use conf['secret']['parameterName'] 
     
    Refer to the documentation for further details. 
    """

    if len(intentMessage.slots.channel) > 0:
        channel = intentMessage.slots.channel.first().value

    result_sentence = "Auf Channel " + channel + " kommt gerade "
    # file = urlopen('http://www.tvspielfilm.de/tv-programm/rss/heute2015.xml')
    # file = urlopen('http://www.tvspielfilm.de/tv-programm/rss/heute2200.xml')
    file = urlopen('http://www.tvspielfilm.de/tv-programm/rss/jetzt.xml')
    data = file.read()
    file.close()
    data = xmltodict.parse(data)

    for item in data['rss']['channel']['item']:
        if channel in item['title']:
            result_sentence = result_sentence + item['title'][8:]

    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)
    


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("Philipp:AddItem", subscribe_intent_callback) \
         .start()
