# window size
SCREEN_WIDTH = 1280  # Ширина экрана
SCREEN_HEIGHT = 720  # Высота экрана

# room size
GENERATE_RANDOM_ROOM = True  # Генерировать случайную комнату или по заданным ниже параметрам?
ROOM_WIDTH = 800  # Длина комнаты
ROOM_HEIGHT = 600  # Ширина комнаты
ROOM_DEPTH = 270  # Высота комнаты
WALLS_WIDTH = 10  # Толщина стен
SCALE = 1  # Масштаб отрисовки

# How many times generate room with furniture objects
MAIN_ITERATIONS = 5  # Количество различных генераций комнаты с мебелью

# Controls
DEBUG = False  # Включить отладочный режим
H_DEBUG = False
START_GA = True  # Запускать генетический алгоритм или нет
FITNESS_GRADIENT_MODE = False  # Режим отрисовки градиента фитнесса у активного объекта
FG_PRECISION = 10  # Точность отрисовки градиента фитнесса
INIT_EVERY_N = True  # Создать интерактивный режим для отрисовки каждой N-ой итерации
DRAW_EVERY_OBJ = False  # Рисовать каждый спрайт по отдельности
FPS_IN_EVERY_N = 60  # 18  # Скорость отрисовки каждой N-ой итерации в секунду
STOP_WHEN_REACHED = 1.1  # Остановиться, когда достигнута эта оценка
LANGUAGE = "EN"  #RU  # Язык интерфейса

# For GA
MAX_NUM_ITERATION = 600  # Максимальное количество итераций
POPULATION_SIZE = 100  # Размер популяции
MAX_ITERATION_WITHOUT_IMPROV = 150  # Максимальное количество итераций без улучшения
MUTATION_PROBABILITY = 0.50  # Вероятность мутации
PARENTS_PORTION = 0.15  # Доля родителей в популяции
ELIT_RATIO = PARENTS_PORTION - 0.01  # Доля элитных особей в популяции

#  #### DO NOT CHANGE ####
ROOM_SQUARE = ROOM_WIDTH * ROOM_HEIGHT  # Площадь комнаты
#   COLLISION_PENALTY
COLLISION_PENALTY = 100_000_000  # Штраф за столкновение
#   controls
X_OFFSET = (SCREEN_WIDTH - ROOM_WIDTH) // 2  # Смещение по X
Y_OFFSET = (SCREEN_HEIGHT - ROOM_HEIGHT) // 2  # Смещение по Y
#   for pygame draw
FONT, CLOCK, SCREEN = None, None, None  # Шрифт, часы, экран
ALL_OBJECTS, SPRITE_ORDER = list(), list()  # Все объекты, порядок отрисовки
CURRENT_GA_SPRITE = None  # Текущий спрайт для GA
MOUSE_MOVING_SPRITE = None  # Текущий спрайт для перемещения мышкой (для отладки)
FG_MODE_RECALC = False  # Пересчёт градиента фитнесса
DEBUG_POINTS_TO_DRAW = list()  # Интересующие нас точки (для отладки)
#  #### DO NOT CHANGE ####
