# See: http://developer.valvesoftware.com/wiki/Server_Queries
#

import logging
import socket
import time

from .buffer import SteamPacketBuffer
from .server import Server
from .packet import *

PACKET_SIZE = 1400
SINGLE_PACKET_RESPONSE = -1
MULTIPLE_PACKET_RESPONSE = -2

#Debug Logging to file
# logger = logging.getLogger('Beispiel_Log')
# logger.setLevel(logging.DEBUG)
# fh = logging.FileHandler('query/debug.log')
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)


class SourceWatchError(Exception):
    pass


class Query:
    global PACKET_SIZE
    def __init__(self, host, port=27015, timeout=2):
        self.logger = logging.getLogger('SourceWatch')
        self.server = Server(socket.gethostbyname(host), int(port))
        self._timeout = timeout
        self._connect()

    def __del__(self):
        self._connection.close()

    def _connect(self):
        self.logger.info('Connecting to %s', self.server)
        self._connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._connection.settimeout(self._timeout)
        self._connection.connect(self.server.as_tuple())

    def _receive(self, packet_buffer={}):
        response = self._connection.recv(PACKET_SIZE)
        self.logger.debug('Received: %s', response)
        packet = SteamPacketBuffer(response)
        response_type = packet.read_long()

        if response_type == SINGLE_PACKET_RESPONSE:
            self.logger.debug('Single packet response')
            return packet

        elif response_type == MULTIPLE_PACKET_RESPONSE:
            self.logger.debug('Multiple packet response')
            request_id = packet.read_long()  

            if request_id not in packet_buffer:
                packet_buffer.setdefault(request_id, [])

            total_packets = packet.read_byte()
            current_packet_number = packet.read_byte()
            packet.size = packet.read_short()
            packet_buffer[request_id].insert(current_packet_number, packet.read())

            if current_packet_number == total_packets - 1:
                full_packet = SteamPacketBuffer(b''.join(packet_buffer[request_id]))

                if full_packet.read_long() == PAKET_HEADER:
                    return full_packet
            else:
                return self._receive(packet_buffer)
        else:
            self.logger.error('Received invalid response type: %s', response_type)
            raise SourceWatchError('Received invalid response type')

    def _get_challenge(self):
        response = self._send(ChallengeRequest())

        response.is_valid()
        return response.raw

    def _send(self, Paket):
        if isinstance(Paket, Challengeable):
            challenge = self._get_challenge()
            self.logger.debug('Using challenge: %s', challenge)
            Paket.challenge = challenge

        timer_start = time.time()
        self.logger.debug('Paket: %s', Paket.as_bytes())
        self._connection.send(Paket.as_bytes())
        result = self._receive()
        ping = round((time.time() - timer_start) * 1000, 2)
        response = create_response(Paket.class_name(), result, ping)
        #
        # #Debug
        #print(response)
        #
        #
        if not response.is_valid():
            raise SourceWatchError('Response packet is invalid.')

        return response

    def request(request):
        def wrapper(self):
            response = request(self)
            result = response.result()
            result['server'] = {
                'ip': self.server.ip,
                'port': self.server.port,
                'ping': response.ping
            }
            return result
        return wrapper

    def ping(self):
        """Fake ping request. Send three InfoRequets and calculate an average ping."""
        self.logger.info('Sending fake ping request')
        MAX_LOOPS = 3
        return round(sum(map(lambda ping: self.info().get('server').get('ping'),
                             range(MAX_LOOPS))) / MAX_LOOPS, 2)

    @request
    def info(self):
        """Request basic server information."""
        self.logger.info('Sending info request')
        return self._send(InfoRequest())

    @request
    def players(self):
        """Request players."""
        self.logger.info('Sending players request')
        return self._send(PlayersRequest())

    @request
    def rules(self):
        """Request server rules."""
        self.logger.info('Sending rules request')
        return self._send(RulesRequest())