#Mise en garde : le jeu fonctionne de façon fluide pour moi mais j'ai noté des problèmes de framerate lorsque non joué en plein écran
#J'ai donc mis le jeu en plein écran par défaut, je vous prie de me prévenir si vous deviez rencontrer des problèmes de framerate malgré tout

import pygame,sys
from pygame.locals import *
import random

'''         CONFIG          '''
WIDTH = 800
LENGTH = 640
BLACK = (15,15,15)
RED = (255,0,0)
WHITE = (255,255,255)
'''         CONFIG          '''

'''initialisation du module pygame et de l'écran de fond '''

pygame.init()
screen = pygame.display.set_mode((WIDTH,LENGTH),pygame.FULLSCREEN)

pygame.key.set_repeat(5,5) #Méthode pygame pour comprendre une touche enfoncé un certain nombre de millisecondes comme une touche préssée plusieurs fois
clock = pygame.time.Clock() #Méthode de pygame pour gérer le temps  : permet de gérer les fps et les cooldowns 

'''                                                      '''
''' definition des variables globales et des groupes de sprites '''
BULLETS = pygame.sprite.Group()
ENNEMIES = pygame.sprite.Group()
ships = pygame.sprite.Group()
n_col_ennemies = 12
descent_speed = 6
cooldown_tracker = 0
game_over = 0
REFRESH_RATE = 60
BULLET_SPEED = 8
BULLET_SPAWN = pygame.USEREVENT +1  #Création d'un événement périodique 
pygame.time.set_timer(BULLET_SPAWN,700) #qui se déclenchera toutes les 700ms 

'''                                                         '''


''' Fonctions d'affichage , de mise à jour de l'écran et de fermeture du jeu '''
def leave_game():
	print("player asked to leave the game")
	pygame.display.quit()
	pygame.quit()
	sys.exit()

def update_screen():
    screen.fill(BLACK)
    ENNEMIES.draw(screen)
    ships.draw(screen)
    BULLETS.draw(screen)
    pygame.display.flip()

def display_text(text, color, x, y, font, police, centered=True):
    font = pygame.font.SysFont(font, police, True)
    message = font.render(text, True, color)
    textrect = message.get_rect()
    if centered:
        textrect.centerx = x
        textrect.centery = y
    screen.blit(message, textrect)

def winning_message():
    screen.fill(BLACK)
    display_text('GAME OVER !', RED, WIDTH * 0.5 , LENGTH * 0.2, 'Calibri', 40)
    display_text('Tu as gagné', WHITE, WIDTH * 0.5, LENGTH * 0.3, 'Calibri', 30)
    pygame.display.flip()

def losing_message():
    screen.fill(BLACK)
    display_text('GAME OVER !', RED, WIDTH * 0.5 , LENGTH * 0.2, 'Calibri', 40)
    display_text('Tu as perdu', WHITE, WIDTH * 0.5, LENGTH * 0.3, 'Calibri', 30)
    pygame.display.flip()
'''   Fonctions d'affichage , de mise à jour de l'écran et de fermeture du jeu           '''


''' ça devient intéressant ''' 


''' définition des 3 classes ''' 

''' Classe des vaisseaux ennemis '''

class ennemy(pygame.sprite.Sprite):
    def __init__(self,speed, xpos, ypos, rangx, rangy,  hp =1):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Pictures/alien.png")
        self.rect = self.image.get_rect()
        self.rect.x = xpos 
        self.speed = speed
        self.rect.y = ypos
        self.rangx = rangx
        self.rangy = rangy
        self.hp =hp
        self.direction = 1 
    
    def update(self):  #Les fonctions appelées sont définies après 
        if someone_out_of_border(ENNEMIES):
            everyone_goes_down_and_left(ENNEMIES,self.direction,self.rangx, self.rangy)  #Permet de changer le sens de circulation des vaisseaux une fois arrivés au bord
        self.rect.x += self.direction * self.speed
        
        


''' Classe du vaissau joueur '''

class spaceShip(pygame.sprite.Sprite):

#Creation du vaisseau joueur, qui dirige sa position sur l'axe horizontal, peut tirer un projectile vers les ennemis
    
    def __init__(self, xpos, ypos, speed, hp = 1):
            pygame.sprite.Sprite.__init__(self)
            self.image = pygame.image.load("Pictures/SpaceShip.png")
            self.rect = self.image.get_rect()
            self.rect.x = xpos
            self.speed = speed
            self.rect.y = ypos
            self.hp =hp

    #Deplacement du vaisseau sur une axe horizontal ou tirer un projectile, on vérifie que le vaisseau reste bien dans l'écran de jeu
    
    def update(self,key):
        if ship.rect.x < 0 :
            if key=='right':
                self.rect.x += self.speed
            elif key == 'space':
                self.fire()
        elif ship.rect.x > 740 :
            if key =='left':
                self.rect.x -= self.speed
            elif key == 'space':
                self.fire()
        else: 
            if key =='left':
                self.rect.x -= self.speed
            elif key=='right':
                self.rect.x += self.speed
            elif key == 'space':
                self.fire()
        
    
    def fire(self):   #Le vaisseau joueur peut tirer un projectile avec un certain cooldown 
        global cooldown_tracker
        cooldown_tracker += clock.get_time()
        if cooldown_tracker > 400:
            cooldown_tracker = 0
        if cooldown_tracker == 0 :
            b = bullet(0,BULLET_SPEED,self.rect.x + 22, 520)
            BULLETS.add(b)


''' CLasse des projectiles '''

