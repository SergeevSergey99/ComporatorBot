import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import creds.info

def get_service_sacc():
    """
    Могу читать и (возможно) писать в таблицы кот. выдан доступ
    для сервисного аккаунта приложения
    sacc-1@privet-yotube-azzrael-code.iam.gserviceaccount.com
    :return:
    """
    creds_json = os.path.dirname(__file__) + "/creds/sacc1.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes)
    client = gspread.authorize(creds)
    return client
    #creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    #return build('sheets', 'v4', http=creds_service)

def GetBase():


    #service = get_service_sacc()
    gc = get_service_sacc()
    #sheet = service.spreadsheets()
    sheet_id = creds.info.SHEET_ID

    # получаем таблицу
    sh = gc.open_by_key(sheet_id)
    # получаем листы
    return sh
    #sheet = sh.sheet1
    #return sheet.acell('A1').value


