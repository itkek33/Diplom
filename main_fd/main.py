#импортирование всех нужных библиотек
from selenium import webdriver
from selenium.webdriver.common.by import By
import telebot
from telebot import types
import time
import threading
import sqlite3


#создание переменной с ботом и токеном
bot =  telebot.TeleBot("")


#настройки парсинга с помощью selenium и ChromeDriver
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


#создание переменной браузера с ранее созданными настройками и ссылкой на сайт с расписанием коледжа
browser = webdriver.Chrome(options=options)
browser.implicitly_wait(5)
browser.get("https://colportal.uni-college.ru/rasp/changes.php")


#переменная с массивом команд для обработки повторной отправки команд
mas_command = ["регистрация", "замены", "замены преподавателей", "регистрация преподавателей"]
#переменная с временем когда нужно отправлять данные о заменах зарегистрированных пользователей
mas_time_rass = ()
#переменная для проверки изменения таблицы с временами
time_izm = True




#функция проверки изменения данных в таблице с временами
def check_change_time():
    global mas_time_rass


    mas_time_rass = []
    #соеденение с базой данных
    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    #запрос на вывод времени из таблицы с временами
    cur.execute(f"select time from times;")
    #добавление результата запроса в переменную
    mas_time_rass_test = cur.fetchall()
   
    #перебор переменной с временами
    for i in mas_time_rass_test:
        mas_time_rass.append(i[0])


    #закрытие соеденения с базой данных
    cur.close()
    conn.close()


       
#основная функция бота
def bot_main_func():
    #декоратор start который активирует следующую функцию
    @bot.message_handler(commands=['start'])
    #стартовая функция
    def input_group(message):
        #создание переменной с кнопками
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        #создание кнопок с текстом в эту переменную
        btn1 = types.KeyboardButton("регистрация")
        btn2 = types.KeyboardButton("замены")
        btn3 = types.KeyboardButton("замены преподавателей")
        btn4 = types.KeyboardButton("регистрация преподавателей")
        #добавление в переменную с кнопками кнопок
        markup.add(btn1, btn2, btn3, btn4)
        #сообщение от бота пользователю с выводом ранее созданных кнопок
        bot.send_message(message.chat.id, f'''
        Привет {message.chat.first_name}.
Для получения данных о заменах по группе нажмите кнопку "замены"
Для регестрации на рассылку данных о заменах по группе нажмите кнопку "регистрация"
Для получения данных о заменах по преподавателям нажмите кнопку "замены преподавателей"
Для регестрации на рассылку данных о заменах по преподавателям нажмите кнопку "регистрация преподавателей"
''', reply_markup=markup)
    #декоратор для добавление времени в таблицу с временем    
    @bot.message_handler(commands=['set_time'])
    def set_time_text(message):
        #проверка является ли id пользователя id администратора так как изменять таблицу с временнем может только администратор
        if str(message.chat.id) == "1066409953":
            #вывод всех времён в таблице в чате
            for i in mas_time_rass:
                bot.send_message(message.chat.id,str(i)[2:-3])
            #ожидание нового времени от пользователя
            set_time_text1 = bot.send_message(message.chat.id,"Введите время которое хотите добавить для рассылки(19:0:0 или 7:30:10):")
            #перенос ответа в функцию для добавления времени
            bot.register_next_step_handler(set_time_text1, set_time)
    #декоратор для удаление времени из таблицы с временами    
    @bot.message_handler(commands=['del_time'])
    def del_time_text(message):
        #проверка является ли id пользователя id администратора так как изменять таблицу с временнем может только администратор
        if str(message.chat.id) == "1066409953":
            #вывод всех времён в таблице в чате
            for i in mas_time_rass:
                bot.send_message(message.chat.id,i)
            #ожидание нового времени от пользователя
            del_time_text1 = bot.send_message(message.chat.id,"Введите время которое хотите убрать для рассылки(19:0:0 или 7:30:10):")
            #перенос ответа в функцию для удаления времени
            bot.register_next_step_handler(del_time_text1, del_time)
    #декоратор для обработки текстовых ответов(нажатий на ранее созданные кнопки)
    @bot.message_handler(content_types=['text'])
    def main(message):
        #проверка на отправки от пользователя определдённого текста запрос у пользователя данных для дальнейшего взаимодейтсвия и перенос ответа в определённые функции
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
    #создание соеденения с базой данных
    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    #запрос на добавление времени в таблицу с временами с помощью ранее переданным ответом от пользователя
    cur.execute(f"Insert into times (time) values ('{str(message.text)}');")
    #сохранение изменений
    conn.commit()
    #закрытие соеденения
    cur.close()
    conn.close()
    #оповещение пользователя о успешном добавлении времени в таблицу
    bot.send_message(message.chat.id,f"Вы успешно добавили время: {message.text}")
    #активация функции для изменения переменной с временами
    check_change_time()
