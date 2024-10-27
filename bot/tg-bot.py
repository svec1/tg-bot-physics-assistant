import telebot
import os
import copy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.signal import chirp, find_peaks, peak_widths
from telebot import types

from const_def import (str_help, str_welcome,
                       str_for_user_help, str_frequency_to_lenght,
                       str_energy_to_lenght, str_resonance,
                       const_c, const_h, const_ev_dj)

# pre-init
frequency_to_lenght = 0
energy_to_lenght = 0
resonance = 0

file_api_key = open('../api.k', 'r')
bot = telebot.TeleBot(file_api_key.read());
file_api_key.close()

markup = types.ReplyKeyboardMarkup(row_width=1)
itembtn1 = types.KeyboardButton('/частоту-в-длину')
itembtn2 = types.KeyboardButton('/энергию-в-длину')
itembtn3 = types.KeyboardButton('/резонанс')
itembtn4 = types.KeyboardButton('/мощность-лазерной-системы')
markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

def get_dots_peak(arrx: list, arry_c: list):
    if(len(arry_c) == 0):
        return []

    dots = []
    arry = copy.deepcopy(arry_c)

    start_peak = 0
    start_increase = 0
    y_small = 0
    y_start_peak = 0
    current_peak = 0

    removed = 0

    for y in arry[1:]:
        prev_y = arry[arry.index(y)-1]
        if y >= y_start_peak and y >= current_peak and start_peak:
            y_small = prev_y
            current_peak = y
        elif y >= prev_y and start_increase == 0:
            y_small = prev_y
            start_increase = 1
        elif y < current_peak and start_peak:
            dots.append(((arrx[arry.index(current_peak)]+removed, current_peak), (arry_c[arry_c.index(y)-2], y)))
            arry.remove(current_peak)
            removed += 1
            y_small = y
            current_peak = 0
            start_peak = 0
            #start_increase = 0


        if start_increase == 1 and start_peak == 0:
            start_peak = 1
            y_start_peak = y_small

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
def _proc_txt_file_to_resonance(message):
    global resonance
    if (resonance == 0):
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
        it += 1
        if (it == len(data_file) - 3):
            break
        elif (it < prefix_file_len or sym == '\\' or sym == 'n'):
            continue
        elif (sym == ' '):
            current_intensity += 1
        elif (sym == 't'):
            current_intensity += 4
        elif (sym == 'r'):
            x.append(i)
            intensity_s.append(current_intensity)
            current_intensity = 0
            i += 1
        else:
            bot.send_message(message.chat.id, "Ошибка, неправильный формат файла!")
            break

    x_array = np.array(x)

    plt.figure()
    plt.plot(x, intensity_s)

    dots = get_dots_peak(x, intensity_s)
    print(str(dots))
    for dot in dots:
        point = np.array([dot[0][0], dot[0][1]])
        plt.scatter(*point, color='red', s=10)

    intensity_s = np.array(intensity_s)

    peaks, _ = find_peaks(intensity_s)
    results_half = peak_widths(intensity_s, peaks, rel_height=0.5)
    results_full = peak_widths(intensity_s, peaks, rel_height=1)

    plt.plot(x)
    plt.plot(peaks, x_array[peaks], "x")
    plt.hlines(*results_half[1:], color="C2")
    plt.hlines(*results_full[1:], color="C3")

    plt.title("График Спектра")
    plt.xlabel("X")
    plt.ylabel("Интенсивность")

    filename = 'graph.png'
    plt.savefig(filename)
    plt.close()

    with open(filename, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(filename)

    bot.send_message(message.chat.id, str(results_half[0]))

    resonance = 0

if(__name__ == "__main__"):

    print("Debug info: " + str(bot.get_me()))

    matplotlib.use('SVG')
    bot.polling(none_stop=True, interval=0)