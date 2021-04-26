import importlib
import io
import struct

from .buffer import SteamPacketBuffer


def create_response(request_class_name, *args):
    """Create a ResponsePaket instance from a RequestPaket class name."""
    name = request_class_name[:-len('Request')]
    ResponsePaket = globals()['{}Response'.format(name)]
    return ResponsePaket(*args)


class Challengeable:
    """Flag a Paket to request a challenge."""
    pass


class BasePaket:
    def __init__(self):
        self._buffer = SteamPacketBuffer()
        self._header = None

    def __repr__(self):
        return '<{}> buffer:{}'.format(self.class_name(), self._buffer.getvalue())

    def class_name(self):
        return self.__class__.__name__


class RequestPaket(BasePaket):
    PAKET_HEADER = -1

    def __init__(self):
        super(RequestPaket, self).__init__()
        self._buffer.write_long(self.PAKET_HEADER)
        self._buffer.write_byte(self.REQUEST_HEADER)

    def as_bytes(self):
        return self._buffer.getvalue()

    @property
    def challenge(self):
        return self._challenge

    @challenge.setter
    def challenge(self, value):
        self._buffer.write_long(value)


class ResponsePaket(BasePaket):
    def __init__(self, buffer, ping):
        super(ResponsePaket, self).__init__()
        self._buffer = buffer
        self._ping = ping
        self._result = None

    def is_valid(self):
        return self.header == self.RESPONSE_HEADER

    @property
    def header(self):
        if self._header is None:
            self._header = self._buffer.read_byte()
        return self._header

    @property
    def ping(self):
        return self._ping

    def result(self):
        """Change stream position back to the beginning."""
        self._buffer.seek(0)
        return self._result


class InfoRequest(RequestPaket):
    REQUEST_HEADER = 0x54
    REQUEST_PAYLOAD = 'Source Engine Query'

    def __init__(self):
        super(InfoRequest, self).__init__()
        self._buffer.write_string(self.REQUEST_PAYLOAD)


class InfoResponse(ResponsePaket):
    RESPONSE_HEADER = 0x49

    def result(self):
        info = {
            'server_protocol_version': self._buffer.read_byte(),
            'server_name': self._buffer.read_string(),
            'game_map': self._buffer.read_string(),
            'game_directory': self._buffer.read_string(),
            'game_description': self._buffer.read_string(),
            'game_app_id': self._buffer.read_short(),
            'players_current':  self._buffer.read_byte(),
            'players_max': self._buffer.read_byte(),
            'players_bot': self._buffer.read_byte(),
            'server_type': chr(self._buffer.read_byte()),
            'server_os': chr(self._buffer.read_byte()),
            'server_password_protected': self._buffer.read_byte(),
            'server_vac_secured': self._buffer.read_byte(),
            'game_version': self._buffer.read_string()
        }

        try:
            extra_data_flags = self._buffer.read_byte()
        except:
            logger.debug('No extra data flags set.')
        else:
            if extra_data_flags & 0x80:
                info['server_port'] = self._buffer.read_short()
            if extra_data_flags & 0x10:
                info['server_steam_id'] = self._buffer.read_long_long()
            if extra_data_flags & 0x40:
                info['server_spectator_port'] = self._buffer.read_short()
                info['server_spectator_name'] = self._buffer.read_string()
            if extra_data_flags & 0x20:
                info['server_tags'] = self._buffer.read_string()
            if extra_data_flags & 0x01:
                """A more accurate AppID as the earlier appID could have benn truncated as it was forced into 16-bit storage"""
                info['game_app_id'] = self._buffer.read_long_long()
        finally:
            info['players_human'] = info['players_current'] - info['players_bot']

        return {'info': info}


class ChallengeRequest(RequestPaket):
    REQUEST_HEADER = 0x56
    REQUEST_CHALLANGE = -1

    def __init__(self):
        super(ChallengeRequest, self).__init__()
        self.challenge = self.REQUEST_CHALLANGE


class ChallengeResponse(ResponsePaket):
    RESPONSE_HEADER = 0x41

    @property
    def raw(self):
        return self._buffer.read_long()


class RulesRequest(RequestPaket, Challengeable):
    REQUEST_HEADER = 0x56


class RulesResponse(ResponsePaket):
    RESPONSE_HEADER = 0x45

    def result(self):
        rules = {}
        total_rules = self._buffer.read_short()
        for _ in range(total_rules):
            key = self._buffer.read_string()
            value = self._buffer.read_string()
            rules.setdefault(key, value)
        return {'rules': rules}


class PlayersRequest(RequestPaket, Challengeable):
    REQUEST_HEADER = 0x55


class PlayersResponse(ResponsePaket):
    RESPONSE_HEADER = 0x44

    def result(self):
        total_players = self._buffer.read_byte()
        players = []
        for _ in range(total_players):
            player = {
                'id': self._buffer.read_byte(),
                'name': self._buffer.read_string(),
                'kills': self._buffer.read_long(),
                'play_time': self._buffer.read_float()
            }
            players.append(player)
        return {'players': players}
