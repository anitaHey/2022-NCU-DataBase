#!/usr/bin/env python
# coding: utf-8

# In[13]:


import requests
import pymssql
import json
import pandas as pd
import time
from fake_useragent import UserAgent
from datetime import datetime

db_settings = {
    "host": "127.0.0.1",
    "user": "sa",
    "password": "zxc123",
    "database": "ncu_database",
    "charset": "utf8"
}


# In[14]:


def daily_search():
    try:  
        user_agent = UserAgent()
        conn = pymssql.connect(**db_settings)
        with conn.cursor() as cursor:
            insert_command = "INSERT INTO stock_data(c, d, v, z, o, h, l, tz, u, tv) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            command = "SELECT * FROM [dbo].[stock_list]"
            cursor.execute(command)
            result = cursor.fetchall()
            for r in result:
                try:
                    stock = r[0]
                    if r[2] == "上市":
                        stock_type = "tse"
                    elif r[2] == "上櫃":
                        stock_type = "otc"

                    address = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={stock_type}_{stock}.tw&json=1&delay=0"
                    response = requests.get(url=address, headers={ 'user-agent': user_agent.random })
                    data = response.text  # 這是json格式的資料
                    a_json = json.loads(data)  # 轉成dict

                    data_json = a_json["msgArray"][0]
                    date = data_json["d"] + " " + time.strftime("%H:%M:%S", time.localtime())

                    if(stock_type == "tse"): v = int(data_json["v"]) * 1000
                    else: v = int(data_json["v"])

                    change = round(float(data_json["z"]) - float(data_json["y"]), 2)
                    cursor.execute(insert_command, (r[0], date, str(v), "", data_json["o"], data_json["h"], data_json["l"], data_json["z"], str(change), ""))
                    conn.commit()
                    time.sleep(10)
                    print(time.strftime("%H:%M:%S", time.localtime()) + " " + address)
                except Exception as ex:
                    time.sleep(10)
                    print(time.strftime("%H:%M:%S", time.localtime()) + " error " + address + " " + data)
                    continue
            conn.close()
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


# In[28]:


from apscheduler.schedulers.blocking import BlockingScheduler

conn = pymssql.connect(**db_settings)
with conn.cursor() as cursor:
    today = datetime.today().strftime('%Y%m%d')
    command = "select * from [dbo].[calendar] where date = '" + today + "'"
    cursor.execute(command)
    result = cursor.fetchall()[0]
    if(result[2].strip() == "1"):
        scheduler = BlockingScheduler()

        now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        end = datetime.today().strftime('%Y-%m-%d') + " 14:00:00"
        scheduler.add_job(daily_search, 'interval', hours=1, start_date=now, end_date=end, next_run_time=now)

        def my_listener(event):
            if event.exception:
                print('The job crashed :(')
            else:
                print('The job worked :)')

        # 當任務執行完或任務出錯時，調用my_listener
        scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

        scheduler.start()
    else:
        print("no work!")


# In[ ]:




