import pygame

# Definindo DIRECTION_LTR manualmente
DIRECTION_LTR = 0

# Substituindo a importação no pygame_gui
import sys
import pygame_gui.core.interfaces.font_dictionary_interface as original_module

original_module.DIRECTION_LTR = DIRECTION_LTR
sys.modules['pygame_gui.core.interfaces.font_dictionary_interface'] = original_module