#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: tasdik
# @Contributers : Branden (Github: @bardlean86)
# @Date:   2016-01-17
# @Email:  prodicus@outlook.com  Github: @tasdikrahman
# @Last Modified by:   tasdik
# @Last Modified by:   Branden
# @Last Modified by:   Dic3
# @Last Modified time: 2016-10-16
# MIT License. You can find a copy of the License @ http://prodicus.mit-license.org

## Game music Attribution
##Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 <http://creativecommons.org/licenses/by/3.0/>

## Additional assets by: Branden M. Ardelean (Github: @bardlean86)

from __future__ import division
import pygame
import random
from os import path

import fuzzy_engine
import fuzzy_ui

## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

###############################
## to be placed in "constant.py" later

# ─── Layout ───
#  +────────────────────────+──────────────────+
#  │  TOP BAR (560 × 160)   │                  │
#  +────────────────────────+  PLOTS (720×720) │
#  │                        │  3×3 grid        │
#  │  GAME AREA (560 × 560) │                  │
#  │                        │                  │
#  +────────────────────────+──────────────────+

GAME_WIDTH = 560
PLOT_WIDTH = 720
TOP_HEIGHT = 160
GAME_HEIGHT = 560
WIDTH = GAME_WIDTH + PLOT_WIDTH  # 1280
HEIGHT = TOP_HEIGHT + GAME_HEIGHT  # 720

FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
###############################

###############################
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()     ## For syncing the FPS
###############################

font_name = pygame.font.match_font('arial')


# ─── Init Fuzzy Engine ───
engine = fuzzy_engine.FuzzyDifficultyEngine()
mf_data = engine.get_mf_data()

# ─── Global state ───
restart_count = 0
game_paused = False
manual_mode = False
sidebar_btns = []

# throttle the AI:
last_fuzzy_update = 0 
FUZZY_UPDATE_RATE = 500 # Milliseconds between fuzzy calculations
plot_surface = pygame.Surface((PLOT_WIDTH, HEIGHT))
last_plot_update = 0
PLOT_UPDATE_RATE = 500

dda_metrics = {
    "total_mobs_spawned": 0,
    "mobs_destroyed": 0,
    "session_time_elapsed": 0,
    "health": 100,
    "lives": 5,
    "gun_level": 1,
    "restart_count": 0,
    "current_speed_mult": 1.0,
    "current_spawn_delay": 1.5,
    "current_mob_size": 1.0,
    "fired_rules": [],
}


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def run_fuzzy():
    outputs = engine.evaluate(
        dda_metrics["mobs_destroyed"],
        dda_metrics["session_time_elapsed"],
        dda_metrics["health"],
        dda_metrics["lives"],
        dda_metrics["gun_level"],
        dda_metrics["restart_count"],
    )
    dda_metrics["current_speed_mult"] = outputs["speed_mult"]
    dda_metrics["current_spawn_delay"] = outputs["spawn_delay"]
    dda_metrics["current_mob_size"] = outputs["mob_size"]
    dda_metrics["fired_rules"] = outputs["fired_rules"]


def main_menu():
    global screen
    try:
        pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    title = pygame.image.load(path.join(img_dir, "main.png")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)
    screen.blit(title, (0, 0))
    pygame.display.update()

    waiting = True
    while waiting:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                waiting = False
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        elif ev.type == pygame.QUIT:
            pygame.quit()
            quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH / 2, HEIGHT / 2)
            draw_text(screen, "or [Q] To Quit", 30, WIDTH / 2, HEIGHT / 2 + 40)
            pygame.display.update()

    #pygame.mixer.music.stop()
    try:
        ready = pygame.mixer.Sound(path.join(sound_folder, "getready.ogg"))
        ready.play()
    except Exception:
        pass
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH / 2, HEIGHT / 2)
    pygame.display.update()


