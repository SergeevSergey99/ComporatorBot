import json

from telebot.async_telebot import AsyncTeleBot
from datetime import datetime
import googleSheets
from lxml import html
# main variables
import creds.info
TOKEN = creds.info.TELGRAM_TOKEN
bot = AsyncTeleBot(TOKEN)

import asyncio
from pyppeteer import launch


products = {
    'Молоко': [
            {'Название': "Простоквашино отборное пастеризованное 3.4-4.5%, 930мл", 'Магазин': "Перекресток", 'url': "https://www.perekrestok.ru/cat/370/p/moloko-prostokvasino-otbornoe-pasterizovannoe-3-4-4-5-930ml-2085981", 'xpath': "//*[@id=\"app\"]/div/main/div/div[1]/div[3]/div[2]/div[2]/div[3]/div[1]/div[1]/div[1]/div"},
            {'Название': "Простоквашино пастеризованное 2.5%, 930мл", 'Магазин': "Перекресток", 'url': "https://www.perekrestok.ru/cat/370/p/moloko-prostokvasino-pasterizovannoe-2-5-930ml-2093081", 'xpath': "//*[@id=\"app\"]/div/main/div/div[2]/div/div/div/div/div/div/div[1]/div[1]"}
        ]
}


with open('data.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

start_parm = {
    # Начать хромированный путь
    "executablePath": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    # Закройте браузер без заголовка По умолчанию запускается без заголовка
    "headless": False,
}

async def get_Prices() -> str:
    # Launch the browser
    browser = await launch(**start_parm)


    fulstr = "База обновлена вот все обнаруженные цены:\n"
    for currType in products:
        smallstr = "" #"\n" + currType + "\n"
        for i in products[currType]:
            print(i)
            if('price' in i):
                smallstr += "Название: " + i['Название'] + "\nСтоимость: " + i['price'] + "\nМагазин: " + i['Магазин'] + "\n\n"
                continue


            # Open a new browser page
            page = await browser.newPage()
            cdp = await page.target.createCDPSession()

            await cdp.send('Target.createBrowserContext')

            page.setDefaultNavigationTimeout(0)
            # Create a URI for our test file
            page_path = i['url']


            await page.goto(page_path)
            page_content = await page.content()
            tree = html.fromstring(page_content)
            try:

                el = tree.xpath(i['xpath'])

                if len(el) > 0:
                    print(el[0].text)
                    i['price'] = el[0].text
                    smallstr +="Название: " + i['Название'] + "\nСтоимость: " + el[0].text + "\nМагазин: " + i['Магазин'] + "\n\n"
            except Exception:
                print("Не удалось загрузить " + i['Название'])
            await page.close()

        if len(smallstr) > 0:
            fulstr +="\n" + currType + "\n" + smallstr

    # Close browser
    await browser.close()

    with open('data.json', 'w', encoding='utf-8') as fp:
        json.dump(products, fp=fp, ensure_ascii=False, indent=2)

    return fulstr

def get_PricesOfType(type: str) -> str:
    # Launch the browser
    if type in products == False or len(products[type]) == 0:
        return "В базе нет цен на наименования \"" + type + "\". Обновити или дождитесь ее расширения"

    fulstr = "Известные цены на наименования \"" + type + "\" в базе:\n"
    for i in products[type]:
        print(i)
        if('price' in i):
            fulstr += "Название: " + i['Название'] + "\nСтоимость: " + i['price'] + "\nМагазин: " + i['Магазин'] + "\n\n"

    return fulstr



@bot.message_handler(commands=['milk'])
async def milk_handler(message):

    print("milk")
    await bot.send_message(message.chat.id, get_PricesOfType("Молоко"))

@bot.message_handler(commands=['milkShake'])
async def milkShake_handler(message):

    print("milkShake")
    await bot.send_message(message.chat.id, get_PricesOfType("Молочные коктели"))


@bot.message_handler(commands=['start'])
async def start_handler(message):

    await bot.send_message(message.chat.id, "Start")

from datetime import timedelta
@bot.message_handler(commands=['update'])
async def update_base(message):

    print("update")

    await bot.send_message(message.chat.id, "Обновляем базу")
    lists = googleSheets.GetBase()

    data = {}
    for list in lists.worksheets():
        data[list.title] = list.get_all_records()

    print(data)

    global products

    products = data

    with open('data.json', 'w', encoding='utf-8') as fp:
        json.dump(data, fp=fp, ensure_ascii=False, indent=2)

    await bot.send_message(message.chat.id, "Обновляем цены")

    try:
        msg = await get_Prices()
        print("База обновлена")
        await bot.send_message(message.chat.id, "База обновлена")
    except Exception:
        print(Exception)
        await bot.send_message(message.chat.id, "Что то пошло не так")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    print("id: \"" + str(message.from_user.id) + "\"\tusername: \"" + str(message.from_user.username) +
          "\"\tname: \"" + str(message.from_user.first_name) + " " + str(message.from_user.last_name)
          + "\"\ttext: \"" + str(message.text) + "\"\t\tdate: " + datetime.fromtimestamp((message.date)).strftime("%A, %B %d, %Y %I:%M:%S"))


asyncio.run(bot.polling())



