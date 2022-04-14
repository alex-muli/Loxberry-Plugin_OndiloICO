#!/usr/bin/python3
# encoding=utf-8

# Version 2022-04-14_V23 Loxberry Plugin - Ondilo ICO Poolsensor

import requests
import getpass
import random
import string
import datetime
import argparse
import socket
import sys
import time
import os
import configparser
import json
import logging
import urllib.parse
from datetime import datetime, timedelta
from lxml import html
import os.path


def main(args):

    # ---------------------------------------------
    ### Global variables
    # ---------------------------------------------
    separator = ";"
    
    # ---------------------------------------------
    ### Check if running in debug mode
    # ---------------------------------------------
    if args.debug:
        import debugpy
        print("running in debug mode - waiting for debugger connection on {0}:{1}".format(args.debugip, args.debugport))
        debugpy.listen((args.debugip, args.debugport))
        debugpy.wait_for_client()

    # ---------------------------------------------
    ### Parse PlugIn config file
    # ---------------------------------------------
   
    lbpConfigICOCFG = os.path.join(PConfig.plugin("LBPCONFIG"),"ICO", "ico.cfg")
    lbpConfigICOtoken = os.path.join(PConfig.plugin("LBPCONFIG"),"ICO", "token.txt")
    #print('lbpConfigICOCFG:',lbpConfigICOCFG)
    #print('lbpConfigICOtoken:',lbpConfigICOtoken)
    
    if not os.path.exists(lbpConfigICOCFG):
        logging.critical("Plugin configuration file missing {0}".format(lbpConfigICOCFG))
        sys.exit(-1)
    
    
        
    pluginconfig = configparser.ConfigParser()
    pluginconfig.read(lbpConfigICOCFG)
    username = pluginconfig.get('ICO', 'USERNAME')
    password = pluginconfig.get('ICO', 'PASSWORD')
    enabled = pluginconfig.get('ICO', 'ENABLED')
    localtime = pluginconfig.get('ICO', 'ENABLED')
    miniservername = pluginconfig.get('ICO', 'MINISERVER')
    virtualUDPPort = int(pluginconfig.get('ICO', 'UDPPORT'))
    
    # ---------------------------------------------
    ### transistion from general.cfg to general.json
    # ---------------------------------------------
    
    if miniservername.startswith("MINISERVER"):
        miniserverID = miniservername.replace("MINISERVER", "")
    
    else:
        miniserverID = miniservername
        miniservername = "MINISERVER{0}".format(miniserverID)

    # ---------------------------------------------
    ### Check if general.json exists and Loxberry version > 2.2
    # ---------------------------------------------
    lbsConfigGeneralJSON = os.path.join(Config.Loxberry("LBSCONFIG"), "general.json")
    lbsConfigGeneralCFG = os.path.join(Config.Loxberry("LBSCONFIG"), "general.cfg")

    if not os.path.exists(lbsConfigGeneralJSON):
        logging.warning("gerneral.json missing in path {0}".format(lbsConfigGeneralJSON))
        logging.warning("trying general.cfg instead {0}".format(lbsConfigGeneralCFG))

        if not os.path.exists(lbsConfigGeneralCFG):
            logging.critical("general.cfg not found in path {0}".format(lbsConfigGeneralCFG))
            sys.exit(-1)

        # ---------------------------------------------
        ### general.cfg (legacy configuration file)
        # ---------------------------------------------
        
        logging.info("using system configuration file {0}/general.cfg".format(Config.Loxberry("LBSCONFIG")))
        loxberryconfig = configparser.ConfigParser()
        loxberryconfig.read("{0}/general.cfg".format(Config.Loxberry("LBSCONFIG")))
        miniserverIP = loxberryconfig.get(miniservername, 'IPADDRESS')
    
    else:
        with open(lbsConfigGeneralJSON, "r") as lbsConfigGeneralJSONHandle:
            logging.info("using system configuration file {0}/general.json".format(Config.Loxberry("LBSCONFIG")))
            data = json.load(lbsConfigGeneralJSONHandle)

        ### check if miniserver from plugin config exists in general.json
        if not miniserverID in data["Miniserver"].keys():
            logging.critical("Miniserver with id {0} not found general.json - please check plugin configuration".format(miniserverID))
            sys.exit(-1)

        miniserverIP = data["Miniserver"][miniserverID]["Ipaddress"]
        MSFulluri = data["Miniserver"][miniserverID]["Fulluri"]
        logging.info("Miniserver ip address: {0}".format(miniserverIP))


    # ---------------------------------------------
    ### exit if PlugIn is not enabled
    # ---------------------------------------------
    if enabled != "1":
        logging.warning("Plugin is not enabled in configuration - exiting")
        sys.exit(-1)

    # ---------------------------------------------
    ### start new request session
    # ---------------------------------------------
    session = requests.Session()

    # ---------------------------------------------
    ### set User-Agent to emulate Windows 10 / IE 11
    # ---------------------------------------------
    session.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'}
     
    # ---------------------------------------------
    ### Open socket connection
    # ---------------------------------------------
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



