from selenium import webdriver
from selenium.webdriver.common.by import By
import telebot
from telebot import types
import json
import time
import threading
import re
import sqlite3

bot =  telebot.TeleBot("6604939799:AAEbeeFw2_u7XygHlIVRZ_QarHPiOfGwSS4")

options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("detach", True)
options.add_argument("--mute-audio")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--headless")
options.add_argument(f'--user-agent=aboba')

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

browser = webdriver.Chrome(options=options)
browser.implicitly_wait(5)
browser.get("https://colportal.uni-college.ru/rasp/changes.php")


mas_command = ["регистрация", "замены", "замены преподавателей", "регистрация преподавателей"]
mas_time_rass = ()
time_izm = True



def check_change_time():
    global mas_time_rass

    mas_time_rass = []
    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    cur.execute(f"select time from times;")
    
    mas_time_rass_test = cur.fetchall()

    for i in mas_time_rass_test:
        mas_time_rass.append(i[0])


    cur.close()
    conn.close()

        

def bot_main_func():
    @bot.message_handler(commands=['start'])
    def input_group(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("регистрация")
        btn2 = types.KeyboardButton("замены")
        btn3 = types.KeyboardButton("замены преподавателей")
        btn4 = types.KeyboardButton("регистрация преподавателей")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, f'''
        Привет {message.chat.first_name}.
Для получения данных о заменах по группе нажмите кнопку "замены"
Для регестрации на рассылку данных о заменах по группе нажмите кнопку "регистрация"
Для получения данных о заменах по преподавателям нажмите кнопку "замены преподавателей"
Для регестрации на рассылку данных о заменах по преподавателям нажмите кнопку "регистрация преподавателей"
''', reply_markup=markup)
        
    @bot.message_handler(commands=['set_time'])
    def set_time_text(message):
        if str(message.chat.id) == "1066409953":
            for i in mas_time_rass:
                bot.send_message(message.chat.id,str(i)[2:-3])
            set_time_text1 = bot.send_message(message.chat.id,"Введите время которое хотите добавить для рассылки(19:0:0 или 7:30:10):")
            bot.register_next_step_handler(set_time_text1, set_time)
        
    @bot.message_handler(commands=['del_time'])
    def del_time_text(message):
        if str(message.chat.id) == "1066409953":
            for i in mas_time_rass:
                bot.send_message(message.chat.id,i)
            del_time_text1 = bot.send_message(message.chat.id,"Введите время которое хотите убрать для рассылки(19:0:0 или 7:30:10):")
            bot.register_next_step_handler(del_time_text1, del_time)
    @bot.message_handler(content_types=['text'])
    def main(message):
        if message.text == "регистрация":   
            mes1 = bot.send_message(message.chat.id,"Введите название вашей группы:")
            bot.register_next_step_handler(mes1, reg)
        if message.text == "замены":   
            mes2 = bot.send_message(message.chat.id,"Введите название вашей группы:")
            bot.register_next_step_handler(mes2, send_zam)
        if message.text == "замены преподавателей":
            mes2 = bot.send_message(message.chat.id,"Введите данные преподавателя(Гагарин В.А.):")
            bot.register_next_step_handler(mes2, send_zam_prepod)
        if message.text == "регистрация преподавателей":
            mes2 = bot.send_message(message.chat.id,"Введите данные преподавателя(Гагарин В.А.):")
            bot.register_next_step_handler(mes2, reg_prepod)    
#функции добавления времени и удаления
def set_time(message):
    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    cur.execute(f"Insert into times (time) values ('{str(message.text)}');")
    
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id,f"Вы успешно добавили время: {message.text}")
    check_change_time()
    
def del_time(message):

    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    cur.execute(f"DELETE FROM times WHERE time ='{str(message.text)}';")
    
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id,f"Вы успешно убрали время: {message.text}")
    check_change_time()


