import json

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from datetime import datetime
import googleSheets
from lxml import html
# main variables
import creds.info
TOKEN = creds.info.TELGRAM_TOKEN
bot = AsyncTeleBot(TOKEN)
import time
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
    "userDataDir": r"C:\Users\Сергей\AppData\Local\Google\Chrome\User Data",
    # Закройте браузер без заголовка По умолчанию запускается без заголовка
    "headless": False,
    #"devtools ": True
}
def tryXPath(page, tree, path):
    try:
        el = tree.xpath(path)
    except Exception:
        time.sleep(3)
        try:
            page_content = await page.content()
            tree = html.fromstring(page_content)
            el = tree.xpath('xpath')

        except Exception:
            print("Не удалось загрузить " + path)
            return []
    return el

async def get_Prices() -> str:
    # Launch the browser
    browser = await launch(**start_parm)

    """
    await browser._connection.send('Browser.setPermission', {
        'permission': 'geolocation',
        'setting': 'granted'
    })"""

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

            page.setDefaultNavigationTimeout(0)
            # Create a URI for our test file
            page_path = i['url']

            await page.goto(page_path)
            page_content = await page.content()
            tree = html.fromstring(page_content)

            el = tryXPath(page, tree, i['xpath'])
            if len(el) == 0:
                el = tryXPath(page, tree, i['xpath2'])
            if len(el) == 0:
                el = tryXPath(page, tree, i['xpath3'])

            if len(el) > 0:
                print(type(el[0]))
                try:
                    print(el[0].text)
                    i['price'] = el[0].text
                except Exception:
                    print(el[0])
                    i['price'] = el[0]

                smallstr +="Название: " + i['Название'] + "\nСтоимость: " + i['price'] + "\nМагазин: " + i['Магазин'] + "\n\n"

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


@bot.message_handler(commands=['help'])
async def milkShake_handler(message):

    print("help")

    tmpstr = ""
    if str(message.from_user.id) == "131856094":
        tmpstr = "/update - обновление базы данных\n"
    await bot.send_message(message.chat.id, tmpstr + "/milk - информация о молоке коктелях\n"
                                            "/milkShake - информация о молочных коктелях\n")


@bot.message_handler(commands=['start'])
async def start_handler(message):

    await bot.send_message(message.chat.id, "Start\nИспользуйте /help")

from datetime import timedelta
@bot.message_handler(commands=['update'])
async def update_base(message):

    print("update")
    if str(message.from_user.id) != "131856094":
        return
    print("admin update")

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
async def text_handler(message):
    print("id: \"" + str(message.from_user.id) + "\"\tusername: \"" + str(message.from_user.username) +
          "\"\tname: \"" + str(message.from_user.first_name) + " " + str(message.from_user.last_name)
          + "\"\ttext: \"" + str(message.text) + "\"\t\tdate: " + datetime.fromtimestamp((message.date)).strftime("%A, %B %d, %Y %I:%M:%S"))

asyncio.run(bot.polling())