# ---------------------------------------------------------------------------------------
### Check if refresh_token in tokens.txt file ###
# ---------------------------------------------------------------------------------------
    if os.path.isfile(lbpConfigICOtoken):
        with open(lbpConfigICOtoken, "r") as f:
            for refresh_token in f: pass
    else: refresh_token = '1234'

# ---------------------------------------------------------------------------------------
### Get access token ###
# ---------------------------------------------------------------------------------------
    access_token = OndiloAPI().get_access_token(refresh_token)

# ---------------------------------------------------------------------------------------
### Authentication with Ondilo user credentials if access token not retrieved ###
### (no refresh_token or refresh_token expired) - Add refresh_token to token.txt file ###
# ---------------------------------------------------------------------------------------
    if access_token == "Error":
        print('Authentication needed for new Refresh_Token : ')
        #username = input('Username:')
        #password = getpass.getpass(prompt='Password: ')
        refresh_token = OndiloAPI().get_refresh_token(username, password)
        f = open(lbpConfigICOtoken, "a")
        f.write("\n")
        f.write(refresh_token)
        f.close()

# ---------------------------------------------------------------------------------------
### Get access_token ###
# ---------------------------------------------------------------------------------------
    access_token = OndiloAPI().get_access_token(refresh_token)

# ---------------------------------------------------------------------------------------
### Get and print ICOs infos ###
# ---------------------------------------------------------------------------------------
    if enabled == "1":
        infos = OndiloAPI().get_infos(access_token)

        #print("Infos:",infos)
        #print('------------------------------------')
        #for i in infos:
        #    print("NAME: ",i['address'])
        #print('------------------------------------')

    # ---------------------------------------------------------------------------------------
    ### Display Pool Id and Refresh_Token###
    # ---------------------------------------------------------------------------------------

        pool_id = OndiloAPI().get_infos(access_token)[0]['id']
        print('\n')
        print('--------------------------------------------------------')
        print('Pool ID :',pool_id)
        print('Refresh Token :',refresh_token)
        print('(Refresh Token added to token.txt)')
        print('--------------------------------------------------------')
        print('\n')

    # ---------------------------------------------------------------------------------------
    ### Get and print units infos ###
    # ---------------------------------------------------------------------------------------

        units = OndiloAPI().get_units(access_token)
        #print("units:",units)
        #print('------------------------------------')

        #units_conductivity = OndiloAPI().get_units(access_token)['conductivity']
        #units_hardness = OndiloAPI().get_units(access_token)['hardness']
        units_orp = OndiloAPI().get_units(access_token)['orp']
        units_pressure = OndiloAPI().get_units(access_token)['pressure']
        units_salt = OndiloAPI().get_units(access_token)['salt']
        units_speed = OndiloAPI().get_units(access_token)['speed']
        units_temperature = OndiloAPI().get_units(access_token)['temperature']
        units_volume = OndiloAPI().get_units(access_token)['volume']
        units_tds = OndiloAPI().get_units(access_token)['tds']
        #print("Units:",units_temperature)

        conf_temp_low = OndiloAPI().get_configuration(pool_id, access_token)['temperature_low']
        conf_temp_high = OndiloAPI().get_configuration(pool_id, access_token)['temperature_high']
        conf_ph_low = OndiloAPI().get_configuration(pool_id, access_token)['ph_low']
        conf_ph_high = OndiloAPI().get_configuration(pool_id, access_token)['ph_high']
        conf_orp_low = OndiloAPI().get_configuration(pool_id, access_token)['orp_low']
        conf_orp_high = OndiloAPI().get_configuration(pool_id, access_token)['orp_high']
        conf_salt_low = OndiloAPI().get_configuration(pool_id, access_token)['salt_low']
        conf_salt_high = OndiloAPI().get_configuration(pool_id, access_token)['salt_high']
        conf_tds_low = OndiloAPI().get_configuration(pool_id, access_token)['tds_low']
        conf_tds_high = OndiloAPI().get_configuration(pool_id, access_token)['tds_high']


        #print("configuration:",conf_temp_low)

    # ---------------------------------------------------------------------------------------
    ### Get and print last measures ###
    # ---------------------------------------------------------------------------------------
        data = OndiloAPI().get_values(pool_id, access_token)
        date_time_obj = datetime.strptime(data[0]['value_time'], '%Y-%m-%dT%H:%M:%S+0000') + timedelta(hours=2)

        print('------------------------------------')
        print('LAST MEASURES :',date_time_obj)
        for i in data:
            print(" ",i['data_type'],":",i['value'])
            packet = "{0}.{1}.{2}={3}".format("Ondilo_ICO_last:measure",date_time_obj, i['data_type'], i['value'])
            #print(" ",packet)
            #sock.sendto(bytes(packet, 'utf-8'), (miniserverIP, virtualUDPPort))
        print('------------------------------------')
    
    # ---------------------------------------------------------------------------------------
    ### Get a list active recommendations ###
    # ---------------------------------------------------------------------------------------
        recommendations = OndiloAPI().get_recommendations(pool_id, access_token)
        n = int(0)
        print('------------------------------------')
        h = requests.post(str(MSFulluri) + '/dev/sps/io/ICO1/...')
        h = requests.post(str(MSFulluri) + '/dev/sps/io/ICO2/...')
        h = requests.post(str(MSFulluri) + '/dev/sps/io/ICO3/...')
        h = requests.post(str(MSFulluri) + '/dev/sps/io/ICO4/...')
        print('ICO1-4 gelöscht')
        
        for i in recommendations:
            n = n + 1
            created_time_obj = datetime.strptime(i['created_at'], '%Y-%m-%dT%H:%M:%S+0000') + timedelta(hours=2)
            updated_time_obj = datetime.strptime(i['updated_at'], '%Y-%m-%dT%H:%M:%S+0000') + timedelta(hours=2)
            print('------------------------------------')
            print(n)
            print('------------------------------------')
            print('Notification von: ',created_time_obj, 'Update am: ',updated_time_obj)
            print(i['title'],":",i['message'])
            packet = "{0}.{1}.{2}={3}".format("Ondilo_ICO_recommendations",created_time_obj, i['title'], i['message'])
            http_packet = "{0} Beschreibung: {1} von: {2} update am: {3} ".format(i['title'], i['message'], created_time_obj, updated_time_obj)
            print('------------------------------------')
            print(i)
            print('------------------------------------')
            #print(" ",packet)
            #sock.sendto(bytes(packet, 'utf-8'), (miniserverIP, virtualUDPPort))
            h = requests.post(str(MSFulluri) + '/dev/sps/io/ICO' + str(n) + '/' + str(http_packet))

            #if h.status_code != 200:
                #auth_error = 1
                #print('Authentication error')
                #exit()
            print('------------------------------------')
        
        
    # ---------------------------------------------------------------------------------------
    ### Send UDP-Messages and print UDP-Messages ###
    # ---------------------------------------------------------------------------------------
        print(" ")
        print("Send follow UDP-Messages to Miniserver: ",miniserverIP," on  UDP-Port: ",virtualUDPPort)
        print(" ")
        temp = OndiloAPI().get_values(pool_id, access_token)[0]['value']
        packet_temp = "{0}.{1}_min{2}_={3}_max{4}-{5}".format("Ondilo_ICO_Temperatur",date_time_obj, conf_temp_low, temp, conf_temp_high, units_temperature)
        print(packet_temp)
        sock.sendto(bytes(packet_temp, 'utf-8'), (miniserverIP, virtualUDPPort))
        
        orp = OndiloAPI().get_values(pool_id, access_token)[1]['value']
        packet_orp = "{0}.{1}_min{2}_={3}_max{4}-{5}".format("Ondilo_ICO_ORP",date_time_obj, conf_orp_low, orp ,conf_orp_high, units_orp)
        print(packet_orp)
        sock.sendto(bytes(packet_orp, 'utf-8'), (miniserverIP, virtualUDPPort))
        
        ph = OndiloAPI().get_values(pool_id, access_token)[2]['value']
        packet_ph = "{0}.{1}_min{2}_={3}_max{4}".format("Ondilo_ICO_PH",date_time_obj, conf_ph_low, ph ,conf_ph_high)
        print(packet_ph)
        sock.sendto(bytes(packet_ph, 'utf-8'), (miniserverIP, virtualUDPPort))
        
        tds = OndiloAPI().get_values(pool_id, access_token)[3]['value']
        packet_tds = "{0}.{1}_min{2}_={3}_max{4}-{5}".format("Ondilo_ICO_TDS",date_time_obj, conf_tds_low, tds ,conf_tds_high, units_tds)
        print(packet_tds)
        sock.sendto(bytes(packet_tds, 'utf-8'), (miniserverIP, virtualUDPPort))
        
        battery = OndiloAPI().get_values(pool_id, access_token)[4]['value']
        packet_battery = "{0}.{1}_{2}%".format("Ondilo_ICO_Battery",date_time_obj, battery)
        print(packet_battery)
        sock.sendto(bytes(packet_battery, 'utf-8'), (miniserverIP, virtualUDPPort))
        
        rssi = OndiloAPI().get_values(pool_id, access_token)[5]['value']
        packet_rssi= "{0}.{1}_{2}%".format("Ondilo_ICO_Rssi",date_time_obj, rssi)
        print(packet_rssi)
        sock.sendto(bytes(packet_rssi, 'utf-8'), (miniserverIP, virtualUDPPort))
           
        sys.exit(0)


