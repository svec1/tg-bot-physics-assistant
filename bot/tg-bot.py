import telebot
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from telebot import types

from const_def import (str_help, str_welcome,
                       str_for_user_help, str_frequency_to_lenght,
                       str_energy_to_lenght, str_resonance,
                       const_c, const_h, const_ev_dj)

# pre-init
frequency_to_lenght = 0
energy_to_lenght = 0
resonance = 0

file_api_key = open('api-key', 'r')
bot = telebot.TeleBot(file_api_key.read());
file_api_key.close()

markup = types.ReplyKeyboardMarkup(row_width=1)
itembtn1 = types.KeyboardButton('/частоту-в-длину')
itembtn2 = types.KeyboardButton('/энергию-в-длину')
itembtn3 = types.KeyboardButton('/резонанс')
itembtn4 = types.KeyboardButton('/мощность-лазерной-системы')
markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
def find_dots_between_peak(arrx, arry, y):
    dots = []
    dotx = 0
    doty = 0

    y_curr = 0
    i = 0
    while y_curr <= int(y/2) and i < arrx[arry.index(y)]-1:
        y_curr = arry[i]
        i+=1

    dotx = arrx[i]
    doty = arry[i]
    dots.append((dotx, doty))
    while y_curr <= int(y/2) and i < len(arrx):
        y_curr = arry[i]
        i+=1

    dotx = arrx[i]
    doty = arry[i]
    print((dotx, doty))
    dots.append((dotx, doty))

    return dots


@bot.message_handler(commands=['Привет', 'start'])
def send_welcome(message):
    bot.reply_to(message, str_welcome)
    bot.send_message(message.chat.id, "Что тебе нужно?", reply_markup=markup)

@bot.message_handler(commands=['Помоги', 'help'])
def send_help(message):
    bot.reply_to(message, "Вот мои возможности:\n\n" + str_for_user_help)

@bot.message_handler(commands=['частоту-в-длину'])
def send_need_frequency(message):
    global frequency_to_lenght, energy_to_lenght
    bot.reply_to(message, str_frequency_to_lenght)
    frequency_to_lenght = 1
    energy_to_lenght = 0

@bot.message_handler(commands=['энергию-в-длину'])
def send_need_frequency(message):
    global energy_to_lenght, frequency_to_lenght
    bot.reply_to(message, str_energy_to_lenght)
    energy_to_lenght = 1
    frequency_to_lenght = 0

@bot.message_handler(commands=['резонанс'])
def send_need_resonance(message):
    global resonance, energy_to_lenght, frequency_to_lenght
    bot.reply_to(message, str_resonance)
    resonance = 1
    energy_to_lenght = 0
    frequency_to_lenght = 0

@bot.message_handler(func=lambda message: True)
def send_frequency(message):
    global frequency_to_lenght, energy_to_lenght, const_c, const_h, const_ev_dj
    str_message = message.text.lower()
    if str_message.endswith("гц.") and frequency_to_lenght == 1:
        str_message = str_message.replace("гц.", "")
        bot.send_message(message.chat.id, "Длина волны с частотой в " + str(str_message) + " герц: " + str(const_c/int(str_message)/1000) + "км.")
        frequency_to_lenght = 0
    elif str_message.endswith("эв.") and energy_to_lenght == 1:
        str_message = str_message.replace("эв.", "")
        bot.send_message(message.chat.id, "Длина волны с энергие фотона в " + str(str_message) + " электрон-вольт: " + str(
            (const_c*const_h)/(int(str_message)*const_ev_dj)) + "нм.")
        frequency_to_lenght = 0

@bot.message_handler(content_types=['document'])
def proc_txt_file_to_resonance(message):
    global resonance
    if(resonance == 0):
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    prefix_file_len = 2
    data_file = str(downloaded_file)

    x = []
    intensity_s = []
    current_intensity = 0

    i = 0
    it = -1
    for sym in data_file:
        it += 1;
        if(it == len(data_file)-3):
            break
        elif(it < prefix_file_len or sym == '\\' or sym == 'n'):
            continue
        elif(sym == ' '):
            current_intensity += 1
        elif(sym == 't'):
            current_intensity += 4
        elif(sym == 'r'):
            x.append(i)
            intensity_s.append(current_intensity)
            current_intensity = 0
            i+=1;
        else:
            bot.send_message(message.chat.id, "Ошибка, неправильный формат файла!")
            break

    plt.figure()
    plt.plot(x, intensity_s)

    plt.plot(x[intensity_s.index(max(intensity_s))], max(intensity_s), 'ro', markersize=7, label='макс.')
    half_peak_intensity = int(max(intensity_s) - min(intensity_s))

    x_half_peak_intensity = []
    y_half_peak_intensity = []

    current_dot = 0
    dots = find_dots_between_peak(x, intensity_s, max(intensity_s))

    x_half_peak_intensity.append(dots[0][0])
    x_half_peak_intensity.append(dots[1][0])
    y_half_peak_intensity.append(dots[0][1])
    y_half_peak_intensity.append(dots[1][1])

    point1 = np.array([x_half_peak_intensity[0], y_half_peak_intensity[0]])
    point2 = np.array([x_half_peak_intensity[1], y_half_peak_intensity[1]])

    plt.scatter(*point1, color='blue', label=' A(' + str(x_half_peak_intensity[0]) + ', ' + str(y_half_peak_intensity[0]) +')')
    plt.scatter(*point2, color='green', label=' B(' + str(x_half_peak_intensity[1]) + ', ' + str(y_half_peak_intensity[1]) +')')

    plt.plot((x_half_peak_intensity[0], x_half_peak_intensity[1]), (y_half_peak_intensity[0], y_half_peak_intensity[1]), color='red')
    plt.text(x_half_peak_intensity[0]+x_half_peak_intensity[1]/4, y_half_peak_intensity[0]+3, "Hpeak/2 " + str(half_peak_intensity) + ": width " + str(abs(x_half_peak_intensity[1]-x_half_peak_intensity[0])), )

    plt.title("График Спектра")
    plt.xlabel("X")
    plt.ylabel("Интенсивность")

    filename = 'graph.png'
    plt.savefig(filename)
    plt.close()

    with open(filename, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(filename)

    bot.send_message(message.chat.id, "Ширина резонанса на полувысоте - " + str(half_peak_intensity) + ": " + str(abs(x_half_peak_intensity[1]-x_half_peak_intensity[0])+1))
    resonance = 0

if(__name__ == "__main__"):

    print("Debug info: " + str(bot.get_me()))

    matplotlib.use('SVG')
    bot.polling(none_stop=True, interval=0)