#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import pymysql
import json
import pandas as pd
import time
from datetime import date
from fake_useragent import UserAgent

db_settings = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "db": "ncu_database",
    "charset": "utf8"
}


# In[2]:


try:  
    today = date.today()
    user_agent = UserAgent()
    conn = pymysql.connect(**db_settings)
    with conn.cursor() as cursor:
        insert_command = "INSERT INTO stock_data(c, d, v, z, o, h, l, tz, u, tv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        command = "SELECT * FROM etf_list"
        cursor.execute(command)
        conn.commit()
        result = cursor.fetchall()
        for r in result:
            try:
                stock = r[0]
                date = today.strftime("%Y%m%d")
                address = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock}"
                response = requests.get(url=address, headers={ 'user-agent': user_agent.random })
                data = response.text  # 這是json格式的資料
                a_json = json.loads(data)  # 轉成dict
                todat_date = "{}/{}/{}".format(today.year - 1911, f"{today.month:02d}", f"{today.day:02d}")
                for data in a_json["data"]:
                    if(data[0] == todat_date):
                        data[1] = data[1].replace(",", "")
                        data[2] = data[2].replace(",", "")
                        data[3] = data[3].replace(",", "")
                        data[4] = data[4].replace(",", "")
                        data[5] = data[5].replace(",", "")
                        data[6] = data[6].replace(",", "")
                        data[7] = data[7].replace(",", "")
                        data[8] = data[8].replace(",", "")
                        cursor.execute(insert_command, (r[0], data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
                        conn.commit()
                        break;
                time.sleep(10)
                print(time.strftime("%H:%M:%S", time.localtime()) + " " + address)
            except Exception as ex:
                time.sleep(10)
                print(time.strftime("%H:%M:%S", time.localtime()) + " error " + address + " " + data)
                continue
except Exception as e:
#    print(e)
    error_class = e.__class__.__name__ #取得錯誤類型
    detail = e.args[0] #取得詳細內容
    cl, exc, tb = sys.exc_info() #取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
    fileName = lastCallStack[0] #取得發生的檔案名稱
    lineNum = lastCallStack[1] #取得發生的行號
    funcName = lastCallStack[2] #取得發生的函數名稱
    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
    print(errMsg)