def draw_text(surf, text, size, x, y):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       ## True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0) 
    ## moving them to top
    # BAR_LENGTH = 100
    # BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)
    dda_metrics["total_mobs_spawned"] += 1

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = GAME_WIDTH / 2
        self.rect.bottom = TOP_HEIGHT + GAME_HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 5
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        ## time out for powerups
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        ## unhide 
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = GAME_WIDTH / 2
            self.rect.bottom = TOP_HEIGHT + GAME_HEIGHT - 30

        self.speedx = 0     ## makes the player static in the screen by default. 
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 

        ## will give back a list of the keys which happen to be pressed down at that moment
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5

        #Fire weapons by holding spacebar
        if keystate[pygame.K_SPACE]:
            self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > GAME_WIDTH:
            self.rect.right = GAME_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        self.rect.x += self.speedx

    def shoot(self):
        ## to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (GAME_WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images).copy()
        self.image_orig.set_colorkey(BLACK)

        # DDA mob_size scaling
        size_scale = dda_metrics.get("current_mob_size", 1.0)
        ow, oh = self.image_orig.get_size()
        nw = max(8, int(ow * size_scale))
        nh = max(8, int(oh * size_scale))
        self.image_orig = pygame.transform.scale(self.image_orig, (nw, nh))

        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.90 / 2)
        self.rect.x = random.randrange(0, max(1, GAME_WIDTH - self.rect.width))
        self.rect.y = random.randrange(TOP_HEIGHT - 150, TOP_HEIGHT - 40)
        self.speedy = random.randrange(5, 20)        ## for randomizing the speed of the Mob

        ## randomize the movements a little more 
        self.speedx = random.randrange(-3, 3)

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen

    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy * dda_metrics["current_speed_mult"]

        ## now what if the mob element goes out of the screen
        bottom_edge = TOP_HEIGHT + GAME_HEIGHT
        if (
            self.rect.top > bottom_edge + 10
            or self.rect.left < -25
            or self.rect.right > GAME_WIDTH + 20
        ):
            self.rect.x = random.randrange(0, max(1, GAME_WIDTH - self.rect.width))
            self.rect.y = random.randrange(TOP_HEIGHT - 100, TOP_HEIGHT - 40)
            self.speedy = random.randrange(1, 8)        ## for randomizing the speed of the Mob

## defines the sprite for Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > TOP_HEIGHT + GAME_HEIGHT:
            self.kill()



## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < TOP_HEIGHT:
            self.kill()

        ## now we need a way to shoot
        ## lets bind it to "spacebar".
        ## adding an event for it in Game loop

## FIRE ZE MISSILES
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < TOP_HEIGHT:
            self.kill()


###################################################
## Load all game images

background = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()

background = pygame.transform.scale(background, (GAME_WIDTH, GAME_HEIGHT))
background_rect = background.get_rect(topleft=(0, TOP_HEIGHT))
## ^^ draw this rect first 

player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)

bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()

meteor_images = []
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png', 
    'meteorBrown_med1.png', 
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    ## resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    ## player explosion
    filename2 = 'sonicExplosion0{}.png'.format(i)
    img2 = pygame.image.load(path.join(img_dir, filename2)).convert()
    img2.set_colorkey(BLACK)
    explosion_anim['player'].append(img2)

## load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


###################################################


###################################################
### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))
###################################################

## TODO: make the game music loop over again and again. play(loops=-1) is not working
# Error : 
# TypeError: play() takes no keyword arguments
#pygame.mixer.music.play()

#############################
## Game loop
running = True
menu_display = True
death_explosion = None

active_input = None
sidebar_btns = []
input_rects = []
input_text = ""

