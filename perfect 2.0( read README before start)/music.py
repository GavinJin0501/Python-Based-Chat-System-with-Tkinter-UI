import pygame
import time
pygame.init()
pygame.mixer.init()
#pygame.mixer.music.load("Blues_Étude.wav")
#pygame.mixer.music.play()
#time.sleep(5)
#pygame.mixer.music.stop()
sound=pygame.mixer.Sound("Blues_Étude.wav")
sound.play()
time.sleep(5)
sound.stop()
