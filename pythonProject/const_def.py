str_help = \
("   ° Перевод частоты излучения или энергии фотона в длину волны света ★[/частоту-в-длину или /энергию-в-длину];\n\n\
   ° Вычисление положение резонанса и его ширину на полувысоте, по отправленному мне файлу(.txt) ★[/резонанс];\n\n\
   ° Вычисление флюенса лазерной системы по средней мощности ★[/мощность-лазерной-системы];\n\n")

str_welcome = "Привет, я ассистент по физике! Думаю тебе нужна помощь, вот что я умею:\n\n" + str_help
str_for_user_help = "Вот мои возможности:\n\n" + str_help

str_frequency_to_lenght = "Напиши мне частоту излучения, с окончанием на обозначение её единицы измерения(Гц.)"
str_energy_to_lenght = "Напиши мне энергию фотона, с окончанием на обозначение её единицы измерения(эВ.)"
str_resonance = "Предоставь мне txt файл, имитации волн(ы). Каждая строка - точка на графике, пробел или табуляция - интенсивнось волны"

# speed of light
const_c = 299792458

# Planck's constant
const_h = 6.6260701e-34
const_ev_dj = 1.60218e-19