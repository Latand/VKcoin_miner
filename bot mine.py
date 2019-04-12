from collections import defaultdict
from autobot import Miner
import asyncio
from config import users

link = users[int(input("Выбери юзера (1,2,3)"))]


class User:
    coins_init = {
        "cursor": {
            "speed": 0.001,
            "price": 0.03
        },
        "cpu": {
            "speed": 0.003,
            "price": 0.1
        },
        "cpu_stack": {
            "speed": 0.01,
            "price": 1
        },
        "computer": {
            "speed": 0.03,
            "price": 10
        },
        "server_vk": {
            "speed": 0.1,
            "price": 50
        },
        "quantum_pc": {
            "speed": 0.5,
            "price": 200
        },
        "datacenter": {
            "speed": 1,
            "price": 5000
        },
    }

    items = defaultdict(int)
    for i in coins_init.keys():
        items[i] = 0

    def __init__(self, miner):
        self.miner = miner
        self.speed = 0
        self.buying_state = True
        self.MAX_PAYBACK_HOURS = 200
        # self.MAX_PAYBACK_HOURS = int(input(
        #     "Введите максимальный срок окупаемости ускорений в часах (рекоммендуется до 120 часов)\n"))

    def coins(self):
        if not self.miner.items:
            return
        self.items = {item: self.miner.items.count(item) for item, value in self.items.items()}
        self.coins_init = {item: {"speed": value["speed"],
                                  "price": pow(1.3, self.items[item]) * value["price"]}
                           for item, value in self.coins_init.items()}
        return True

    @property
    def money(self):
        return self.miner.money / 1000

    def update_speed(self):
        self.speed = self.miner.speed / 1000

    async def update_coins(self):
        while not self.coins():
            self.coins()
            await asyncio.sleep(1)

    async def choose_coin(self):
        await asyncio.sleep(1)
        if self.buying_state and not self.miner.buying_state:
            for_choice = [(value["price"] / value["speed"], name, value["price"], value["speed"]) for name, value in
                          self.coins_init.items()]
            bargain = min(for_choice, key=lambda x: x[0])
            # print(bargain)
            if bargain:
                relative, name, price, speed = bargain
                print(f"Собираемся купить {name} за {price}")
                profitability = relative / 3600
                if self.money < price:
                    sleep_for = (price - self.money) / self.speed
                    print(f"Денег не хватает, ждем {sleep_for} сек")
                    await asyncio.sleep(sleep_for + 1)

                print("Денег хватает")
                if profitability > self.MAX_PAYBACK_HOURS:
                    print("Максимальная окупаемость превышена, покупка отменена, далее просто майнинг")
                    self.buying_state = False
                else:
                    await self.pay(*bargain)
                    return

        print(f"Баланс: {self.money:.3f}")

    async def pay(self, _, name, price, speed):
        self.miner.buy(name)
        while self.miner.buying_state:
            await asyncio.sleep(1)

        self.items[name] += 1
        print(f"Баланс: {self.money}")
        self.coins_init[name]["price"] *= 1.3
        self.speed += self.coins_init[name]["speed"]
        print(f"Купили {name} за {price:.3f}")
        print(f"Новая скорость {self.speed}")


miner = Miner(link=link)
loop = asyncio.get_event_loop()


async def running():
    u = User(miner=miner)
    await u.update_coins()
    u.update_speed()

    while True:
        await u.choose_coin()
        await asyncio.sleep(2)


async def main():
    a = asyncio.create_task(miner.mining())
    b = asyncio.create_task(running())

    await asyncio.gather(a, b)


loop.run_until_complete(main())

