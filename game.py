import pygame
import random
import math
import os
import sys

# Initialize Pygame
pygame.init()

global playerStates, p1State, p2State, p1Building, p2Building, playerHeightPx, building_surface, buildings

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
WHITE = (255, 255, 255)
DARK_BLUE = (0, 0, 139)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
building_colors = [(171, 48, 31), (72, 171, 171), (170, 170, 170)]  # Red, Blue, Gray
window_colors = [(254, 248, 85), (85, 85, 85)]  # Light, Dark
playerStates = ['Waiting', 'Throw', 'Lose', 'Win', 'Dead']
CONFETTI_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]
p1State = playerStates[0]
p2State = playerStates[0]
p1Building = None
p2Building = None
playerHeightPx = 26
buildings = []
hasInitialized = False
playerLvl = 1 
currentAngle = ''
currentSpeed = ''
currentPlayer = 1
needThrowBanana = False
bananaCollided = False
banana_frame_index = 0
banana_frame_time = 0
has_collided = False
banana_out = False
banana_colide_pos_x, banana_colide_pos_y = None, None
draw_banana = True
banana_explosion_frame_time = 0
banana_explosion_frame_index = 0
need_throw_banana_animation = False
playerKilled = None
run_explosion_animation = False
p1_points = 0
p2_points = 0
kill_cool_down = 2
start_kill_cooldown = False
explosion_run = False
games = 0
start_game = False
starting_questions = True
questionsLvl = 1
current_name = ''
total_points = ''
end_game = False

# Animation timing variables
animation_delay = 0.8  # Time delay between frames in secondse
animation_timer = 0  # Timer to track animation progress
p1_frame_index = 0  # Current frame index for player 1
p2_frame_index = 0  # Current frame index for player 2


g = ''  # Gravitational acceleration
t = 0
playerNames = []