class OndiloAPI(): 
# ---------------------------------------------------------------------------------------
### Ondilo API - Connection
# ---------------------------------------------------------------------------------------

    def __init__(self):
        self._auth_url = 'https://interop.ondilo.com/oauth2/'
        self._api_url = 'https://interop.ondilo.com/api/customer/v1/'

# ---------------------------------------------------------------------------------------
### Use Ondilo credentials to get an authorization code, then get a refresh_token : ###
### Post request to ondilo authorize url with random state and fake redirect_uri ###
### Retrieve authorization_code in the response location header ###
### Post request to ondilo token url to generate and retrive a refresh_token ###
# ---------------------------------------------------------------------------------------
    def get_refresh_token(self, username, password):
        def random_state(stringLength=16):
            lettersAndDigits = string.ascii_lowercase + string.digits
            return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))
        post_url = self._auth_url + 'authorize'
        state = random_state(24)
        post_data = {'login':username,
                     'password':password,
                     'locale' :'de',
                     'proceed' :'Authorize'}
        post_params = {'client_id':'customer_api',
					   'response_type' :'code',
					   'redirect_uri' :'https://1.2.3.4/authorize',
					   'scope':'api',
					   'state':state}

        r = requests.post(url = post_url, params = post_params, data = post_data, allow_redirects=False)

        if r.status_code != 302:
            auth_error = 1
            print('Authentication error')
            exit()

        location = r.headers['location']
        left = 'code='
        right = '&state='
        authorization_code = location[location.index('code=')+len('code='):location.index('&state=')]

        post_url = self._auth_url + 'token'
        post_data = {'code':authorization_code,
		             'grant_type':'authorization_code',
				     'client_id':'customer_api',
				     'redirect_uri':'https://1.2.3.4/authorize'}

        r = requests.post(url = post_url, data = post_data)
        data = r.json()

        if not "refresh_token" in data:
            print('Token cannot be retrieved :')
            print(data['error'])
            print(data['error_description'])

        refresh_token = data['refresh_token']
        return refresh_token
