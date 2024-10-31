import math

import telebot
import os
import copy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_widths
from telebot import types

from const_def import (str_help, str_welcome,
                       str_for_user_help, str_frequency_to_lenght,
                       str_energy_to_lenght, str_resonance,
                       const_c, const_h, const_ev_dj, const_nm,
                       action1_str_freq_to_lenght,action2_str_e_to_lenght, action3_str_lenght_to_freq,
                       action4_str_lenght_to_e, action5_str_resonance, action6_str_power_ls,
                       str_lenght_to_frequency, str_lenght_to_energy, const_ev_mkev)

def is_number(string):
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False

# pre-init
frequency_to_lenght = 0
energy_to_lenght = 0
lenght_to_frequency = 0
lenght_to_energy = 0
resonance = 0

file_api_key = open('../api.k', 'r')
bot = telebot.TeleBot(file_api_key.read());
file_api_key.close()

markup = types.ReplyKeyboardMarkup(row_width=3)
itembtn1 = types.KeyboardButton(action1_str_freq_to_lenght)
itembtn2 = types.KeyboardButton(action2_str_e_to_lenght)
itembtn3 = types.KeyboardButton(action3_str_lenght_to_freq)
itembtn4 = types.KeyboardButton(action4_str_lenght_to_e)
itembtn5 = types.KeyboardButton(action5_str_resonance)
itembtn6 = types.KeyboardButton(action6_str_power_ls)
markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)

def null_setup_bool_control():
    global frequency_to_lenght, frequency_to_lenght, \
        energy_to_lenght, lenght_to_frequency, lenght_to_energy, resonance
    frequency_to_lenght = 0
    energy_to_lenght = 0
    lenght_to_frequency = 0
    lenght_to_energy = 0
    resonance = 0

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

def send_need_frequency(message):
    global frequency_to_lenght
    bot.send_message(message.chat.id, str_frequency_to_lenght)
    null_setup_bool_control()
    frequency_to_lenght = 1

def send_need_energy(message):
    global energy_to_lenght
    bot.send_message(message.chat.id, str_energy_to_lenght)
    null_setup_bool_control()
    energy_to_lenght = 1

def send_need_lenght_for_freq(message):
    global lenght_to_frequency
    bot.send_message(message.chat.id, str_lenght_to_frequency)
    null_setup_bool_control()
    lenght_to_frequency = 1

def send_need_lenght_for_energy(message):
    global lenght_to_energy
    bot.send_message(message.chat.id, str_lenght_to_energy)
    null_setup_bool_control()
    lenght_to_energy = 1

def send_need_file_for_resonance(message):
    global resonance
    bot.send_message(message.chat.id, str_resonance)
    null_setup_bool_control()
    resonance = 1

@bot.message_handler(func=lambda message: True)
def logic(message):
    global frequency_to_lenght, energy_to_lenght, lenght_to_frequency, lenght_to_energy, const_c, const_h, const_ev_dj, const_nm
    str_message = message.text.lower()
    if frequency_to_lenght == 1 and str_message.endswith("гц."):
        str_message = str_message.replace("гц.", "")
        bot.send_message(message.chat.id, "Длина волны с частотой в " + str(str_message) + " герц: " + str(
            const_c / float(str_message) / 1000) + "км.")
    elif energy_to_lenght == 1 and str_message.endswith("эв."):
        str_message = str_message.replace("эв.", "")
        bot.send_message(message.chat.id, "Длина волны с энергие фотона в " + str(str_message) + " электрон-вольт: " + str(
            (const_c * const_h) / (float(str_message) * const_ev_dj)/const_nm) + "нм.")
    elif lenght_to_frequency == 1 and str_message.endswith("м."):
        if str_message.endswith("см."):
            str_message = str_message.replace("см.", "")
            bot.send_message(message.chat.id,
                            "Частота волны длиной " + str(str_message) + " см.: " + str(const_c / float(str_message) * 100) + "Гц.")
        elif str_message.endswith("км."):
            str_message = str_message.replace("км.", "")
            bot.send_message(message.chat.id,
                         "Частота волны длиной " + str(str_message) + " км.: " + str(const_c / float(str_message) / 1000) + "Гц.")
        else:
            str_message = str_message.replace("м.", "")
            bot.send_message(message.chat.id,
                         "Частота волны длиной " + str(str_message) + " м.: " + str(const_c / float(str_message)) + "Гц.")
    elif lenght_to_energy and str_message.endswith("м."):
        ratio = 1
        if str_message.endswith("нм."):
            str_message = str_message.replace("нм.", "")
            ratio = const_nm
        elif str_message.endswith("см."):
            str_message = str_message.replace("см.", "")
            ratio = 0.01
        else:
            str_message = str_message.replace("м.", "")
            ratio = 1

        if not is_number(str_message):
            bot.reply_to(message, "Нужно числовое значение")
            return

        energy = (const_c * const_h) / (float(str_message)*ratio)
        energy_mkev = round((energy / const_ev_dj)* const_ev_mkev, 4)
        if energy_mkev > 1000:
            bot.send_message(message.chat.id,"Энергия фотона волны длиной " + str(str_message) + " нм.: " + str(energy_mkev/const_ev_mkev) + "эВ. или " + str(energy) + "дж.")
        else:
                bot.send_message(message.chat.id,"Энергия фотона волны длиной " + str(str_message) + " нм.: " + str(energy_mkev) + "мкэВ. или " + str(energy) + "дж.")
    else:
        command(message)

@bot.message_handler(func=lambda message: True)
def command(message):
    global frequency_to_lenght, energy_to_lenght, lenght_to_frequency, lenght_to_energy, const_c, const_h, const_ev_dj
    str_message = message.text.lower()
    if str_message == action1_str_freq_to_lenght:
        send_need_frequency(message)
    elif str_message == action2_str_e_to_lenght:
        send_need_energy(message)
    elif str_message == action3_str_lenght_to_freq:
        send_need_lenght_for_freq(message)
    elif str_message == action4_str_lenght_to_e:
        send_need_lenght_for_energy(message)
    elif str_message == action5_str_resonance:
        send_need_file_for_resonance(message)
    else:
        if frequency_to_lenght == 1:
            bot.reply_to(message, str_frequency_to_lenght)
        elif energy_to_lenght == 1:
            bot.reply_to(message, str_energy_to_lenght)
        elif lenght_to_frequency == 1:
            bot.reply_to(message, str_lenght_to_frequency)
        elif lenght_to_energy == 1:
            bot.reply_to(message, str_lenght_to_energy)
        else:
            send_help(message)

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
            return

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