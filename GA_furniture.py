from geneticalgorithm2 import geneticalgorithm2 as ga
from geneticalgorithm2 import ActionConditions, MiddleCallbacks
import settings
import os


def set_sprite_values(data):
    settings.CURRENT_GA_SPRITE.rect.center = (data[0], data[1])
    settings.CURRENT_GA_SPRITE.angle = int(data[2])
    settings.CURRENT_GA_SPRITE.update()

    # for i, sprite in enumerate(settings.FURNITURE_SPRITES):
    #     if i == settings.CURRENT_OBJECT:
    #         # sprite.rect.center = (data[0 + i * 3], data[1 + i * 3])
    #         # sprite.angle = data[2 + i * 3]
    #         sprite.rect.center = (data[0], data[1])
    #         sprite.angle = int(data[2])
    #         sprite.update()


def get_current_fitness(data):
    fit_sum = settings.CURRENT_GA_SPRITE.get_fitness()
    # fit_sum = 0
    # for sprite in settings.FURNITURE_SPRITES:
    #     fit_sum += sprite.get_fitness()

    # pygame.image.save(settings.DISPLAY_SURFACE, f"video/test_{settings.COUNTER}_{number}.png")

    return fit_sum


def fitness_function(data):
    set_sprite_values(data)
    fitness = get_current_fitness(data)
    return fitness


def start_ga():
    # ==================== GA ====================
    var_bound = [
        (0, settings.ROOM_WIDTH),  # X
        (0, settings.ROOM_HEIGHT),  # Y
        (0, 360)  # angle
    ]

    algorithm_param = {'max_num_iteration': settings.MAX_NUM_ITERATION,
                       'population_size': settings.POPULATION_SIZE,
                       'mutation_probability': settings.MUTATION_PROBABILITY,
                       'elit_ratio': settings.ELIT_RATIO,
                       'parents_portion': settings.PARENTS_PORTION, }

    # furniture_amount = len(settings.FURNITURE_SPRITES)
    model = ga(function=fitness_function,
               dimension=3,  # *furniture_amount,
               variable_type='int',
               variable_boundaries=var_bound,  # *furniture_amount,
               function_timeout=60 * 10,
               algorithm_parameters=algorithm_param)

    # model.run()
    # model.run(no_plot=True)
    # model.run(no_plot=True, stop_when_reached=0.84)
    from draw_engine import draw_every_generation
    model.run(no_plot=True, stop_when_reached=1.1,
              middle_callbacks=[MiddleCallbacks.UniversalCallback(draw_every_generation, ActionConditions.Always())])
    # model.run(stop_when_reached=1)
    # model.run(middle_callbacks=[MiddleCallbacks.UniversalCallback(own_action(), ActionConditions.Always())])

    solution = model.result
    return solution
    # ==================== GA ====================


def get_various_indexes(solution):
    various_indexes = []
    various_solutions = []
    for i, data in enumerate(solution.last_generation.variables):
        if data.tolist() not in various_solutions:
            various_solutions.append(data.tolist())
            various_indexes.append(i)
    return various_indexes