# ---------------------------------------------------------------------------------------
### Use the refresh_token to get an access_token  ###
# ---------------------------------------------------------------------------------------
    def get_access_token(self, refresh_token):
        auth_url = self._auth_url + 'token'
        auth_data = {'refresh_token':refresh_token,
					'grant_type':'refresh_token',
					'client_id' : 'customer_api'}
        r = requests.post(url = auth_url, data = auth_data)
        data = r.json()

        if not "access_token" in data:
            access_token = "Error"
            print('Error : ',data['error_description'] )
            return access_token

        access_token = data['access_token']
        return access_token
# ---------------------------------------------------------------------------------------
### Retrieve the pool infos   ###
# ---------------------------------------------------------------------------------------
    def get_infos(self, access_token):
        pool_url = self._api_url + "pools"
        headers = {'Authorization': 'Bearer '+str(access_token),
					'Accept': 'application/json',
					'Accept-Charset': 'utf-8',
					'Accept-Encoding': 'gzip-deflate',}

        r = requests.get(url = pool_url, headers = headers)
        data = r.json()
        return data
# ---------------------------------------------------------------------------------------
### Retrieve the pool units   ###
# ---------------------------------------------------------------------------------------
    def get_units(self, access_token):
        units_url = self._api_url + "user/units"
        headers = {'Authorization': 'Bearer '+str(access_token),
					'Accept': 'application/json',
					'Accept-Charset': 'utf-8',
					'Accept-Encoding': 'gzip-deflate',}

        r = requests.get(url = units_url, headers = headers)
        data = r.json()
        return data