#фоновый режим            
def online_update_func():
    while True:
        now = time.localtime()
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        if str(now_str) in  str(mas_time_rass):
            conn = sqlite3.connect(r'database.db')
            cur = conn.cursor()
            cur.execute(f"select * from group_st;")
            
            groups = cur.fetchall()

            cur.close()
            conn.close()

            for group_names in groups:
                lines = browser.find_elements(By.CLASS_NAME,"exams")
                for item in lines:
                    param_lines = item.find_elements(By.TAG_NAME,"td")
                    if(str(param_lines[2].text) == str(group_names[2])):
                        bot.send_message(group_names[1],f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
            time.sleep(1)  
def online_update_func_prepod():
    while True:
        now = time.localtime()
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        if str(now_str) in  str(mas_time_rass):
            conn = sqlite3.connect(r'database.db')
            cur = conn.cursor()
            cur.execute(f"select * from group_prep;")
            
            preps = cur.fetchall()

            cur.close()
            conn.close()
            for prep_names in preps:
                lines = browser.find_elements(By.CLASS_NAME,"exams")
                for item in lines:
                    param_lines = item.find_elements(By.TAG_NAME,"td")
                    if(param_lines[6].text == str(prep_names[2])):
                        bot.send_message(prep_names[1],f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
            time.sleep(1)        
#регистрация     
def reg(message):
    if(message.text not in mas_command):
        user_name = str(message.chat.id)
        user_group = message.text

        conn = sqlite3.connect(r'database.db')
        cur = conn.cursor()
        cur.execute(f"select * from group_st where telegram_id ='{user_name}'")

        check_reg = cur.fetchall()
        if len(check_reg) != 0:
            cur.executescript(f"DELETE FROM group_st where telegram_id='{user_name}';")
            conn.commit()
            cur.executescript(f'Insert into group_st (telegram_id,group_name) values ("{user_name}","{user_group}");')
            conn.commit()
            bot.send_message(message.chat.id, f"Успешная перерегистрация на группу: {user_group}")
        else:
            cur.execute(f'Insert into group_st (telegram_id,group_name) values ("{user_name}","{user_group}");')
            bot.send_message(message.chat.id, f"Успешная регистрация на группу: {user_group}")
        
        conn.commit()
        cur.close()
        conn.close()
    else:   
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")

def reg_prepod(message):
    if(message.text not in mas_command):
        user_name = str(message.chat.id)
        user_fio_prepod = message.text
       
        conn = sqlite3.connect(r'database.db')
        cur = conn.cursor()
        cur.execute(f"select * from group_prep where telegram_id ='{user_name}'")

        check_reg = cur.fetchall()
        if len(check_reg) != 0:
            cur.executescript(f"DELETE FROM group_prep where telegram_id='{user_name}';")
            conn.commit()
            cur.executescript(f'Insert into group_prep (telegram_id,prep_name) values ("{user_name}","{user_fio_prepod}");')
            conn.commit()
            bot.send_message(message.chat.id, f"Успешная перерегистрация на преподавателя: {user_fio_prepod}")
        else:
            cur.execute(f'Insert into group_prep (telegram_id,prep_name) values ("{user_name}","{user_fio_prepod}");')
            bot.send_message(message.chat.id, f"Успешная регистрация на преподавателя: {user_fio_prepod}")
        
        conn.commit()
        cur.close()
        conn.close()
    else:   
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#вывод замен
def send_zam(message):
    if(message.text not in mas_command):
        lines = browser.find_elements(By.CLASS_NAME,"exams")
        check_zameni = True
        for item in lines:
            param_lines = item.find_elements(By.TAG_NAME,"td")
            if(param_lines[2].text == message.text):
                bot.send_message(message.chat.id,f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
                check_zameni = False
        if check_zameni == True:  
            bot.send_message(message.chat.id,f"Замен нет для группы: {message.text}")
    else:   
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
def send_zam_prepod(message):
    if(message.text not in mas_command):
        lines = browser.find_elements(By.CLASS_NAME,"exams")
        check_zameni_prepod = True
        for item in lines:
            param_lines = item.find_elements(By.TAG_NAME,"td")
            if(str(param_lines[6].text) == str(message.text)):
                bot.send_message(message.chat.id,f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
                check_zameni_prepod = False
        if check_zameni_prepod == True:  
            bot.send_message(message.chat.id,f"Замен нет для преподавателя: {message.text}")
    else:   
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#многопоток
if __name__ == "__main__":
    my_dict = {'mas_time_rass':mas_time_rass}
    t1 = threading.Thread(target=bot_main_func)
    t2 = threading.Thread(target=check_change_time)
    t3 = threading.Thread(target=online_update_func_prepod)
    t4 = threading.Thread(target=online_update_func,)
    
    t1.start()
    t2.start()
    t3.start()
    t4.start()


bot.polling(non_stop=True)
