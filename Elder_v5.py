import pygame
from pygame.sprite import LayeredUpdates
import math
import requests

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1100, 900
WHITE = (255, 255, 255)
GREY = (180, 180, 180)
BLACK = (0, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elder")

class Game(object):
    def __init__(self):
        self.online = False
        self.turn = 'red'
        self.clock = pygame.time.Clock()
        self.state = 'init'
        self.select = False
        self.board = None
        self.hex_r = 0
        self.offset = 0
        self.selected_hex = (0,0)
        self.control = ['none','none','none','none','none','none','none','none','none']
        self.territory_tiles = [
            ['6, 0.0','6, 1.0','6, 2.0','5, 0.5','5, 1.5','7, 0.5','7, 1.5'],
            ['9, 1.5','9, 2.5','9, 3.5','8, 2.0','8, 3.0','10, 2.0','10, 3.0'],
            ['9, 4.5','9, 5.5','9, 6.5','8, 5.0','8, 6.0','10, 5.0','10, 6.0'],
            ['6, 6.0','6, 7.0','6, 8.0','5, 6.5','5, 7.5','7, 6.5','7, 7.5'],
            ['3, 4.5','3, 5.5','3, 6.5','2, 5.0','2, 6.0','4, 5.0','4, 6.0'],
            ['3, 1.5','3, 2.5','3, 3.5','2, 2.0','2, 3.0','4, 2.0','4, 3.0'],
            ['6, 3.0','6, 4.0','6, 5.0','5, 3.5','5, 4.5','7, 3.5','7, 4.5'],
            ['1, 2.5','0, 3.0','1, 3.5','0, 4.0','1, 4.5','0, 5.0','1, 5.5'],
            ['11, 2.5','12, 3.0','11, 3.5','12, 4.0','11, 4.5','12, 5.0','11, 5.5']
            ]
        self.piece_weights = {
            'Elder': 100,
            'Hawk':10,
            'Chief':1,
            'Spirit':1,
            'Warrior':1
        }

        self.green_hex = pygame.image.load("HexGreen.png")
        self.blue_hex = pygame.image.load("HexBlue.png")
        self.brown_hex = pygame.image.load("HexBrown.png")
        self.yellow_hex = pygame.image.load("HexYellow.png")
        self.white_hex = pygame.image.load("HexWhite.png")
        self.red_hex = pygame.image.load("HexRed.png")
        self.dullgreen_hex = pygame.image.load("HexDullGreen.png")
        self.red_control = pygame.image.load("RedControl.png")
        self.red_side_control = pygame.image.load("RedSideControl.png")
        self.green_control = pygame.image.load("GreenControl.png")
        self.green_side_control = pygame.image.load("GreenSideControl.png")
        self.neutral_control = pygame.image.load("NeutralControl.png")
        self.neutral_side_control = pygame.image.load("NeutralSideControl.png")
        self.red_wins = pygame.image.load("RedWins.png")
        self.green_wins = pygame.image.load("GreenWins.png")

        self.all_sprites = []

    def _board_shape_logic(self, x, y):
        boarderTiles = ['0, 0.0', '2, 0.0', '4, 0.0', '8, 0.0', '10, 0.0', '12, 0.0',
                    '1, 0.5', '3, 0.5', '9, 0.5', '11, 0.5', 
                    '0, 1.0', '2, 1.0', '10, 1.0', '12, 1.0',
                    '1, 1.5', '11, 1.5',
                    '0, 2.0', '12, 2.0',
                    '0, 6.0', '12, 6.0',
                    '1, 6.5', '11, 6.5',
                    '0, 7.0', '2, 7.0', '10, 7.0', '12, 7.0',
                    '1, 7.5', '3, 7.5', '9, 7.5', '11, 7.5',
                    '0, 8.0', '2, 8.0', '4, 8.0', '8, 8.0', '10, 8.0', '12, 8.0']
        
        nonIslandTiles = [
            '4, 1.0', '8, 1.0',
            '4, 4.0', '8, 4.0',
            '4, 7.0', '8, 7.0']
        
        outerIslandTiles = [
            '1, 2.5', '11, 2.5',
            '0, 3.0', '12, 3.0',
            '1, 3.5', '11, 3.5',
            '0, 4.0', '12, 4.0',
            '1, 4.5', '11, 4.5',
            '0, 5.0', '12, 5.0',
            '1, 5.5', '11, 5.5']
        
        waterTiles = ['5, 2.5', '7, 2.5',
                    '2, 4.0', '10, 4.0',
                    '5, 5.5', '7, 5.5']

        if str(x)+', '+str(y) in waterTiles:
            color = 'blue'
        elif str(x)+', '+str(y) in nonIslandTiles:
            color = 'brown'
        elif str(x)+', '+str(y) in boarderTiles:
            color = 'empty'
        elif str(x)+', '+str(y) in outerIslandTiles:
            color = 'dullgreen'
        else:
            color = 'green'
        return color

    def generate_board_shape(self):
        board_width = 13
        board_height = 9

        grid = []

        for y in range(0, board_height):
            for x in range(0, board_width):
                color = self._board_shape_logic(x, y+((x%2)*.5))
                if color != 'empty':
                    space = {'x':x,'y':y+((x%2)*.5),
                            'centroid':(0,0),
                            'type':color,
                            'contains':'',
                            'selected':False,
                            'highlighted':False,
                            'territory':None}
                    coords_str = '{0}, {1}'.format(space['x'], space['y'])
                    for i, territory in enumerate(self.territory_tiles):
                        for tile in territory:
                            if tile == coords_str:
                                space['territory'] = i
                    grid.append(space)
        
        self.board = grid
        self.state = 'running'

    def lookup_space(self, x, y):
        for i, space in enumerate(self.board):
                if space['x'] == x and space['y'] == float(y):
                    return space

    def set_space_value(self, x, y, key, value):
        for i, space in enumerate(self.board):
            if space['x'] == x and space['y'] == float(y):
                self.board[i][key] = value

    def _render_text(self, centroid, text):
        font = pygame.font.Font('freesansbold.ttf', 24)
        rendered_text = font.render(text, True, BLACK)

        textRect = rendered_text.get_rect()
        textRect.center = centroid

        return rendered_text, textRect

    def _draw_hexagon(self, screen, space, hex, piece=None):
        """ Draw a hexagon at (x, y) with a given size """
        hex_pos = ((space['x']*self.hex_r)+self.offset, (space['y']*self.hex_r*1.2)+self.offset)
        self.all_sprites.append((hex, hex_pos))
        if piece:
            self.all_sprites.append((piece, hex_pos))

        '''
        else:
            text, textRect = self._render_text(space['centroid'], '{0},{1}'.format(chr(int(space['x'])+65), space['y']))
            text.set_alpha(60)
            self.all_sprites.append((text, textRect))
        #'''

    def _draw_control_lights(self):
        for i, territory in enumerate(self.control):
            if i < 7:
                if territory == 'red':
                    control_img = self.red_control
                elif territory == 'green':
                    control_img = self.green_control
                else:
                    control_img = self.neutral_control
                target_tile_str = self.territory_tiles[i][1]
                space = self.lookup_space(int(target_tile_str.split(',')[0]),float(target_tile_str.split(',')[1]))
                self.all_sprites.append((control_img, (space['centroid'][0]-116,space['centroid'][1]-110)))
            else:
                if territory == 'red':
                    control_img = self.red_side_control
                elif territory == 'green':
                    control_img = self.green_side_control
                else:
                    control_img = self.neutral_side_control
                self.all_sprites.append((control_img, (25+((i-7)*890),300)))

    def draw(self, screen):
        """ Draw the hexagonal board """
        screen.fill(BLACK)
        self._draw_control_lights()

        for i, space in enumerate(self.board):
            if space['contains']:
                piece = pygame.image.load(space['contains']+".png")
            else:
                piece = None
            if space['y'] == 8.5:
                pass
            else:
                self.board[i]['centroid'] = ((space['x']*self.hex_r)+(self.offset*3)+5, (space['y']*self.hex_r*1.2)+(self.offset*3))
                if space['selected']:
                    self._draw_hexagon(screen, space, self.white_hex, piece)
                elif space['highlighted']:
                    if self.board[i]['contains']:
                        self._draw_hexagon(screen, space, self.red_hex, piece)
                    else:
                        self._draw_hexagon(screen, space, self.yellow_hex, piece)
                else:
                    if space['type'] == 'green':
                        self._draw_hexagon(screen, space, self.green_hex, piece)
                    elif space['type'] == 'dullgreen':
                        self._draw_hexagon(screen, space, self.dullgreen_hex, piece)
                    elif space['type'] == 'blue':
                        self._draw_hexagon(screen, space, self.blue_hex, piece)
                    elif space['type'] == 'brown':
                        self._draw_hexagon(screen, space, self.brown_hex, piece)

        if self.state == 'green win':
            self.all_sprites.append((self.green_wins, (100,300)))
        elif self.state == 'red win':
            self.all_sprites.append((self.red_wins, (130,300)))

        screen.blits(blit_sequence=self.all_sprites)

    def deselect_all(self):
        for i, space in enumerate(self.board):
            self.board[i]['selected'] = False
            self.board[i]['highlighted'] = False
        return self.board

    def highlight(self, pos):
        for i, space in enumerate(self.board):
            if abs(space['centroid'][0]-pos[0]) < (self.hex_r/2) and abs(space['centroid'][1]-pos[1]) < (self.hex_r/2):
                if self.turn in space['contains'].lower():
                    if space['selected']:
                        self.board[i]['selected'] = False
                        self.board = self.deselect_all()
                        self.select = False
                        break
                    else:
                        self.board[i]['selected'] = True
                        if 'elder' in self.board[i]['contains'].lower():
                            self.elder_moves(space)
                        elif 'chief' in self.board[i]['contains'].lower():
                            self.chief_moves(space)
                        elif 'hawk' in self.board[i]['contains'].lower():
                            self.hawk_moves(space)
                        elif 'warrior' in self.board[i]['contains'].lower():
                            self.warrior_moves(space)
                        elif 'spirit' in self.board[i]['contains'].lower():
                            self.spirit_moves(space)
                        self.select = True
                        self.selected_hex = (space['x'],space['y'])
                        break

    def elder_moves(self, elder_space):
        # find possible double steps
        possible_jumps = [
            (elder_space['x']+2, elder_space['y']+1),
            (elder_space['x']+2, elder_space['y']-1),
            (elder_space['x']-2, elder_space['y']+1),
            (elder_space['x']-2, elder_space['y']-1),
            (elder_space['x'], elder_space['y']+2),
            (elder_space['x'], elder_space['y']-2),
        ]
        for i, space in enumerate(self.board):
            if space['type'] != 'blue' and self.turn not in space['contains'].lower():
                if space['contains'] == '' or 'Elder' in space['contains']:
                    x_dir = space['x']-elder_space['x']
                    y_dir = space['y']-elder_space['y']

                    # Single step move
                    if abs(x_dir) <= 1 and abs(y_dir) <= 1:
                        self.board[i]['highlighted'] = True

                    # Double step move
                    elif (space['x'], space['y']) in possible_jumps:
                        passing_space = self.lookup_space(space['x']-x_dir/2, space['y']-y_dir/2)
                        if passing_space:
                            if passing_space['type'] != 'blue' and not passing_space['contains']:
                                self.board[i]['highlighted'] = True
        self.set_space_value(elder_space['x'], elder_space['y'], 'highlighted', False)

    def hawk_moves(self, hawk_space):
        # find possible double steps
        possible_jumps = [
            (hawk_space['x']+2, hawk_space['y']+1),
            (hawk_space['x']+2, hawk_space['y']-1),
            (hawk_space['x']-2, hawk_space['y']+1),
            (hawk_space['x']-2, hawk_space['y']-1),
            (hawk_space['x'], hawk_space['y']+2),
            (hawk_space['x'], hawk_space['y']-2),
        ]
        for i, space in enumerate(self.board):
            if self.turn not in space['contains'].lower():
                x_dir = space['x']-hawk_space['x']
                y_dir = space['y']-hawk_space['y']

                # Single step move
                if abs(x_dir) <= 1 and abs(y_dir) <= 1:
                    if not space['contains']:
                        self.board[i]['highlighted'] = True

                # Double step move
                elif (space['x'], space['y']) in possible_jumps:
                    if 'Elder' not in space['contains']:
                        self.board[i]['highlighted'] = True
        
        self.set_space_value(hawk_space['x'], hawk_space['y'], 'highlighted', False)

    def chief_moves(self, chief_space):
        for i, space in enumerate(self.board):
            if space['type'] != 'blue' and self.turn not in space['contains'].lower():
                x_dir = space['x']-chief_space['x']
                y_dir = space['y']-chief_space['y']

                # Single step move
                if abs(x_dir) <= 1 and abs(y_dir) <= 1:
                    self.board[i]['highlighted'] = True

                # Island Hop move
                if space['territory']:
                    if '{0}, {1}'.format(space['x'], space['y']) == self.territory_tiles[space['territory']][1]:
                        for tile in self.territory_tiles[space['territory']]:
                            contains = self.lookup_space(int(tile.split(', ')[0]), float(tile.split(', ')[1]))['contains']
                            if f'elder_{self.turn}' == contains.lower():
                                self.board[i]['highlighted'] = True
                                break

        self.set_space_value(chief_space['x'], chief_space['y'], 'highlighted', False)

    def warrior_moves(self, warrior_space):
        first_step_spaces = []
        for i, space in enumerate(self.board):
            if space['type'] != 'blue' and self.turn not in space['contains'].lower():
                x_dir = space['x']-warrior_space['x']
                y_dir = space['y']-warrior_space['y']

                # Single step move
                if abs(x_dir) <= 1 and abs(y_dir) <= 1:
                    if 'Elder' not in space['contains']:
                        self.board[i]['highlighted'] = True
                        if not space['contains']:
                            first_step_spaces.append(self.board[i])

        # Second step move
        for prev_space in first_step_spaces:
            for i, space in enumerate(self.board):
                if space['type'] != 'blue' and self.turn not in space['contains'].lower():
                    x_dir = space['x']-prev_space['x']
                    y_dir = space['y']-prev_space['y']

                    if abs(x_dir) <= 1 and abs(y_dir) <= 1:
                        if 'Elder' not in space['contains']:
                            self.board[i]['highlighted'] = True

        self.set_space_value(warrior_space['x'], warrior_space['y'], 'highlighted', False)

    def spirit_moves(self, spirit_space):
        for dir in ((0,-1),(1,-.5),(1,.5),(0,1),(-1,.5),(-1,-.5)):
            new_x = spirit_space['x']
            new_y = spirit_space['y']
            blocked = False
            while blocked is False:
                new_x += dir[0]
                new_y += dir[1]
                space = self.lookup_space(new_x, new_y)
                if space:
                    if space['type'] == 'blue' or space['contains']:
                        if space['contains'] and self.turn not in space['contains'].lower():
                            if 'Elder' not in space['contains']:
                                self.set_space_value(new_x, new_y, 'highlighted', True)
                        blocked = True
                    else:
                        self.set_space_value(new_x, new_y, 'highlighted', True)
                else:
                    blocked = True
        
        self.set_space_value(spirit_space['x'], spirit_space['y'], 'highlighted', False)

    def make_move(self, pos):
        for i, space in enumerate(self.board):
            if abs(space['centroid'][0]-pos[0]) < (self.hex_r/2) and abs(space['centroid'][1]-pos[1]) < (self.hex_r/2):
                if space['highlighted']:
                    piece = self.lookup_space(self.selected_hex[0], self.selected_hex[1])['contains']
                    self.set_space_value(self.selected_hex[0], self.selected_hex[1], 'contains', '')
                    self.board[i]['contains'] = piece
                    if self.turn == 'red':
                        self.turn = 'green'
                    else:
                        self.turn = 'red'
        self.deselect_all()
        self.select = False
        self.eval_control()

    def eval_control(self):
        side_control = ['none', 'none']
        for i in range(0, 9):
            red_weight = 0
            green_weight = 0
            for tile in self.territory_tiles[i]:
                space = self.lookup_space(int(tile.split(', ')[0]), float(tile.split(', ')[1]))
                if space['contains'] != '':
                    piece = space['contains']
                    if piece.split('_')[1] == 'Red':
                        red_weight += self.piece_weights[piece.split('_')[0]]
                    elif piece.split('_')[1] == 'Green':
                        green_weight += self.piece_weights[piece.split('_')[0]]
                    else:
                        pass
            
            if red_weight > green_weight:
                if i < 7:
                    self.control[i] = 'red'
                else:
                    side_control[i-7] = 'red'
            elif green_weight > red_weight:
                if i < 7:
                    self.control[i] = 'green'
                else:
                    side_control[i-7] = 'green'
            else:
                self.control[i] = 'none'

        if side_control == ['red', 'red']:
            self.control[7] = 'red'
            self.control[8] = 'red'
        elif side_control == ['green', 'green']:
            self.control[7] = 'green'
            self.control[8] = 'green'

    def check_win(self):
        if self.control[:7].count('red') + (self.control[7:].count('red')//2) > 4:
            print("Red wins!")
            self.state = 'red win'
            return True
        elif self.control[:7].count('green') + (self.control[7:].count('green')//2) > 4:
            print("Green wins!")
            self.state = 'green win'
            return True
        else:
            return False

    def run(self):
        while self.state == 'running':
            self.clock.tick(15)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = 'stop'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.select:
                        self.make_move(event.pos)
                        if self.online:
                            response = requests.post('https://srgarlick96.pythonanywhere.com/setboard', json={"board":game.board})
                            if response.status_code == 200:
                                print("Response from server:", response.json())
                                self.board = response.json()["board"]
                            else:
                                print("Error:", response.status_code, response.json())
                    else:
                        self.highlight(event.pos)
            if self.state not in ['green win', 'red win']:
                self.check_win()
            self.draw(screen)
            pygame.display.flip()

class Menu(object):
    def __init__(self):
        self.curr_menu = 'Main'
        self.prev_menu = ''
        self.menu_map = {'Main':{'Play Local':'Button:StartLocal',
                                 'Play Online':'Button:Navigate'},
                         'Play Online':{'Create Game':'Button:CreateGame',
                                        'Join Game':'Button:Navigate',
                                        'Back':'Button:Back'}, 
                         'Join Game':{'Enter Game Id':'TextBox:GameId',
                                      'Join Game':'Button:JoinGame'}
                        }
        self.all_sprites = []
        self.hover = None
        self.action = None
        self.state = 'run'
        self.clock = pygame.time.Clock()
        self.cursor_x = 0
        self.cursor_y = 0
        self.game_code = ''
        self.enter_text = False
        self.text = ''

        self.menu_header = pygame.image.load("ElderLogo.png")
        self.font = pygame.font.Font('freesansbold.ttf', 34)

    def __del__(self):
        self.all_sprites = []
        #self._draw(screen)
        pygame.display.flip()

    def run(self):
        while self.state == 'run':
            #self.clock.tick(5)
            self._display_menu(screen)

            self.cursor_x, self.cursor_y = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = 'stop'
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.hover:
                        print(self.action)
                        if self.action == 'Navigate':
                            self.prev_menu = self.curr_menu
                            self.curr_menu = self.hover
                        elif self.action == 'Back':
                            self.curr_menu = self.prev_menu
                        elif self.action == 'StartLocal':
                            print('starting game')
                            self.state = 'run game'
                        self.hover = None
                        self.action = None
            pygame.display.flip()
        
        if self.state == 'run game':
            return Game()
        
    def _display_menu(self, screen):
        screen.fill(BLACK)
        self.all_sprites = [(self.menu_header, (350, 100))]

        count = 0
        for i, option in enumerate(self.menu_map[self.curr_menu].keys()):
            if self.menu_map[self.curr_menu][option].split(':')[0] == 'Button':
                count += self._draw_button(option, (550, 400+(i*60)), self.menu_map[self.curr_menu][option].split(':')[1])
            if self.menu_map[self.curr_menu][option].split(':')[0] == 'TextBox':
                count += self._draw_textbox((550, 400+(i*60)), self.menu_map[self.curr_menu][option].split(':')[1])
        if count == 0:
            self.hover = None
            self.action = None

        screen.blits(blit_sequence=self.all_sprites)

    def _draw_button(self, text, pos, action):
        if abs(self.cursor_x - pos[0]) < 100 and abs(self.cursor_y - pos[1]) < 20:
            rendered_text = self.font.render(text, True, GREY)
            textRect = rendered_text.get_rect()
            textRect.center = pos

            self.all_sprites.append((rendered_text, textRect))

            self.hover = text
            self.action = action
            return 1
        else:
            rendered_text = self.font.render(text, True, WHITE)
            textRect = rendered_text.get_rect()
            textRect.center = pos

            self.all_sprites.append((rendered_text, textRect))
            return 0
        
    def _draw_textbox(self, pos, action):
        input_box = pygame.Rect(pos[0]-70, pos[1], 140, 32)
        text = ''
        color = GREY if self.enter_text else WHITE
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.enter_text = True
                else:
                    self.enter_text = False
                # Change the current color of the input box.
            if event.type == pygame.KEYDOWN:
                if self.enter_text:
                    if event.key == pygame.K_RETURN:
                        print(self.text)
                        self.game_code = self.text
                        self.text = ''  # Reset text
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = text[:-1]
                    else:
                        self.text += event.unicode

        txt_surface = self.font.render(self.text, True, color)
        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(screen, color, input_box, 2)
        return 1

# Main loop
menu = Menu()
game = menu.run()

del menu

game.hex_r = 80
game.offset = 20
game.generate_board_shape()
game.set_space_value(5, 6.5, 'contains', 'Hawk_Red')
game.set_space_value(5, 1.5, 'contains', 'Hawk_Green')
game.set_space_value(7, 6.5, 'contains', 'Hawk_Red')
game.set_space_value(7, 1.5, 'contains', 'Hawk_Green')
game.set_space_value(5, 7.5, 'contains', 'Spirit_Red')
game.set_space_value(5, 0.5, 'contains', 'Spirit_Green')
game.set_space_value(7, 7.5, 'contains', 'Spirit_Red')
game.set_space_value(7, 0.5, 'contains', 'Spirit_Green')
game.set_space_value(6, 7, 'contains', 'Elder_Red')
game.set_space_value(6, 1, 'contains', 'Elder_Green')
game.set_space_value(2, 6, 'contains', 'Elder_Red')
game.set_space_value(2, 2, 'contains', 'Elder_Green')
game.set_space_value(10, 6, 'contains', 'Elder_Red')
game.set_space_value(10, 2, 'contains', 'Elder_Green')
game.set_space_value(3, 6.5, 'contains', 'Elder_Red')
game.set_space_value(3, 1.5, 'contains', 'Elder_Green')
game.set_space_value(9, 6.5, 'contains', 'Elder_Red')
game.set_space_value(9, 1.5, 'contains', 'Elder_Green')
game.set_space_value(4, 7, 'contains', 'Warrior_Red')
game.set_space_value(4, 1, 'contains', 'Warrior_Green')
game.set_space_value(8, 7, 'contains', 'Warrior_Red')
game.set_space_value(8, 1, 'contains', 'Warrior_Green')
game.set_space_value(6, 0.0, 'contains', 'Chief_Green')
game.set_space_value(6, 8, 'contains', 'Chief_Red')
game.eval_control()

game.run()

pygame.quit()