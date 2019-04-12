from selenium import webdriver
import asyncio
import websockets
import json


class Miner(object):
    def __init__(self, link):
        self.driver = webdriver.PhantomJS(r"phantomjs.exe")
        self.socket_link = link
        self.bought_times = 1
        self.code = None
        self.money = 0
        self.items = None
        self.speed = None
        self.buying_state = False
        self.to_buy = str()

    def prepare_response(self, data):
        to_run = data["pow"]
        id_send = data["randomId"]
        pow_send = self.driver.execute_script("return " + to_run)
        command = f"C1 {id_send} {pow_send}"
        return command, id_send

    async def mining(self):
        async with websockets.connect(self.socket_link) as websocket:
            await websocket.send("")

            message = await websocket.recv()
            print(message)
            data = json.loads(message)
            self.money = data.get("score")
            self.items = data.get("items")
            self.speed = data.get("tick")

            command, id_send = self.prepare_response(data)
            await asyncio.sleep(2)
            await websocket.send(command)
#
            while True:
                command = f"C1 {id_send} 1"

                await websocket.send(command)
                print(f"Sent {command}")

                message = await websocket.recv()
                print(message)
                # print(message)
                place, money, id_send = map(int, message.split()[1:4])
                print(f"Баланс: {money/1000:.3f}")
                self.money = money

                if self.buying_state:
                    command = f"P{self.bought_times} B {self.to_buy}"
                    await websocket.send(command)
                    self.buying_state = False
                    self.to_buy = str()
                    await websocket.recv()

                await asyncio.sleep(2)

    def buy(self, name):
        self.buying_state = True
        self.to_buy = name

