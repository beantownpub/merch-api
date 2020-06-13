import asyncio
import time
import json


def fuck():
    print('reg sleep')
    time.sleep(10)
    print('Fuck You')


async def suck():
    print('sync sleep')
    await asyncio.sleep(10)
    print('Suck You')


async def get_products():
    fuck()
    await suck()
    with open('./api/products.json') as f:
        print('im an idiot')
        products = json.load(f)
    return products


async def main():
    await asyncio.sleep(2)
    print(await get_products())


asyncio.run(main())
