# Work: getInfo(), getPlayers(), getChallenge(), getRules(), getPing()
# Support: Source Servers, GoldSrc servers, The Ship Servers
# Based on Dasister's Source-Query-Class that had a couple of tiny bugs in it
# Corrected by Madman in 2020

import socket
import struct
import sys
import time


A2S_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
A2S_PLAYERS = b'\xFF\xFF\xFF\xFF\x55'
A2S_RULES = b'\xFF\xFF\xFF\xFF\x56'

S2A_INFO_SOURCE = chr(0x49)
S2A_INFO_GOLDSRC = chr(0x6D)

class SourceQuery(object):
    is_third = False
    __sock = None
    __challenge = None


    def __init__(self, addr, port=27216, timeout=0.6):
        self.ip, self.port, self.timeout = socket.gethostbyname(addr), port, timeout
        if sys.version_info >= (3, 0):
            self.is_third = True

    def disconnect(self):
        """ Close socket """
        if self.__sock is not None:
            self.__sock.close()
            self.__sock = False

    def connect(self):
        """ Opens a new socket """
        self.disconnect()
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__sock.settimeout(self.timeout)
        self.__sock.connect((self.ip, self.port))

    def get_ping(self):
        """ Get ping to server """
        return self.get_info()['Ping']

    def get_info(self):
        """ Retrieves information about the server including, but not limited to: its name, the map currently being played, and the number of players. """
        if self.__sock is None:
            self.connect()
        self.__sock.send(A2S_INFO)
        before = time.time()
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        after = time.time()
        data = data[4:]

        result = {}

        header, data = self.__get_byte(data)
        result['Ping'] = int((after - before) * 1000)
        if chr(header) == S2A_INFO_SOURCE:
            result['Protocol'], data = self.__get_byte(data)
            result['Hostname'], data = self.__get_string(data)
            result['Map'], data = self.__get_string(data)
            result['GameDir'], data = self.__get_string(data)
            result['GameDesc'], data = self.__get_string(data)
            result['AppID'], data = self.__get_short(data)
            result['Players'], data = self.__get_byte(data)
            result['MaxPlayers'], data = self.__get_byte(data)
            result['Bots'], data = self.__get_byte(data)
            dedicated, data = self.__get_byte(data)
            if chr(dedicated) == 'd':
                result['Dedicated'] = 'Dedicated'
            elif dedicated == 'l':
                result['Dedicated'] = 'Listen'
            else:
                result['Dedicated'] = 'SourceTV'

            os, data = self.__get_byte(data)
            if chr(os) == 'w':
                result['OS'] = 'Windows'
            elif chr(os) in ('m', 'o'):
                result['OS'] = 'Mac'
            else:
                result['OS'] = 'Linux'
            result['Password'], data = self.__get_byte(data)
            result['Secure'], data = self.__get_byte(data)
            if result['AppID'] == 2400:  # The Ship server
                result['GameMode'], data = self.__get_byte(data)
                result['WitnessCount'], data = self.__get_byte(data)
                result['WitnessTime'], data = self.__get_byte(data)
            result['Version'], data = self.__get_string(data)
            edf, data = self.__get_byte(data)
            try:
                if edf & 0x80:
                    result['GamePort'], data = self.__get_short(data)
                if edf & 0x10:
                    result['SteamID'], data = self.__get_long_long(data)
                if edf & 0x40:
                    result['SpecPort'], data = self.__get_short(data)
                    result['SpecName'], data = self.__get_string(data)
                if edf & 0x10:
                    result['Tags'], data = self.__get_string(data)
            except:
                pass
        elif chr(header) == S2A_INFO_GOLDSRC:
            result['GameIP'], data = self.__get_string(data)
            result['Hostname'], data = self.__get_string(data)
            result['Map'], data = self.__get_string(data)
            result['GameDir'], data = self.__get_string(data)
            result['GameDesc'], data = self.__get_string(data)
            result['Players'], data = self.__get_byte(data)
            result['MaxPlayers'], data = self.__get_byte(data)
            result['Version'], data = self.__get_byte(data)
            dedicated, data = self.__get_byte(data)
            if chr(dedicated) == 'd':
                result['Dedicated'] = 'Dedicated'
            elif dedicated == 'l':
                result['Dedicated'] = 'Listen'
            else:
                result['Dedicated'] = 'HLTV'
            os, data = self.__get_byte(data)
            if chr(os) == 'w':
                result['OS'] = 'Windows'
            else:
                result['OS'] = 'Linux'
            result['Password'], data = self.__get_byte(data)
            result['IsMod'], data = self.__get_byte(data)
            if result['IsMod']:
                result['URLInfo'], data = self.__get_string(data)
                result['URLDownload'], data = self.__get_string(data)
                data = self.__get_byte(data)[1]  # NULL-Byte
                result['ModVersion'], data = self.__get_long(data)
                result['ModSize'], data = self.__get_long(data)
                result['ServerOnly'], data = self.__get_byte(data)
                result['ClientDLL'], data = self.__get_byte(data)
            result['Secure'], data = self.__get_byte(data)
            result['Bots'], data = self.__get_byte(data)

        return result

    # <------------------getInfo() End -------------------------->

    def get_challenge(self):
        """ Get challenge number for A2S_PLAYER and A2S_RULES queries. """
        if self.__sock is None:
            self.connect()
        self.__sock.send(A2S_PLAYERS + b'0xFFFFFFFF')
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        self.__challenge = data[5:]

        return True

    # <-------------------getChallenge() End --------------------->

    def get_players(self):
        """ Retrieve information about the players currently on the server. """
        if self.__sock is None:
            self.connect()
        if self.__challenge is None:
            self.get_challenge()

        if self.__challenge:
            try:
                self.__sock.send(A2S_PLAYERS + self.__challenge)
            except:
                return False    
        try:
            data = self.__sock.recv(4096)
        except:
            return False

        data = data[4:]

        header, data = self.__get_byte(data)
        num, data = self.__get_byte(data)
        result = []
        try:
            for i in range(num):
                player = {}
                data = self.__get_byte(data)[1]
                player['id'] = i + 1  # ID of All players is 0
                player['Name'], data = self.__get_string(data)
                player['Frags'], data = self.__get_long(data)
                player['Time'], data = self.__get_float(data)
                ftime = time.gmtime(int(player['Time']))
                player['FTime'] = ftime
                player['PrettyTime'] = time.strftime('%H:%M:%S', ftime)
                result.append(player)

        except Exception:
            pass

        return result

    # <-------------------getPlayers() End ----------------------->

    def get_rules(self):
        """ Returns the server rules, or configuration variables in name/value pairs. """
        if self.__sock is None:
            self.connect()
        if self.__challenge is None:
            self.get_challenge()

        self.__sock.send(A2S_RULES + self.__challenge)
        try:
            data = self.__sock.recv(4096)
            if data[0] == '\xFE':
                num_packets = ord(data[8]) & 15
                packets = [' ' for i in range(num_packets)]
                for i in range(num_packets):
                    if i != 0:
                        data = self.__sock.recv(4096)
                    index = ord(data[8]) >> 4
                    packets[index] = data[9:]
                data = ''
                for i, packet in enumerate(packets):
                    data += packet
        except:
            return False
        data = data[4:]

        header, data = self.__get_byte(data)
        num, data = self.__get_short(data)
        result = {}

        # Server sends incomplete packets. Ignore "NumPackets" value.
        while 1:
            try:
                rule_name, data = self.__get_string(data)
                rule_value, data = self.__get_string(data)
                if rule_value:
                    result[rule_name] = rule_value
            except:
                break

        return result

    # <-------------------getRules() End ------------------------->

    def __get_byte(self, data):
        if self.is_third:
            return data[0], data[1:]
        else:
            return ord(data[0]), data[1:]

    def __get_short(self, data):
        return struct.unpack('<h', data[0:2])[0], data[2:]

    def __get_long(self, data):
        return struct.unpack('<l', data[0:4])[0], data[4:]

    def __get_long_long(self, data):
        return struct.unpack('<Q', data[0:8])[0], data[8:]

    def __get_float(self, data):
        return struct.unpack('<f', data[0:4])[0], data[4:]

    def __get_string(self, data):
        s = ""
        i = 0
        if not self.is_third:
            while data[i] != '\x00':
                s += data[i]
                i += 1
        else:
            while chr(data[i]) != '\x00':
                s += chr(data[i])
                i += 1
        return s, data[i + 1:]


#Just for testing - uncomment the blow lines for testing with my test server

if __name__ == '__main__':
    try:
        query = SourceQuery('93.186.198.185', 27216) # Test Server you can use as long as it lives
        res = query.get_info()
        print(res['Hostname'])
        print(res['Map'])
        print(res['GameDir'])
        print("%i/%i" % (res['Players'], res['MaxPlayers']))
        print(res['AppID'])
        print(res['Tags'])
        print(res['Ping'])

        players = query.get_players()

        for player in players:
            print("{id:<2} {Name:<35} {Frags:<5} {PrettyTime} {NetID}".format(**player))

        rules = query.get_rules()

        print
        "\n{0:d} Rules".format(len(rules))
        print
        "------------------------------------"
        for rule_name, value in rules.items():
            print("{0:<5} {1}".format(rule_name, value))
        query.disconnect()
        query = False
    except Exception:
        print("Error while executing!")