while running:
    if menu_display:
        main_menu()
        pygame.time.wait(3000)

        #Stop menu music
        pygame.mixer.music.stop()
        #Play the gameplay music
        try:
            pygame.mixer.music.load(
                path.join(sound_folder, "tgfcoder-FrozenJam-SeamlessLoop.ogg")
            )
            pygame.mixer.music.play(-1)     ## makes the gameplay sound in an endless loop
        except Exception:
            pass

        menu_display = False
        game_paused = False
        manual_mode = False

        ## group all the sprites together for ease of update
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)

        ## spawn a group of mob
        mobs = pygame.sprite.Group()
        for i in range(8):      ## 8 mobs
            # mob_element = Mob()
            # all_sprites.add(mob_element)
            # mobs.add(mob_element)
            newmob()

        ## group for bullets
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()


        # Reset metrics
        dda_metrics["total_mobs_spawned"] = 0
        dda_metrics["mobs_destroyed"] = 0
        dda_metrics["session_time_elapsed"] = 0
        dda_metrics["health"] = player.shield
        dda_metrics["lives"] = player.lives
        dda_metrics["gun_level"] = player.power
        dda_metrics["restart_count"] = restart_count
        dda_metrics["current_speed_mult"] = 1.0
        dda_metrics["current_spawn_delay"] = 1.5
        dda_metrics["current_mob_size"] = 1.0
        dda_metrics["fired_rules"] = []
        session_start_time = pygame.time.get_ticks()


        #### Score board variable
        score = 0
        death_explosion = None

    #1 Process input/events
    clock.tick(FPS)     ## will make the loop run at the same speed all the time
    for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
        if event.type == pygame.QUIT:
            running = False

        ## Press ESC to exit game
        if event.type == pygame.KEYDOWN:
            # -- NEW: Intercept typing if a text box is active --
            if active_input is not None:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Apply value and exit typing mode
                    if input_text.strip() != "":
                        try:
                            # Cast to the original type (int or float)
                            original_type = type(dda_metrics.get(active_input, 0))
                            dda_metrics[active_input] = original_type(input_text)
                        except ValueError:
                            pass
                    active_input = None
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1] # Delete last char
                elif event.key == pygame.K_ESCAPE:
                    active_input = None # Cancel typing
                else:
                    # Append numbers or decimals
                    if event.unicode.isnumeric() or event.unicode == ".":
                        input_text += event.unicode
            
            # -- Existing Keybinds (Only run if NOT typing in a box) --
            else:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # ## event for shooting the bullets
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         player.shoot()      ## we have to define the shoot()  function

                elif event.key == pygame.K_TAB:
                    game_paused = not game_paused
                elif event.key == pygame.K_m:
                    manual_mode = not manual_mode
                    if manual_mode:
                        game_paused = True
                elif event.key == pygame.K_p:
                    try:
                        engine.plot_graphs()
                    except Exception as e:
                        print(f"Plotting failed: {e}")

        # -- UPDATED: Mouse Clicks --
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and manual_mode:
            mx, my = event.pos
            clicked_box = False

            # 1. Check if an input box was clicked
            for rect, key in input_rects:
                if rect.collidepoint(mx, my):
                    active_input = key
                    input_text = str(dda_metrics.get(key, 0))
                    clicked_box = True
                    break
            
            if not clicked_box:
                # 2. If clicked elsewhere, save any pending typing and deselect
                if active_input is not None and input_text.strip() != "":
                    try:
                        original_type = type(dda_metrics.get(active_input, 0))
                        dda_metrics[active_input] = original_type(input_text)
                    except ValueError:
                        pass
                active_input = None

                # 3. Check if +/- buttons were clicked
                for r_minus, r_plus, key, lo, hi, step in sidebar_btns:
                    if r_minus.collidepoint(mx, my):
                        dda_metrics[key] = max(lo, dda_metrics[key] - step)
                    elif r_plus.collidepoint(mx, my):
                        dda_metrics[key] = min(hi, dda_metrics[key] + step)

    #2 Update
    if not game_paused:
        dda_metrics["session_time_elapsed"] = (pygame.time.get_ticks() - session_start_time) // 1000        
        dda_metrics["health"] = player.shield
        dda_metrics["lives"] = player.lives
        dda_metrics["gun_level"] = player.power
        dda_metrics["restart_count"] = restart_count

        fuzz_now = pygame.time.get_ticks()
        if fuzz_now - last_fuzzy_update > FUZZY_UPDATE_RATE:
            run_fuzzy() # Run Fuzzy twice a second
            last_fuzzy_update = fuzz_now

        all_sprites.update()


        ## check if a bullet hit a mob
        ## now we have a group of bullets and a group of mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
        ## as there will be no mob_elements left out 
        for hit in hits:
            score += 50 - hit.radius         ## give different scores for hitting big and small metoers
            random.choice(expl_sounds).play()
            # m = Mob()
            # all_sprites.add(m)
            # mobs.add(m)
            dda_metrics["mobs_destroyed"] += 1
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob()        ## spawn a new mob

        ## ^^ the above loop will create the amount of mob objects which were killed spawn again
        #########################

        ## check if the player collides with the mob
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
        for hit in hits:
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob()
            if player.shield <= 0:
                player_die_sound.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                # running = False     ## GAME OVER 3:D
                player.hide()
                player.lives -= 1
                player.shield = 100

        ## if the player hit a power up
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.powerup()

        ## if player died and the explosion has finished, end game
        if player.lives == 0 and death_explosion and not death_explosion.alive():
            # running = False
            restart_count += 1
            menu_display = True
            # pygame.display.update()
    else:
        if manual_mode:
            # 1. Sync manual UI overrides back into the actual Pygame entities
            player.shield = float(dda_metrics["health"])
            if player.shield <= 0:
                player.shield = float(1)

            player.lives = int(dda_metrics["lives"])

            player.power = int(dda_metrics["gun_level"])
            player.power_time = pygame.time.get_ticks()

            restart_count = int(dda_metrics["restart_count"])

            # 2. Run the fuzzy engine to crunch the new manual inputs live
            run_fuzzy()
            current_time_sec = float(dda_metrics.get("session_time_elapsed", 0))
            session_start_time = pygame.time.get_ticks() - int(current_time_sec * 1000)

    #3 Draw/render
    screen.fill(BLACK)

    # Game area (clipped so sprites don't bleed into top bar or plots)
    game_clip = pygame.Rect(0, TOP_HEIGHT, GAME_WIDTH, GAME_HEIGHT)
    screen.set_clip(game_clip)

    ## draw the stargaze.png image
    screen.blit(background, background_rect)

    all_sprites.draw(screen)

    # HUD inside game area
    draw_text(screen, str(score), 18, GAME_WIDTH / 2, TOP_HEIGHT + 10)
    draw_shield_bar(screen, 5, TOP_HEIGHT + 5, player.shield)

    # Draw lives
    draw_lives(screen, GAME_WIDTH - 150, TOP_HEIGHT + 5, player.lives, player_mini_img)

    if game_paused:
        pause_overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pause_overlay.set_alpha(120)
        pause_overlay.fill(BLACK)
        screen.blit(pause_overlay, (0, TOP_HEIGHT))
        draw_text(
            screen, "PAUSED", 36, GAME_WIDTH / 2, TOP_HEIGHT + GAME_HEIGHT // 2 - 20
        )

    screen.set_clip(None)

    # -- UPDATED: Top bar call --
    # Unpack both returned lists, and pass the active_input and input_text
    sidebar_btns, input_rects = fuzzy_ui.draw_top_bar(
        screen, dda_metrics, manual_mode, game_paused, GAME_WIDTH, TOP_HEIGHT, font_name,
        active_input, input_text
    )

    # Plot panel (right side, full height)
    current_vals = {
        "Mobs Killed": dda_metrics["mobs_destroyed"],
        "Time Elapsed": dda_metrics["session_time_elapsed"],
        "Health": dda_metrics["health"],
        "Lives": dda_metrics["lives"],
        "Gun Level": dda_metrics["gun_level"],
        "Restarts": dda_metrics["restart_count"],
        "Speed Mult": dda_metrics["current_speed_mult"],
        "Spawn Delay": dda_metrics["current_spawn_delay"],
        "Mob Size": dda_metrics["current_mob_size"],
    }

    plot_now = pygame.time.get_ticks()
    # If 500ms have passed OR we are changing values in manual mode.
    if plot_now - last_plot_update > PLOT_UPDATE_RATE or manual_mode:
        # 1. Clear our invisible cache canvas
        plot_surface.fill(BLACK) 
        
        # 2. Draw the heavy plots onto the cache canvas.
        fuzzy_ui.draw_plot_panel(
            plot_surface, mf_data, current_vals, 0, PLOT_WIDTH, HEIGHT, font_name
        )
        last_plot_update = plot_now

    # 3. "Stamp" the cached canvas onto the main screen exactly where it belongs
    screen.blit(plot_surface, (GAME_WIDTH, 0))


    ## Done after drawing everything to the screen
    pygame.display.flip()

pygame.quit()