# Initialize the screen

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller bundle """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
building_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
building_surface.fill(DARK_BLUE)

retroFont = pygame.font.Font(resource_path('assets/font/font.ttf'), 12)

class ConfettiParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(5, 10)
        self.color = random.choice(CONFETTI_COLORS)
        self.speed = random.uniform(1, 5)
        self.direction = random.uniform(-1, 1)

    def update(self):
        self.y += self.speed
        self.x += self.direction
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))



# Functions to draw buildings
def draw_building(surface, x_pos, width, height, color):
    building_rect = pygame.Rect(x_pos, SCREEN_HEIGHT - height, width, height)
    pygame.draw.rect(surface, color, building_rect)
    draw_windows(surface, building_rect)
    buildings.append(building_rect)

def draw_windows(surface, building_rect):
    """Draws windows on the building."""
    window_width = 5
    window_height = 10
    for y in range(building_rect.top + 10, building_rect.bottom - 10, window_height + 7):
        for x in range(building_rect.left + 5, building_rect.right - 5, window_width + 7):
            window_color = random.choice(window_colors)
            pygame.draw.rect(surface, window_color, pygame.Rect(x, y, window_width, window_height))

def generate_buildings(surface):
    """Generates and draws buildings until the screen is filled."""
    x_pos = 0
    while x_pos < SCREEN_WIDTH:
        width = random.randint(50, 100)
        height = random.randint(100, 300)
        color = random.choice(building_colors)
        draw_building(surface, x_pos, width, height, color)
        x_pos += width + 2  # Adding space between buildings

def choose_players_pos():
    global p1Building, p2Building
    p1Building = random.choice(buildings[1:3])
    p2Building = random.choice(buildings[-3:-1])

def update_players(delta_time):
    global animation_timer, p1_frame_index, p2_frame_index, p1State, p2State

    # List of player images for different states
    player_images = {
        'Waiting': [pygame.image.load(resource_path('assets/img/Waiting.png')).convert_alpha()],
        'Throw': [pygame.image.load(resource_path(f'assets/img/Throw{i}.png')).convert_alpha() for i in range(1, 3)],
        'Lose': [pygame.image.load(resource_path(f'assets/img/Lose{i}.png')).convert_alpha() for i in range(1, 4)],
        'Win': [pygame.image.load(resource_path(f'assets/img/Win{i}.png')).convert_alpha() for i in range(1, 3)],
        'Dead': [pygame.image.load(resource_path('assets/img/Dead.png')).convert_alpha()],
    }
    # Update animation timer
    animation_timer += delta_time

    # Check if it's time to update the frame
    if animation_timer >= animation_delay:
        animation_timer -= animation_delay  # Reset the timer

        # Update frame index for both players if they are in a state that requires animation
        if p1State in ['Throw', 'Lose', 'Win']:
            p1_frame_index = (p1_frame_index + 1) % len(player_images[p1State])
        else:
            p1_frame_index = 0

        if p2State in ['Throw', 'Lose', 'Win']:
            p2_frame_index = (p2_frame_index + 1) % len(player_images[p2State])
        else:
            p2_frame_index = 0

    p1_frame_index = min(p1_frame_index, len(player_images[p1State]) - 1)
    p2_frame_index = min(p2_frame_index, len(player_images[p2State]) - 1)
    # Get the current image based on state and frame index
    p1_image = player_images[p1State][p1_frame_index]
    p2_image = player_images[p2State][p2_frame_index]

    # Position players on their buildings
    p1_rect = p1_image.get_rect()
    p1_rect.center = (p1Building.left + p1Building.width / 2, p1Building.top - playerHeightPx / 2)
    screen.blit(p1_image, p1_rect)

    p2_rect = p2_image.get_rect()
    p2_rect.center = (p2Building.left + p2Building.width / 2, p2Building.top - playerHeightPx / 2)
    screen.blit(p2_image, p2_rect)

def throw_info(playerTurn, inputLvl, angle, speed):
    global playerNames
    if angle is None:
        angle = ''
    if speed is None:
        speed = ''
    p1Nametext = retroFont.render(playerNames[0], True, WHITE)
    p2Nametext = retroFont.render(playerNames[1], True, WHITE)
    p2NameXPos = SCREEN_WIDTH - p2Nametext.get_width() - 10
    if p2NameXPos > 715:
        p2NameXPos = 715
    
    screen.blit(p1Nametext, (10, 10))
    screen.blit(p2Nametext, (p2NameXPos, 10))

    if playerTurn == 1:
        if inputLvl == 1:
            text = retroFont.render(f"Angle: {angle}", True, WHITE)
            screen.blit(text, (10, 30))
        elif inputLvl == 2:
            text = retroFont.render(f"Angle: {angle}", True, WHITE)
            screen.blit(text, (10, 30))
            text = retroFont.render(f"Speed: {speed}", True, WHITE)
            screen.blit(text, (10, 50))

    elif playerTurn == 2:
        if inputLvl == 1:
            text = retroFont.render(f"Angle: {angle}", True, WHITE)
            screen.blit(text, (p2NameXPos, 30))
        elif inputLvl == 2:
            text = retroFont.render(f"Angle: {angle}", True, WHITE)
            screen.blit(text, (p2NameXPos, 30))
            text = retroFont.render(f"Speed: {speed}", True, WHITE)
            screen.blit(text, (p2NameXPos, 50))

def get_banana_pos(initial_pos, speed, angle, t):
    """Calculates the position of the banana at time t."""
    # Convert angle to radians
    ## Turn angle and speed into integers and for player 1, angle is negative
    speed = int(speed)
    angle = int(angle)
    if currentPlayer == 2:
        angle = 180 - angle
    angle_rad = math.radians(angle)
    x = initial_pos[0] + speed * math.cos(angle_rad) * t
    y = initial_pos[1] - (speed * math.sin(angle_rad) * t - 0.5 * g * t**2)
    return x, y

def throw_banana():
    global t, banana_frame_time, banana_frame_index, has_collided, banana_out, banana_colide_pos_x, banana_colide_pos_y, draw_banana, p1State, p2State, objHit
    if draw_banana:
        if currentPlayer == 1:
            banana_pos = p1Building.left + p1Building.width / 2, p1Building.top - playerHeightPx - 10
            p1State = playerStates[1]
        if currentPlayer == 2:
            banana_pos = p2Building.left + p2Building.width / 2, p2Building.top - playerHeightPx - 10
            p2State = playerStates[1]
            
        speed = currentSpeed
        angle = currentAngle 
        banana_x, banana_y = get_banana_pos(banana_pos, speed, angle, t)

        banana_images = {
            'Bananas': [pygame.image.load(resource_path(f'assets/img/Banana{i}.png')).convert_alpha() for i in range(1, 4)],
        }

        if banana_frame_time >= 0.1:
            banana_frame_time -= 0.1
            banana_frame_index = (banana_frame_index + 1) % len(banana_images['Bananas'])
        banana_img = banana_images['Bananas'][banana_frame_index]
        banana_rect = banana_img.get_rect()
        banana_rect.center = (banana_x, banana_y)
        screen.blit(banana_img, banana_rect)

        t += 0.03
        banana_frame_time += delta_time


        if check_collision((banana_x, banana_y)):
            has_collided = True
            draw_banana = False
            banana_colide_pos_x, banana_colide_pos_y = banana_x, banana_y
            p1State = playerStates[0]
            p2State = playerStates[0]
            objHit = 'building'
        if banana_y > SCREEN_HEIGHT or banana_x < 0 or banana_x > SCREEN_WIDTH:
            banana_out = True
            draw_banana = False
            p1State = playerStates[0]
            p2State = playerStates[0]
        if has_banana_hit_player(banana_x, banana_y):
            has_collided = True
            draw_banana = False
            banana_colide_pos_x, banana_colide_pos_y = banana_x, banana_y
            p1State = playerStates[0]
            p2State = playerStates[0]
            objHit = 'player'

def check_collision(banana_pos):
    """Checks if the banana has collided with a building."""
    banana_rect = pygame.Rect(banana_pos[0], banana_pos[1], 5, 5)
    for building in buildings:
        if building.colliderect(banana_rect):
            return True
    return False

def banana_explosion_animation():
    global banana_explosion_frame_time, banana_explosion_frame_index, banana_colide_pos_x, banana_colide_pos_y, playerKilled, p1State, p2State, objHit, run_explosion_animation, start_kill_cooldown, explosion_run
    banana_explosion_images = {
        'Explosion': [pygame.image.load(resource_path(f'assets/img/Explosion{i}.png')).convert_alpha() for i in range(1, 7)],
    }
    
    if objHit == 'building':

        if banana_explosion_frame_index == 1:
            pygame.draw.ellipse(building_surface, DARK_BLUE, pygame.Rect(banana_colide_pos_x-12.5, banana_colide_pos_y-7.5, 25, 15))
        

        if banana_explosion_frame_time >= 0.1:
            banana_explosion_frame_time -= 0.1
            banana_explosion_frame_index = (banana_explosion_frame_index + 1) % len(banana_explosion_images['Explosion'])
        banana_explosion_img = banana_explosion_images['Explosion'][banana_explosion_frame_index]
        banana_explosion_rect = banana_explosion_img.get_rect()
        banana_explosion_rect.center = (banana_colide_pos_x, banana_colide_pos_y)
        screen.blit(banana_explosion_img, banana_explosion_rect)
        banana_explosion_frame_time += delta_time
        if banana_explosion_frame_index == 5:
            change_turn()
    elif objHit == 'player':
        if banana_explosion_frame_index == 1:
            pygame.draw.ellipse(building_surface, DARK_BLUE, pygame.Rect(banana_colide_pos_x-50, banana_colide_pos_y-15, 100, 60))
        
        if playerKilled == 1:
            if not explosion_run:
                p1State = playerStates[2]
            p2State = playerStates[3]
            if p1_frame_index == 2:
                run_explosion_animation = True
        elif playerKilled == 2:
            if not explosion_run:
                p2State = playerStates[2]
            p1State = playerStates[3]
            if p2_frame_index == 2:
                run_explosion_animation = True
        
        if run_explosion_animation:

            if playerKilled == 1:
                p1State = playerStates[4]


            elif playerKilled == 2:
                p2State = playerStates[4]

            if banana_explosion_frame_time >= 0.1:
                banana_explosion_frame_time -= 0.1
                banana_explosion_frame_index = (banana_explosion_frame_index + 1) % len(banana_explosion_images['Explosion'])

            banana_explosion_img = banana_explosion_images['Explosion'][banana_explosion_frame_index]
            banana_explosion_rect = banana_explosion_img.get_rect()

            if playerKilled == 1:
                banana_explosion_rect.center = (p1Building.left + p1Building.width / 2, p1Building.top - playerHeightPx / 2)
                if banana_explosion_frame_index == 2:
                    pygame.draw.ellipse(building_surface, DARK_BLUE, pygame.Rect((p1Building.left + p1Building.width / 2)-50, ( p1Building.top - playerHeightPx / 2)-30, 100, 60))
            elif playerKilled == 2:
                banana_explosion_rect.center = (p2Building.left + p2Building.width / 2, p2Building.top - playerHeightPx / 2)
                if banana_explosion_frame_index == 2:
                    pygame.draw.ellipse(building_surface, DARK_BLUE, pygame.Rect((p2Building.left + p2Building.width / 2)-50, ( p2Building.top - playerHeightPx / 2)-30, 100, 60))

            screen.blit(banana_explosion_img, banana_explosion_rect)
            banana_explosion_frame_time += delta_time

            if banana_explosion_frame_index == 5:
                run_explosion_animation = False   
                start_kill_cooldown = True
                explosion_run = True    
            
def change_turn():
    global currentPlayer, currentAngle, currentSpeed, playerLvl, needThrowBanana, bananaCollided, banana_frame_index,banana_frame_time, has_collided, banana_out, banana_colide_pos_x, banana_colide_pos_y, draw_banana, banana_explosion_frame_time, banana_explosion_frame_index, need_throw_banana_animation, t, p1State, p2State, playerKilled, run_explosion_animation, objHit, kill_cool_down, start_kill_cooldown, explosion_run
    if currentPlayer == 1:
        currentPlayer = 2
    else:
        currentPlayer = 1
    currentAngle = ''
    currentSpeed = ''
    playerLvl = 1
    needThrowBanana = False
    bananaCollided = False
    banana_frame_index = 0
    banana_frame_time = 0
    has_collided = False
    banana_out = False
    banana_colide_pos_x, banana_colide_pos_y = None, None
    draw_banana = True
    banana_explosion_frame_time = 0
    banana_explosion_frame_index = 0
    need_throw_banana_animation = False
    t = 0
    p1State = playerStates[0]
    p2State = playerStates[0]
    playerKilled = None
    run_explosion_animation = False
    objHit = None
    kill_cool_down = 2
    start_kill_cooldown = False
    explosion_run = False

def has_banana_hit_player(banana_x,banana_y):
    global playerKilled, p1_points, p2_points
    p1_rect = pygame.Rect(p1Building.left, p1Building.top - playerHeightPx, p1Building.width, playerHeightPx)
    p2_rect = pygame.Rect(p2Building.left, p2Building.top - playerHeightPx, p2Building.width, playerHeightPx)
    if p1_rect.collidepoint(banana_x, banana_y):
        playerKilled = 1
        p2_points += 1
        return True
    if p2_rect.collidepoint(banana_x, banana_y):
        playerKilled = 2
        p1_points += 1
        return True
    return False

def initialize_game():
    generate_buildings(building_surface)
    choose_players_pos()

def handle_key_event(event):
    global playerLvl, currentAngle, currentSpeed, needThrowBanana

    if event.key == pygame.K_BACKSPACE:
        if playerLvl == 1:
            currentAngle = currentAngle[:-1]
        elif playerLvl == 2:
            currentSpeed = currentSpeed[:-1]
        return

    if event.key == pygame.K_RETURN:
        if playerLvl == 1:
            currentAngle = currentAngle or '0'
            playerLvl = 2
        elif playerLvl == 2:
            currentSpeed = currentSpeed or '0'
            needThrowBanana = True
            playerLvl = None
        return

    if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
        if playerLvl == 1 and len(currentAngle) < 2:
            currentAngle += pygame.key.name(event.key)
        elif playerLvl == 2 and len(currentSpeed) < 2:
            currentSpeed += pygame.key.name(event.key)

def display_score():
    global p1_points, p2_points
    score_text = retroFont.render(f"{p1_points}>Score<{p2_points}", True, WHITE)
    score_x_pos = (SCREEN_WIDTH - score_text.get_width()) / 2
    score_y_pos = SCREEN_HEIGHT - score_text.get_height() - 10
    score_bg_rect = pygame.Rect(score_x_pos, score_y_pos, score_text.get_width(), score_text.get_height())
    pygame.draw.rect(screen, DARK_BLUE, score_bg_rect)
    screen.blit(score_text, (score_x_pos, score_y_pos))

def a_win():
    global p1Building, p2Building, buildings, games, end_game, winner, playerNames, p1_points, p2_points, total_points, start_game
    
    games += 1
    building_surface.fill(DARK_BLUE)
    buildings = []
    initialize_game()
    change_turn()
    if games >= total_points:
        end_game = True
        start_game = False
        if p1_points > p2_points:
            winner = playerNames[0]
        elif p1_points < p2_points:
            winner = playerNames[1]
        else:
            winner = 'Tie ... :('
 
def handle_question_input(event):

    global questionsLvl, current_name, total_points, playerNames, g, starting_questions, start_game
    if questionsLvl == 1:
        if event.key == pygame.K_RETURN:
            if current_name == '':
                current_name = 'Player 2'
            playerNames.append(current_name)
            questionsLvl += 1
            current_name = ''
        elif event.key == pygame.K_BACKSPACE:
            current_name = current_name[:-1]
        else:
            current_name += event.unicode
    elif questionsLvl == 2:
        if event.key == pygame.K_RETURN:
            if current_name == '':
                current_name = 'Player 2'
            playerNames.append(current_name)
            questionsLvl += 1
            current_name = ''
        elif event.key == pygame.K_BACKSPACE:
            current_name = current_name[:-1]
        else:
            current_name += event.unicode
    elif questionsLvl == 3:
        if event.key == pygame.K_RETURN:
            if total_points == '':
                total_points = 3
            else:
                total_points = int(total_points)
            questionsLvl += 1
        elif event.key == pygame.K_BACKSPACE:
            total_points = total_points[:-1]
        elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                     pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
            total_points = str(total_points)
            if len(total_points) < 2:
                total_points = str(total_points)
                total_points += str(event.unicode)
    elif questionsLvl == 4:
        # Have it so it can hanle decimals
        if event.key == pygame.K_RETURN:
            if g == '':
                g = 9.8
            else:
                g = float(g)
            questionsLvl += 1
        elif event.key == pygame.K_BACKSPACE:
            g = g[:-1]
        elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                        pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_PERIOD]:
                g = str(g)
                if len(g) < 3:
                    g = str(g)
                    g += str(event.unicode)
    elif questionsLvl == 5:
        if event.key == pygame.K_p or event.key == pygame.K_RETURN:
            starting_questions = False
            start_game = True              

def check_if_name_exist(player):
    global playerNames, current_name
    try:
        name = playerNames[player]
        return name
    except:
        name = current_name
        return name

# def play_sound(sound):
#     sounds = {
#         'throw': 'assets/sound/throw.wav',
#         'explosion': 'assets/sound/explosion.wav',
#         'collision': 'assets/sound/collision.wav',
#         'out_of_bounds': 'assets/sound/out_of_bounds.wav',
#         'win': 'assets/sound/win.wav',
#         'player_hit': 'assets/sound/player_hit.wav',                           
#     }
#     if prev_sound != sound:
#         pygame.mixer.music.load(sounds[sound])
#         pygame.mixer.music.play()
#         prev_sound = sound
    
# Main game loop
running = True
last_time = pygame.time.get_ticks()
confetti_particles = [ConfettiParticle() for _ in range(100)]

while running:
    current_time = pygame.time.get_ticks()
    delta_time = (current_time - last_time) / 1000.0  # Convert milliseconds to seconds
    last_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if start_game:
                handle_key_event(event)
            if starting_questions:
                handle_question_input(event)

    if starting_questions:
        screen.fill(BLACK)
        if questionsLvl >= 1:
            question_p1_name = retroFont.render(
                f"Name of Player 1 (Default = 'Player1'): {check_if_name_exist(0)}", True, WHITE)
            screen.blit(question_p1_name, (SCREEN_WIDTH/2 - 305/2, 40))
        if questionsLvl >= 2:
            question_p2_name = retroFont.render(
                f"Name of Player 2 (Default = 'Player2'): {check_if_name_exist(1)}", True, WHITE)
            screen.blit(question_p2_name, (SCREEN_WIDTH/2 - 305/2, 70))
        if questionsLvl >= 3:
            question_how_meany_points = retroFont.render(
                f"How many total points (Deafault = 3)?: {str(total_points)}", True, WHITE)
            screen.blit(question_how_meany_points, (SCREEN_WIDTH/2 - 297/2, 100))
        if questionsLvl >= 4:
            question_gravity = retroFont.render(
                f"Gravity in Meters/Sec (Earth = 9.8)?: {str(g)}", True, WHITE)
            screen.blit(question_gravity, (SCREEN_WIDTH/2 - 293/2, 130))

        if questionsLvl >= 5:
            question_start_game1 = retroFont.render("---------------", True, WHITE)
            screen.blit(question_start_game1, (SCREEN_WIDTH/2 - 136/2, 175))
            question_start_game2 = retroFont.render("P = Play Game", True, WHITE)
            screen.blit(question_start_game2, (SCREEN_WIDTH/2 - 113/2, 215))
            question_start_game3 = retroFont.render("Your Choice?", True, WHITE)
            screen.blit(question_start_game3, (SCREEN_WIDTH/2 - 106/2, 275))

    if start_game:
        if not hasInitialized:
            initialize_game()
            hasInitialized = True

        screen.fill(DARK_BLUE)
        screen.blit(building_surface, (0, 0))

        update_players(delta_time)
        throw_info(currentPlayer, playerLvl, currentAngle, currentSpeed)
        if has_collided:
            banana_explosion_animation()
        if banana_out:
            change_turn()
        if needThrowBanana:
            throw_banana()

        display_score()

        if start_kill_cooldown:
            kill_cool_down = kill_cool_down - delta_time
            if kill_cool_down <= 0:
                a_win()

    if end_game:
        screen.fill(BLACK)

        end_game_text = retroFont.render("The Winner is", True, WHITE)
        screen.blit(end_game_text, (SCREEN_WIDTH/2 - end_game_text.get_width()/2, SCREEN_HEIGHT/2 - end_game_text.get_height()/2))
        end_game_text2 = retroFont.render(f"{winner}", True, WHITE)
        screen.blit(end_game_text2, (SCREEN_WIDTH/2 - end_game_text2.get_width()/2, SCREEN_HEIGHT/2 - end_game_text2.get_height()/2 + 20))
        for particle in confetti_particles:
            particle.update()
            particle.draw(screen)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()