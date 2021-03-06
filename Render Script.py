# -*- coding: utf-8 -*-
# Библиотека для рисования
import random
# PIL — предназначена для работы с растровой графикой. 
from PIL import Image
# модуль для работы с регулярными выражениями
import re
# Импорт модуля копирования обьектов
import copy

# Ширина картинки
scr_x = 800
# Высота картинки
scr_y = 800

#Класс отвечающий за отрисовку экрана
class Screen(object):

    #Конструктор класса
    def __init__(self, width, height):
        #Передаём высоту экрана и ширину экрана как параметры
        self.width = width
        self.height = height
        # Создадим картинку с черным цветом фона
        self.img = Image.new('RGB', (width, height), 'black')
        # Через эту переменную у нас есть доступ к пикселям картинки
        self.canvas = self.img.load()
        # Создание Z буфера
        # Перед тем как рисовать новую точку, буфер проверяет
        # есть ли там точка и какая у неё глубина, если там уже есть точка
        # если глубина точка больше по глубине чем сущестующая не рисуем её
        # в противном случе заменяем точку на экране
        # и коардинату в буфере новой точкой
        self.z_buffer = [[0] * width for i in range(height)]
        # Начальная структура Z буфера
        # [
        #   [0, 0, 0, 0]
        #   [0, 0, 0, 0]
        #   [0, 0, 0, 0]
        # ]
        
    #Метод point будет добавлять обьект класса Point
    #теперь точки будут знать к комуони пренадлежат
    #это добавляет к ним обьект screen
    def point(self, *coords):
        return TexturePoint(self, *coords)

    @staticmethod
    # Функция рисования треугольника принмает коардинаты и цвет
    def triangle(coords, texture):

        # Сортировка коардинат через регулярное выражение
        a, b, c = sorted(coords, key=lambda p: p.y)
        # Копитуем коардинаты
        p1 = a.copy()
        p2 = a.copy()
        # Делим треугольник пополам от б до а и от с до а
        # Длинна линии от a до b
        # х = width / height = b.x - a.x / b.y - a.y
        delta_p1 = zero_div((b.x - a.x), (b.y - a.y))
        # Длинна линии от a до c
        delta_p2 = zero_div((c.x - a.x), (c.y - a.y))
        # То же самое но по оси Z
        delta_z1 = zero_div((b.z - a.z), (b.y - a.y))
        delta_z2 = zero_div((c.z - a.z), (c.y - a.y))
        
        # Рисуем линию пока она входит в диапазон от и до с
        for y in (b.y, c.y):
            
            # Пока первая точка по у < y
            while p1.y < y:
                #Если первая точка по х
                if p1.x > p2.x:
                    # Копируем её 
                    p3 = p2.copy()
                    # Устраняет ребристость модели
                    # Меняем Z и при рорисовке горизонтальных линий
                    p4 = p1.copy()
                    # х приравниваем 1й точке
                    x = p1.x
                else:
                    # Если нет копируем 1ю точку
                    p3 = p1.copy()
                    # Меняем Z и при рорисовке горизонтальных линий
                    p4 = p2.copy()
                # Так же меняем глубину Z по оси Х
                delta_z3 = zero_div((p4.z - p3.z), (p4.x - p3.x))
                # Пока последняя копированная точка < х
                while p3.x < p4.x:
                    # Показываем её color было рандомно
                    # теперь контрастность точки прямо пропорциональна
                    # коардинате глубины Z чем ближе тем ярче
                    p3.show(texture[p3.u, p3.v])
                    # Прибавляем коаринату
                    p3.x += 1
                    # То же самое но по оси Z
                    p3.z += delta_z3
                # Прибавляем ок всем копированным точка по у 1
                p1.y += 1
                p2.y += 1
                # Прибавляем ко всем копированным точкам то х
                # длинну отрисованной линии
                p1.x += delta_p1
                p2.x += delta_p2
                # То же самое но по оси Z
                p1.z += delta_z1
                p2.z += delta_z2
            # Длинна линии от b до c
            delta_p1 = zero_div((c.x - b.x), (c.y - b.y))
            # То же самое но по оси Z
            delta_z1 = zero_div((c.z - b.z), (c.y - b.y))
            # Eсли а и б коардинаты находятся на одной высоте по У
            # то нижняя часть треугольника отсутствует и он не прорисовывается
            # Для этого в конце сикла принудительно копируем коардинаты
            # Этим мы сделаем аолгоритм точнее он страдает от обновлений до целых
            p1 = b.copy()
        