# ---------------------------------------------------------------------------------------
### Retrieve the last measures  ###
# ---------------------------------------------------------------------------------------
    def get_values(self, pool_id, access_token):
        last_url = self._api_url + 'pools/' + str(pool_id) + '/lastmeasures'
        headers = {'Authorization': 'Bearer '+str(access_token),
            		'Accept': 'application/json',
					'Accept-Charset': 'utf-8',
					'Accept-Encoding': 'gzip-deflate',
					'Content-type': 'application/json'}
        r = requests.get(url = last_url, headers = headers)
        data = r.json()
        return data

# ---------------------------------------------------------------------------------------
### Retrieve the configuration  ###
# ---------------------------------------------------------------------------------------
    def get_configuration(self, pool_id, access_token):
        conf_url = self._api_url + 'pools/' + str(pool_id) + '/configuration'
        headers = {'Authorization': 'Bearer '+str(access_token),
            		'Accept': 'application/json',
					'Accept-Charset': 'utf-8',
					'Accept-Encoding': 'gzip-deflate',
					'Content-type': 'application/json'}
        r = requests.get(url = conf_url, headers = headers)
        data = r.json()
        return data

# ---------------------------------------------------------------------------------------
### Retrieve the history measures  ###
# ---------------------------------------------------------------------------------------
    def get_history(self, pool_id, access_token, type, periode):
        hist_url = self._api_url + 'pools/' + str(pool_id) + '/measures'
        headers = {'Authorization': 'Bearer '+str(access_token),
	   	           'Accept': 'application/json',
 		           'Accept-Charset': 'utf-8',
 		           'Accept-Encoding': 'gzip-deflate',
 		           'Content-type': 'application/json'}
        params = {'type':type,'period': periode}
        r = requests.get(url = hist_url, headers = headers, params = params)
        data = r.json()
        return data

# ---------------------------------------------------------------------------------------
### Retrieve List active recommendations  ###
# ---------------------------------------------------------------------------------------
    def get_recommendations(self, pool_id, access_token):
        last_url = self._api_url + 'pools/' + str(pool_id) + '/recommendations'
        headers = {'Authorization': 'Bearer '+str(access_token),
            		'Accept': 'application/json',
					'Accept-Charset': 'utf-8',
					'Accept-Encoding': 'gzip-deflate',
					'Content-type': 'application/json'}
        r = requests.get(url = last_url, headers = headers)
        data = r.json()
        return data

class Config:
  __loxberry = {
    "LBSCONFIG": os.getenv("LBSCONFIG", os.getcwd()),
  }

  @staticmethod
  def Loxberry(name):
    return Config.__loxberry[name]
    
class PConfig:
  __plugin = {
    "LBPCONFIG": os.getenv("LBPCONFIG", os.getcwd()),
  }

  @staticmethod
  def plugin(name):
    return PConfig.__plugin[name]    



# ---------------------------------------------------------------------------------------
### parse args and call main function
# ---------------------------------------------------------------------------------------
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))


if __name__ == "__main__":
    # ---------------------------------------------------------------------------------------
    ### Parse commandline arguments
    # ---------------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="Loxberry Ondilo ICO Plugin.")
    
    debugroup = parser.add_argument_group("debug")

    debugroup.add_argument("--debug", 
                        dest="debug",
                        default=False,
                        action="store_true",
                        help="enable debug mode")

    debugroup.add_argument("--debugip", 
                        dest="debugip",
                        default=socket.gethostbyname(socket.gethostname()),
                        action="store",
                        help="Local IP address to listen for debugger connections (default={0})".format(socket.gethostbyname(socket.gethostname())))

    debugroup.add_argument("--debugport", 
                        dest="debugport",
                        default=5678,
                        action="store",
                         help="TCP port to listen for debugger connections (default=5678)")
   
    
    loggroup = parser.add_argument_group("log")

    loggroup.add_argument("--logfile", 
                        dest="logfile",
                        default="ico.log",
                        type=str,
                        action="store",
                        help="specifies logfile path")

    loggroup = parser.add_argument_group("config")

    loggroup.add_argument("--configfile", 
                        dest="configfile",
                        default="ico.cfg",
                        type=str,
                        action="store",
                        help="specifies plugin configuration file path")

    args = parser.parse_args()

    # ---------------------------------------------------------------------------------------
    ### logging configuration
    # ---------------------------------------------------------------------------------------
    logging.getLogger().setLevel(logging.DEBUG)
    logging.basicConfig(filename=args.logfile,
                        filemode='w', 
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',)

    ### define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)
    
    ### add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.info("using plugin log file {0}".format(args.logfile))

    # ---------------------------------------------------------------------------------------
    ### call main function
    # ---------------------------------------------------------------------------------------
   
    try:
        main(args)
    except Exception as e:
        logging.critical(e, exc_info=True)