#функция удаления времени    
def del_time(message):
    #создание соеденения с базой данных
    conn = sqlite3.connect(r'database.db')
    cur = conn.cursor()
    #запрос на удаление времени в таблицу с временами с помощью ранее переданным ответом от пользователя
    cur.execute(f"DELETE FROM times WHERE time ='{str(message.text)}';")
    #сохранение изменений
    conn.commit()
    #закрытие соеденения
    cur.close()
    conn.close()
    #оповещение пользователя о успешном удалении времени в таблицу
    bot.send_message(message.chat.id,f"Вы успешно убрали время: {message.text}")
    #активация функции для изменения переменной с временами
    check_change_time()




#фоновый режим    
# функция проверки настоящего времени и времени в базе данных для запланированных оповещений зарегестрируемых пользователей по группам      
def online_update_func():
    #вечная работа функции
    while True:
        #занесение в переменную времени в данный момент
        now = time.localtime()
        #форматирование этой переменной
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        #проверка есть ли время в данный момент в таблице с временами
        if str(now_str) in  str(mas_time_rass):
            #соеденение с базой данных
            conn = sqlite3.connect(r'database.db')
            cur = conn.cursor()
            #запрос на вывод таблицы с данными зарегестрированными пользователями в группах
            cur.execute(f"select * from group_st;")
            # перенос результата запроса в переменную
            groups = cur.fetchall()
            #закрытие соеденение с базой данных
            cur.close()
            conn.close()
            #перебор ранее полученной переменной
            for group_names in groups:
                #парсинг сайта с расписанием по строкам в переменную
                lines = browser.find_elements(By.CLASS_NAME,"exams")
                #перебор элементов в этих строках
                for item in lines:
                    #запись в переменную элементов из линий
                    param_lines = item.find_elements(By.TAG_NAME,"td")
                    #проверка совпадает ли группа из таблицы с группами из базы данных с групой из замен на сайте колледжа
                    if(str(param_lines[2].text) == str(group_names[2])):
                        #отправка пользователю при найденной замене данные по этой замене в удобном формате
                        bot.send_message(group_names[1],f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
            #секундное ожидание для обхода ошибки с постоянным срабатыванием функции
            time.sleep(1)  
# функция проверки настоящего времени и времени в базе данных для запланированных оповещений зарегестрируемых пользователей по преподавателям  
def online_update_func_prepod():
    #вечная работа функции
    while True:
        #занесение в переменную времени в данный момент
        now = time.localtime()
        #форматирование этой переменной
        now_str = str(f"{now.tm_hour}:{now.tm_min}:{now.tm_sec}")
        #проверка есть ли время в данный момент в таблице с временами
        if str(now_str) in  str(mas_time_rass):
            #соеденение с базой данных
            conn = sqlite3.connect(r'database.db')
            cur = conn.cursor()
            #запрос на вывод таблицы с данными зарегестрированными пользователями по преподавателям
            cur.execute(f"select * from group_prep;")
            # перенос результата запроса в переменную
            preps = cur.fetchall()
            #закрытие соеденение с базой данных
            cur.close()
            conn.close()
            #перебор ранее полученной переменной
            for prep_names in preps:
                #парсинг сайта с расписанием по строкам в переменную
                lines = browser.find_elements(By.CLASS_NAME,"exams")
                #перебор элементов в этих строках
                for item in lines:
                    #запись в переменную элементов из линий
                    param_lines = item.find_elements(By.TAG_NAME,"td")
                    #проверка совпадает ли преподаватель из таблицы с преподавателями из базы данных с преподавателями из замен на сайте колледжа
                    if(param_lines[6].text == str(prep_names[2])):
                        #отправка пользователю при найденной замене данные по этой замене в удобном формате
                        bot.send_message(prep_names[1],f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
            #секундное ожидание для обхода ошибки с постоянным срабатыванием функции
            time.sleep(1)        
#регистрация    
def reg(message):
    #проверка не отправил ли пользователь текст из кнопки в качестве ответа для обработки ошибок
    if(message.text not in mas_command):
        #перенос id пользователя в переменную
        user_name = str(message.chat.id)
        #перенос ответа в переменную группы
        user_group = message.text


        #создание соеденения с базой данных
        conn = sqlite3.connect(r'database.db')
        cur = conn.cursor()
        #запрос на проверку есть ли такой id в таблице(повторная регистрация)
        cur.execute(f"select * from group_st where telegram_id ='{user_name}'")
        #перенос запросав в переменную
        check_reg = cur.fetchall()
        #проверка если переменная не пустая значит перерегистрируем пользователя если нет регестрируем пользователя
        if len(check_reg) != 0:
            #запрос на удаление старой записи о регистриции из таблицы
            cur.executescript(f"DELETE FROM group_st where telegram_id='{user_name}';")
            #сохранение изменения
            conn.commit()
            #запрос на добавления новой регистриции в таблицу(id, название группы)
            cur.executescript(f'Insert into group_st (telegram_id,group_name) values ("{user_name}","{user_group}");')
            #сохранение изменения
            conn.commit()
            #отправка пользователю итога операции
            bot.send_message(message.chat.id, f"Успешная перерегистрация на группу: {user_group}")
        #регистрация так как переменная пустая
        else:
            #запрос на добавления новой регистриции в таблицу(id, название группы)
            cur.execute(f'Insert into group_st (telegram_id,group_name) values ("{user_name}","{user_group}");')
            #отправка пользователю итога операции
            bot.send_message(message.chat.id, f"Успешная регистрация на группу: {user_group}")
        #сохранение изменений
        conn.commit()
        #закрытие соеденения с базой данных
        cur.close()
        conn.close()
    #изза нажатия кнопки повторно запрашиваем у пользователя команду повторно
    else:  
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#регистрация по преподавателям
def reg_prepod(message):
    #проверка не отправил ли пользователь текст из кнопки в качестве ответа для обработки ошибок
    if(message.text not in mas_command):
        #перенос id пользователя в переменную
        user_name = str(message.chat.id)
        #перенос ответа в переменную группы
        user_fio_prepod = message.text
        #создание соеденения с базой данных
        conn = sqlite3.connect(r'database.db')
        cur = conn.cursor()
        #запрос на проверку есть ли такой id в таблице(повторная регистрация)
        cur.execute(f"select * from group_prep where telegram_id ='{user_name}'")
        #перенос запросав в переменную
        check_reg = cur.fetchall()
        #проверка если переменная не пустая значит перерегистрируем пользователя если нет регестрируем пользователя
        if len(check_reg) != 0:
            #запрос на удаление старой записи о регистриции из таблицы
            cur.executescript(f"DELETE FROM group_prep where telegram_id='{user_name}';")
            #сохранение изменения
            conn.commit()
            #запрос на добавления новой регистриции в таблицу(id, Фио преподавателя)
            cur.executescript(f'Insert into group_prep (telegram_id,prep_name) values ("{user_name}","{user_fio_prepod}");')
            #сохранение изменения
            conn.commit()
            #отправка пользователю итога операции
            bot.send_message(message.chat.id, f"Успешная перерегистрация на преподавателя: {user_fio_prepod}")
        else:
            #запрос на добавления новой регистриции в таблицу(id, Фио преподавателя)
            cur.execute(f'Insert into group_prep (telegram_id,prep_name) values ("{user_name}","{user_fio_prepod}");')
            #отправка пользователю итога операции
            bot.send_message(message.chat.id, f"Успешная регистрация на преподавателя: {user_fio_prepod}")
        #сохранение изменений
        conn.commit()
        #закрытие соеденения с базой данных
        cur.close()
        conn.close()
    #изза нажатия кнопки повторно запрашиваем у пользователя команду повторно
    else:  
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#вывод замен по группам
def send_zam(message):
    #проверка не отправил ли пользователь текст из кнопки в качестве ответа для обработки ошибок
    if(message.text not in mas_command):
        #парсинг сайта с расписанием по строкам в переменную
        lines = browser.find_elements(By.CLASS_NAME,"exams")
        #переменная для проверки есть ли замены для введённой группы на сайте
        check_zameni = True
        #перебор элементов из строк
        for item in lines:
            #запись в переменную элементов из линий
            param_lines = item.find_elements(By.TAG_NAME,"td")
            #проверка совпадает ли группа введённая пользователем с групой из замен на сайте колледжа
            if(param_lines[2].text == message.text):
                #отправка пользователю при найденной замене данные по этой замене в удобном формате
                bot.send_message(message.chat.id,f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
                #изменение переменной так как замена нашлась
                check_zameni = False
        #если заменная не найдётся отправка пользователю информации об этом
        if check_zameni == True:  
            bot.send_message(message.chat.id,f"Замен нет для группы: {message.text}")
    #изза нажатия кнопки повторно запрашиваем у пользователя команду повторно
    else:  
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#вывод замен по преподавателям
def send_zam_prepod(message):
    #проверка не отправил ли пользователь текст из кнопки в качестве ответа для обработки ошибок
    if(message.text not in mas_command):
        #парсинг сайта с расписанием по строкам в переменную
        lines = browser.find_elements(By.CLASS_NAME,"exams")
        #переменная для проверки есть ли замены для введённой группы на сайте
        check_zameni_prepod = True
        #перебор элементов из строк
        for item in lines:
            #запись в переменную элементов из линий
            param_lines = item.find_elements(By.TAG_NAME,"td")
            #проверка совпадает ли преподаватель введённая пользователем с преподавателем из замен на сайте колледжа
            if(str(param_lines[6].text) == str(message.text)):
                #отправка пользователю при найденной замене данные по этой замене в удобном формате
                bot.send_message(message.chat.id,f"Дата:{param_lines[0].text}\nПара:{param_lines[1].text}\nГруппа:{param_lines[2].text}\nПод группа:{param_lines[3].text}\nПредмет:{param_lines[4].text}\nКабинет: {param_lines[5].text}\nПреподаватель: {param_lines[6].text}")
                #изменение переменной так как замена нашлась
                check_zameni_prepod = False
        #если заменная не найдётся отправка пользователю информации об этом
        if check_zameni_prepod == True:  
            bot.send_message(message.chat.id,f"Замен нет для преподавателя: {message.text}")
    #изза нажатия кнопки повторно запрашиваем у пользователя команду повторно
    else:  
        bot.send_message(message.chat.id,"Нажмите ещё раз на кнопку которая вам нужна")
#активация функций таким образом чтобы они могли работать паралельно друг от друга
if __name__ == "__main__":
    #создание глобальной переменной которая изменяется и используется паралельно всех функций
    my_dict = {'mas_time_rass':mas_time_rass}
    #создание переменных с функциями для паралельных работ
    t1 = threading.Thread(target=bot_main_func)
    t2 = threading.Thread(target=check_change_time)
    t3 = threading.Thread(target=online_update_func_prepod)
    t4 = threading.Thread(target=online_update_func,)
    #запуск этих функций
    t1.start()
    t2.start()
    t3.start()
    t4.start()


#вечная работа бота
bot.polling(non_stop=True)