# Класс который принимает обьект и рисует точку
class Point(object):
    
    # Конструктор принмающий коардинаты
    def __init__(self, screen, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.screen = screen
        
    # Метод для показа точки определённого цвета на конве
    def show(self, color=None):
        # Убираем слово self ото всюду
        screen = self.screen
        x = int(self.x)
        y = int(self.y)
        # Возможно перепутанны Х У местами
        if self.z <= screen.z_buffer[x][y]:
            # Если глубина Z точки меньше буфера
            return
        # Передаём её в буфер как новую коардинату
        screen.z_buffer[x][y] = self.z
        screen.canvas[x, screen.height-y] = color or (255, 255, 255)
    # Метод для создания копий коардинат точек
    def copy(self):
        # Метод создаёт полную копию обьекта
        return copy.copy(self)

# Класс текстурированной точки, наследует обычную и имеет
# 2 дополнительных переметра коардинаты текстуры
class TexturePoint(Point):
    
    # Конструктор принмающий коардинаты
    def __init__(self, screen, x, y, z, u, v):
        # Вызываем метод родителя и передаём ему коардинаты
        super(TexturePoint, self).__init__(screen, x, y, z)
        # Устанавливаем коардинаты тектуры
        self.u = u
        self.v = v

# Функция деления на 0
def zero_div(a, b):
    return float(a)/b if b else 0

# Функуия отрисовку лица
def show_face():        
    # Обьявляем константы для масштабирования при любом разрешении экрана
    half_scr_x = int(scr_x / 2)
    half_scr_y = int(scr_y / 2)
    # Чтение текстуры лица
    texture_img = Image.open('african_head_diffuse.tga')
    # Загрузка текстуры лица
    texture = texture_img.load()
    # Чтение файла с моделью
    f = open('face.obj', 'r')
    # Перевод содержимого файла в строку
    lines = f.read()
    # Создание пустого массива для точек
    points = []
    # Создание пустого массива для текстарных коардинат
    textures = []
    #Создаём обьект экрана и передаём ему параметры
    screen = Screen(scr_x, scr_y)

    # Разбитие строки с помщью регулярного выражения
    for line in lines.split('\n'):

        # Разрезка строки по пробелам регулярное выражение
        try:
            # v - представляет ли собой строка набор коардинат
            v, x, y, z = re.split('\s+', line)
        except:
            continue
        # Если строка v - это набор коардинат
        if v == 'v':
            # Все коардинады представляют собой дапазон от -1 до 1
            # Что бы вписать их в канву переводим полочительный диапазон
            # Максимальная окардината картинки у нас 800 пикселей
            # а максимальная коардината обьекта из документа это 2
            # для маштабирования умножаем каждую коардинату на 400
            # и приводим их в целочисленное значение
            x = int((float(x) + 1) * half_scr_x)
            
            # scr_y что бы перевернуть картинку
            # так как коардинаты по у в документе идут снизу вверх
            # у1  у2
            # 0 - 800
            # 1 - 799
            # 2 - 798
            # вывод от у2 - у1 = нужная коардината
            y = int((float(y) + 1) * half_scr_y)

            # Для создания обьёмного изображения будем использовать Z буфер
            # этот массив который будет хранить расстояние точек от наблюдателей
            # так нахываемая карта теней, где вместо цвета хранитьсяего глубина
            # К любой коардинате + 1 так как массив начинается с 0 а коардината
            # в документе с единицы
            z = float(z)+1
            
            # Передаём эти пиксели конве
            points.append((x, y, z))
        # Если строка vt - это набор коардинат текстуры    
        if v == 'vt':
            # Коардината задана в диапазоне от 0 до 1
            # масштабируем до ширины и высоты картинкистекстурой
            u = float(x) * texture_img.width
            u = float(y) * texture_img.height
            textures.append((u, v))
            
        # Если строка f - это кодирование полигонов    
        if v == 'f':
            # Выбираем рандомный цвет заливки полигона
            color = tuple([random.randint(0, 255)] * 3)
            
            # Передаём функции отрисовки полигонов коардинаты
            # в обьект поинтс передаём коардинаты приведённые
            # в целочисленное значение массива разрезанного
            # по регулярному выражению, из них берём только 1й фрагмент массива
            # и отнимает от него 1 так как в массиве всё начинается с 0
            # а в документе с 1 делаем это в цикле из x y z  коардинат
            # и та же переда1м цвет
            #triangle([points[int(i.split('/')[0])-1] for i in (x, y, z)], color)

            # Строки описывающие массив полигонов, преабразуем в массив из 3х элементов
            # Каждый элемент описывает точку треугольника 1е число номер 3Д точки
            # 2е число номер текстурной точки 
            indexes = [[int(j)-1 for j in i.split('/')] for i in (x, y, z)]
            tr_points = []
            for i in range(3):
                params = points[indexes[i][0]] + textures[indexes[i][1]]
                tr_points.append(screen.point(*params))
            screen.triangle(tr_points, texture)
    # Выводим изображение на экран
    screen.img.show()

# Отрисовать лицо вызов процедуры
show_face()
