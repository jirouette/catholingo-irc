#!/usr/bin/python3
# coding: utf8

import websockets
import asyncio
import json
import enum
import os
import uuid
from typing import Any


class Protocol(enum.EnumMeta):
    AUTH = "AUTH"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    RPC = "RPC"
    RPC_RESPONSE = "RPC_RESPONSE"
    MESSAGE = "MESSAGE"
    PING = "PING"

    @classmethod
    def has(cls, value):
        return value in cls.__members__


class ProtocolError(Exception):
    pass


class Server(object):
    port = 8080
    host = "localhost"
    peers = set()
    peers_by_location = dict()

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.run_forever = websockets.serve(self.process, self.host, self.port)

    async def process(self, websocket, path) -> None:
        print("Hello peer!")
        peer = Peer(self, websocket, path)
        self.peers.add(peer)
        try:
            await peer.run()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.peers.remove(peer)
            if peer.authenticated:
                self.peers_by_location.pop(
                    (peer.protocol, peer.location), None)


class Peer(object):
    websocket = None
    "WebSocket client instance"
    path = ""
    "WebSocket client path"

    app = ""
    "Peer app name (e.g. 'catholingo-irc', 'catholingo-speech')"
    namespace = ""
    "Peer namespace (e.g. 'com.jirouette.catholingo', 'com.jirouette.tools')"
    version = ""
    "Peer app version (e.g. '2.0.1')"
    location = ""
    "Peer dynamic location (e.g. 'chat.freenode.net', 'discord/serverX')"
    protocol = ""
    "Peer handled protocol if the app is a bridge (e.g. None, 'irc', 'discord')"
    authenticated = False

    def __init__(self, server: Server, websocket, path):
        self.websocket = websocket
        self.path = path
        self.server = server

    async def send(self, action: Protocol, data: dict = None, ID: str = None, From: str = None):
        ID = ID or str(uuid.uuid4())
        data = data or dict()
        message = dict(ID=ID, From=From, action=action, data=data)
        return await self.websocket.send(json.dumps(message))

    async def send_error(self, message: str, From=None):
        data = dict(message=message)
        return await self.send(Protocol.ERROR, data, From=From)

    async def send_all(self, action: Protocol, data: dict, ID=None):
        for peer in self.server.peers:
            try:
                await peer.send(action, data, ID)
            except:
                pass

    async def run(self) -> None:
        async for message in self.websocket:
            ID = None
            try:
                message = json.loads(message)
                if not (type(message) is dict):
                    raise ProtocolError("Received wrong format message")
                action = message.get('action')
                data = message.get('data', dict())
                ID = message.get("ID")
                if not (type(data) is dict):
                    raise ProtocolError("Received wrong format data")
                if not ID:
                    raise ProtocolError("Received empty ID (tips: use UUIDv4)")
                if not action:
                    raise ProtocolError("Received empty action")
                await self.handle_message(ID, action, data)
            except ProtocolError as e:
                await self.send_error(str(e), ID)
            except json.decoder.JSONDecodeError as e:
                await self.send_error(f"Received wrong format data : {e}", ID)
            except Exception as e:
                print(type(e))
                print(e)
                await self.send_error(
                    f"Internal error while receiving message {message}",
                    ID)

    async def handle_message(self, ID: Any, action: str, data: Any) -> None:
        if not self.authenticated and action != Protocol.AUTH:
            raise ProtocolError("Must be authenticated first")
        # elif not Protocol.has(action):
        #    raise ProtocolError(f"Unknown action '{action}'")
        await getattr(self, action.lower())(ID, **data)

    async def auth(
        self,
        ID: Any,
        app: str,
        namespace: str,
        version: str,
        location: str,
        protocol: str
    ) -> None:
        if self.authenticated:
            raise ProtocolError(f"Already authenticated as {namespace}:{app} ({version})")
        if (protocol, location) in self.server.peers_by_location.keys():
            raise ProtocolError(f"Location {location} of protocol {protocol} already in use")
        self.server.peers_by_location[protocol, location] = self
        self.app = app
        self.namespace = namespace
        self.version = version
        self.location = location
        self.protocol = protocol
        self.authenticated = True
        await self.send(Protocol.SUCCESS, From=ID)

    async def error(self, ID: Any, message: str, from_ID: Any = None) -> None:
        pass

    async def success(self, ID: Any, ackedID: Any) -> None:
        pass

    async def rpc(self, ID: Any, target: str, method: str, args: list = None, kwargs: dict = None) -> None:
        args = args or list()
        kwargs = kwargs or dict()
        try:
            if not target:
                peer_target = self.server
            else:
                for peer in self.server.peers:
                    if peer.ID == target:
                        peer_target = peer.ID
                        break
                else:
                    raise ProtocolError(f"Unknown target {target}")
            ret = await getattr(target, method)(*args, **kwargs)
            await self.send(Protocol.RPC_RESPONSE, dict(data=ret), From=ID)
        except:
            await self.send_error("Failed to RPC "+method, ID)

    async def rpc_response(self, ID: Any, data: Any) -> None:
        pass

    async def ping(self, ID: Any) -> None:
        await self.send(Protocol.SUCCESS, From=ID)

    async def message(self,
                      ID: Any,
                      channel: str,
                      user: str,
                      message: str,
                      is_trusted: bool) -> None:
        data = dict(
            app=self.app,
            namespace=self.namespace,
            location=self.location,
            channel=channel,
            user=user,
            message=message,
            is_trusted=is_trusted)
        self.send_all(Protocol.MESSAGE, data)


if __name__ == '__main__':
    app = Server(
        host=os.environ.get('HOST', 'localhost'),
        port=int(os.environ.get('PORT', 8080))
    )
    print("Running")
    asyncio.get_event_loop().run_until_complete(app.run_forever)
    asyncio.get_event_loop().run_forever()
