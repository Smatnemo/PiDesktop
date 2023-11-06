import pygame 

PRINTER_TASKS_UPDATED = pygame.USEREVENT + 2

PAPER_FORMATS = {
    '2x6': (2, 6),      # 2x6 pouces - 5x15 cm - 51x152 mm
    '3,5x5': (3.5, 5),  # 3,5x5 pouces - 9x13 cm - 89x127 mm
    '4x6': (4, 6),      # 4x6 pouces - 10x15 cm - 101x152 mm
    '5x7': (5, 7),      # 5x7 pouces - 13x18 cm - 127x178 mm
    '6x8': (6, 8),      # 6x8 pouces - 15x20 cm - 152x203 mm
    '6x9': (6, 9),      # 6x9 pouces - 15x23 cm - 152x229 mm
}



class Printer(object):
    pass