class bullet(pygame.sprite.Sprite):

    def __init__(self,direction,speed, xpos, ypos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("Pictures/bullet.png")
        self.direction = direction
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = ypos
        
    #Les projectiles sont tirés par le joueur comme par les ennemis, et doivent s'auto détruire et détruire le sprite avec lequel ils rentrent en collision 
    def update(self):  
        if self.direction == 0 :
            self.rect.y -= self.speed
        elif self.direction == 1:
            self.rect.y += self.speed 
        if self.collide(ships) :  
            self.collide(ships).kill()
            global game_over 
            game_over = 1
            self.kill()
        if self.collide(ENNEMIES) and self.direction ==0:
            self.kill()
            self.collide(ENNEMIES).kill()
            speed_update(ENNEMIES)
        if self.out_of_screen():
            self.kill()
        
    def out_of_screen(self):
        if self.rect.y < 0 - LENGTH * 0.1 or self.rect.y > LENGTH * 1.1:
            return True
        
        
    def collide(self, sprites):   # test la collision et renvoie le sprite percuté pour pouvoir lui aussi le supprimer  
        for sprite in sprites : 
            if pygame.sprite.collide_mask(self, sprite):
                return sprite 

''' C'est fini pour les classes ''' 
        

''' Fonctions du jeu principales, hors classes ''' 

def create_ennemies():  #Permet de créer au début du jeu la grille de vaisseaux ennemis 
    global n_col_ennemies
    for i in range (0,n_col_ennemies):
        for j in range(0,6):
            new_ennemy = ennemy(1,100+50*i,10+50*j,i+1, j+1)
            ENNEMIES.add(new_ennemy)
    ENNEMIES.draw(screen)
    pygame.display.flip()

#Toutes les x ms, un ennemi tiré au sort doit tirer un projectile, il faut que cet ennemi soit en bas de sa colonne 
def random_bullet(ENNEMIES):
    global n_col_ennemies
    if len(ENNEMIES)==0:  #Exception si tous les ennemis sont déjà détruits 
        game_over=1
        return game_over
    x = random.randint(1,n_col_ennemies)    #On tire une colonne au hasard 
    xpos = 0 
    ypos = 0 
    for ennemy in ENNEMIES : 
        if ennemy.rangx == x :      #on regarde si il y a encore un ennemi vivant dans cette colonne 
            xpos = ennemy.rect.x
            ypos = ennemy.rect.y
    if xpos == 0 :                  #S'il n'y a pas d'ennemies on rappelle la fonction pour tirer au sort un autre colonne 
        random_bullet(ENNEMIES)
    else : 
        b = bullet(1,BULLET_SPEED,xpos + 9, ypos +30 ) #S'il y a bien un ennemi on tire un projectile, comme les ennemis ont été créé de haut en bas..
        BULLETS.add(b)                                 #.. on sait que ypos correspond bien a la position de l'ennemi le plus bas sur la colonne 


#On teste si les ennemis ont atteint le bord de l'écran 
def someone_out_of_border(ENNEMIES):
    for ennemy in ENNEMIES : 
        if ennemy.rect.x < 20 or ennemy.rect.x > 740:
            return True
    return False 

#Si tous les ennemis ont atteint le bord, on les fait changer de direction et descendre d'un cran 
def everyone_goes_down_and_left(ENNEMIES,direction, rangx, rangy):
    global descent_speed
    for ennemy in ENNEMIES:
        if ennemy.rect.x < 25 : 
            ennemy.rect.x = 22
        if ennemy.rect.x > 730 : 
            ennemy.rect.x = 740
        ennemy.direction = - direction
        ennemy.rect.y += descent_speed
        ennemy.rect.x += ennemy.direction 

#Au fur et à mesure du jeu, moins il y a d'ennemis plus ces derniers vont vite 
def speed_update(ENNEMIES):
    if  len(ENNEMIES)== 50 or len(ENNEMIES) == 30  :
        for ennemy in ENNEMIES : 
            ennemy.speed = ennemy.speed + 1
    if len(ENNEMIES) == 10 or len (ENNEMIES)== 1 :
        for ennemy in ENNEMIES : 
            ennemy.speed += 2

#Si les ennemis sont trop bas, le joueur a perdu 
def check_position(ENNEMIES):
    global game_over
    for ennemy in ENNEMIES:
        if ennemy.rect.y > 500 : 
            game_over = 2
            continue 

''' Fin des fonctions principales ''' 

''' INITIALISATION du vaisseau du joueur et des ennemis, ''' 
ship = spaceShip(WIDTH/2-50,550,8)
ships.add(ship)
ships.draw(screen)
create_ennemies()
pygame.display.flip()
'''                 '''


''' Boucle de jeu '''

while not game_over:
    update_screen()
    BULLETS.update()
    ENNEMIES.update()
    for event in pygame.event.get():  
        if event.type == BULLET_SPAWN :
            random_bullet(ENNEMIES)  
        if event.type == QUIT : 
            leave_game() 
        if not hasattr(event , 'key'): #si aucune touche n'est pressé on relance la boucle 
            continue
        if event.key == K_ESCAPE :
            leave_game()
        ships.update(pygame.key.name(event.key))
        clock.tick(REFRESH_RATE)
    check_position(ENNEMIES)
    if len(ENNEMIES)==0 :
        game_over =1
    if len(ships)==0:
        game_over = 2

#Message de fin de partie tant que le joueur ne quitte pas        
while True : 
    if game_over ==1 : 
            winning_message()
    if game_over == 2 :
            losing_message()
    for event in pygame.event.get():
        if event.type == QUIT : 
            leave_game() 
        if not hasattr(event , 'key'):
            continue
        if event.key == K_ESCAPE :
            leave_game()


''' FIN '''