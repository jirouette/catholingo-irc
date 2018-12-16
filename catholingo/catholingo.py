#!/usr/bin/python3
# coding: utf8

import websockets
import asyncio
import json
import enum
import os
import uuid
from typing import Any


class Protocol(enum.Enum):
    AUTH = "AUTH"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    RPC = "RPC"
    RPC_RESPONSE = "RPC_RESPONSE"
    MESSAGE = "MESSAGE"

    @classmethod
    def has(cls, value):
        return value in cls.__members__


class ProtocolError(Exception):
    pass


class Server(object):
    port = 8080
    host = "localhost"
    peers = set()

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.run_forever = websockets.serve(self.process, self.host, self.port)

    async def process(self, websocket, path) -> None:
        peer = Peer(self, websocket, path)
        self.peers.add(peer)
        try:
            await peer.run()
        finally:
            self.peers.remove(peer)


class Peer(object):
    websocket = None
    path = ""
    app = ""
    namespace = ""
    protocol = ""
    authenticated = False

    def __init__(self, server: Server, websocket, path):
        self.websocket = websocket
        self.path = path
        self.server = server

    async def send(self, action: Protocol, data: dict, ID=None):
        ID = ID or str(uuid.uuid4())
        message = dict(ID=ID, action=action, data=data)
        return await self.websocket.send(json.dumps(message))

    async def send_error(self, message: str, from_ID=None):
        data = dict(message=message, from_ID=from_ID)
        return await self.send(Protocol.ERROR, data)

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
                await self.handle_message(ID, action, data)
            except ProtocolError as e:
                await self.send_error(e.message, ID)
            except Exception as e:
                await self.send_error(
                    f"Internal error while receiving message {message}",
                    ID)

    async def handle_message(self, ID: Any, action: str, data: Any) -> None:
        if not self.authenticated and action != Protocol.AUTH:
            raise ProtocolError("Must be authenticated first")
        elif not Protocol.has(action):
            raise ProtocolError(f"Unknown action '{action}'")
        await self[action.lower()](ID, **data)

    async def auth(
        self,
        ID: Any,
        app: str,
        namespace: str,
        protocol: str
    ) -> None:
        self.app = app
        self.namespace = namespace
        self.protocol = protocol
        self.authenticated = True
        await self.send(Protocol.SUCCESS, ID)

    async def error(self, ID: Any, message: str, from_ID: Any = None) -> None:
        pass

    async def success(self, ID: Any, ackedID: Any) -> None:
        pass

    async def rpc(self, ID: Any, method: str, args: list, kwargs: dict) -> None:
        try:
            ret = await self.server[method](*args, **kwargs)
            await self.send(Protocol.RPC_RESPONSE, dict(data=ret))
        except:
            await self.send_error("Failed to RPC "+method, ID)

    async def rpc_response(self, ID: Any, data: Any) -> None:
        pass

    async def message(self,
                      ID: Any,
                      channel: str,
                      user: str,
                      message: str,
                      is_trusted: bool) -> None:
        data = dict(
            app=self.app,
            namespace=self.namespace,
            channel=channel,
            user=user,
            message=message,
            is_trusted=is_trusted)
        self.send_all(Protocol.MESSAGE, data)


if __name__ == '__main__':
    app = Server(
        host=os.environ.get('HOST', 'localhost'),
        port=int(os.environ.get('PORT', 10030))
    )
    asyncio.get_event_loop().run_until_complete(app.run_forever)
    asyncio.get_event_loop().run_forever()
