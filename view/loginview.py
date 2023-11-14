from curses import BUTTON1_CLICKED
import pygame 
import time


pygame.init()
WIDTH = 640
HEIGHT = 480
DEFAULT_SIZE = WIDTH, HEIGHT
vid_info = pygame.display.Info()
vid_size = vid_info.current_w, vid_info.current_h
screen = pygame.display.set_mode(vid_size)
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font('freesansbold.ttf', 20)
LOGINEVENT = pygame.USEREVENT + 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class InputBox:

    def __init__(self, rect:tuple, label='label',input_text='', parent=None):
        self.input_rect_border = pygame.Rect(rect)
        self.border_color = COLOR_INACTIVE
        self.color = COLOR_INACTIVE
        self.text_field_color = WHITE
        self.font_size = 32
        self.text = input_text
        self.label = label
        self.input_text = ''
        if not parent:
            self.iniScreen()
        else:
            self.screen = parent
            self.set_font()
        self.txt_surface = self.font.render(self.text, True, self.color)
        width, height = self.font.size(self.text)
        self.input_rect_border.width, self.input_rect_border.height = width+6, height+6
        self.active = False

        # Create input rectangle to be 2 pixels less than the input_rect_border
        self.input_rect = pygame.Rect(rect[0]+2, rect[1]+2, rect[2]-4, rect[3]-4)
        
    def iniScreen(self):
        pygame.init()
        self.set_font()
        self.screen = pygame.display.set_mode(DEFAULT_SIZE, pygame.RESIZABLE)

    def set_font(self):
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)

    def activate_box_event(self, events):
        pass

    def clear_box_event(self, events):
        pass 

    def handle_event(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if self.input_rect_border.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.border_color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        pygame.event.post(pygame.event.Event(LOGINEVENT))
                        self.input_text = self.text
                        self.text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode
                    # Re-render the text.
                    self.txt_surface = self.font.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.input_rect_border.w = width
        self.input_rect.w = width-4

    def draw(self, screen):
        # Blit the rect.
        pygame.draw.rect(screen, self.border_color, self.input_rect_border, 2)
        # self.input_rect.w = self.input_rect-2
        pygame.draw.rect(screen, self.text_field_color, self.input_rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.input_rect_border.x+5, self.input_rect_border.y+5))
        
        


     


class PushButton:
    def __init__(self, rect:tuple, label:str='Button', parent=None):
        self.label = label
        self.button_color = COLOR_INACTIVE 
        self.font_size = 32
        self.button_rect = pygame.Rect(rect)
        self.coord = self.button_rect.x+3, self.button_rect.y+3
        self.button_enabled = True
        self.button_clicked = False 
        self.button_released = True
        if not parent:
            self.iniScreen()
        else:
            self.screen = parent
            self.set_font()
        
        self.draw()

    def iniScreen(self):
        pygame.init()
        self.set_font()
        self.screen = pygame.display.set_mode(DEFAULT_SIZE, pygame.RESIZABLE)
        self.screen.fill((255,255,255))

    def enabled(self, enabled:str or bool):
        if isinstance(enabled,str):
            if enabled == 'True':
                self.button_color = COLOR_ACTIVE 
                self.button_enabled = True
            elif enabled == 'False':
                self.button_color = COLOR_INACTIVE 
                self.button_enabled = False

        if isinstance(enabled, bool):
            if enabled == True:
                self.button_color = COLOR_ACTIVE 
                self.button_enabled = True
            else:
                self.button_color = COLOR_INACTIVE
                self.button_enabled = False

        # Else log in error 
        
    def clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.button_rect.collidepoint(mouse_pos) and self.button_enabled:
            return True
        else:
            return None
    
    def hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos) and self.button_enabled:
            return True 
        else:
            return None
        
    def set_font(self):
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)

    def draw(self):
        self.button_text = self.font.render(self.label, True, self.button_color)
        width, height = self.font.size(self.label)
        self.button_rect.width, self.button_rect.height = width+6, height+6
        
        if self.button_enabled:
            if self.hovered():
                pygame.draw.rect(self.screen, 'dark gray', self.button_rect)
            else:
                pygame.draw.rect(self.screen, 'light gray', self.button_rect)
        else:
            pygame.draw.rect(self.screen, 'blue', self.button_rect)
        self.screen.blit(self.button_text, self.coord)


class button():
    def __init__(self, color, x,y,width,height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.over = False
        self.button_enabled = True
        self.button_rect = pygame.Rect(self.x, self.y, self.width,self.height)

    def draw(self,window):
        #Call this method to draw the button on the screen
        if self.button_enabled:
            if self.hovered():
                pygame.draw.rect(window, 'light gray', self.button_rect,0)
            else:
                pygame.draw.rect(window, 'light blue', self.button_rect,0)
        else:   
            pygame.draw.rect(window, 'blue', self.button_rect,0)    
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, (0,0,0))
            window.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False

    def playSoundIfMouseIsOver(self, pos, sound):
        if self.isOver(pos):            
            if not self.over:
                beepsound.play()
                self.over = True
        else:
            self.over = False

    def hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_pos) and self.button_enabled:
            return True 
        else:
            return None 
        
    def clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.button_rect.collidepoint(mouse_pos) and self.button_enabled:
            return pygame.event.post(pygame.event.Event(LOGINEVENT))
        else:
            return None


class LoginView(object):
    def __init__(self, screen):
        # Set up the input boxes
        # self.username_box = pg.Rect(200, 200, 400, 50)
        
        passcode_box_width = 200
        passcode_box_height = 38
        x = screen.get_rect().center[0] - passcode_box_width//2
        y = screen.get_rect().center[1] - passcode_box_height//2 - 200
        
        self.passcode_box = InputBox((x, y, passcode_box_width, passcode_box_height), parent=screen)
        button_width = 60 
        button_height = 56
        row_margin = 6
        column_margin = 6
        first_row_y_position = y+58
        second_row_y_position = first_row_y_position + button_height + column_margin
        third_row_y_position = second_row_y_position + button_height + column_margin 
        fourth_row_y_position = third_row_y_position + button_height + column_margin

        first_column_x_position = x
        second_column_x_position = first_column_x_position + button_width + row_margin
        third_column_x_position = second_column_x_position + button_width + row_margin 
        
        # the numbers for the calcaltor
        s_1s = button((0,255,0),first_column_x_position,first_row_y_position,button_width,button_height, '1')
        s_2s = button((0,255,0),second_column_x_position,first_row_y_position,button_width,button_height, '2')
        s_3s = button((0,255,0),third_column_x_position,first_row_y_position,button_width,button_height, '3')
        s_4s = button((0,255,0),first_column_x_position,second_row_y_position,button_width,button_height, '4')
        s_5s = button((0,255,0),second_column_x_position,second_row_y_position,button_width,button_height, '5')
        s_6s = button((0,255,0),third_column_x_position,second_row_y_position,button_width,button_height, '6')
        s_7s = button((0,255,0),first_column_x_position,third_row_y_position,button_width,button_height, '7')
        s_8s = button((0,255,0),second_column_x_position,third_row_y_position,button_width,button_height, '8')
        s_9s = button((0,255,0),third_column_x_position,third_row_y_position,button_width,button_height, '9')
        s_xs = button((0,255,0),first_column_x_position,fourth_row_y_position,button_width,button_height, 'x')
        s_0s = button((0,255,0),second_column_x_position,fourth_row_y_position,button_width,button_height, '0')
        s_enter = button((0,255,0),third_column_x_position,fourth_row_y_position,button_width,button_height, '<-')
        

        self.numbers = [s_1s,s_2s,s_3s,s_4s,s_5s,s_6s,s_7s,s_8s,s_9s,s_xs,s_0s,s_enter]
        # Set up the buttons
        login_button_x = x + 50
        login_button_y = fourth_row_y_position + button_width + column_margin

        self.login_button = PushButton((login_button_x, login_button_y, 200, 38), label='LOG IN', parent=screen)
        self.login_button.enabled(True)

    def get_input_text(self):
        if self.passcode_box.text:
            return self.passcode_box.text

    def draw(self, screen):
        self.passcode_box.update()
        self.passcode_box.draw(screen)
        for button in self.numbers:
            button.draw(screen)
        self.login_button.draw()


    def update(self):
        pass




def main_loop():
    clock = pygame.time.Clock()

    lv = LoginView(screen)
    done = False

    
    while not done:
        events = list(pygame.event.get())
        for event in events:
            if event.type == pygame.QUIT:
                done = True        
        lv.passcode_box.handle_event(events)
        for event in events:
            if event.type == LOGINEVENT:
                pass_code = lv.get_input_text() 
                lv.passcode_box.text=''
                lv.passcode_box.txt_surface = lv.passcode_box.font.render(lv.passcode_box.text, True, lv.passcode_box.color)
                print(pass_code) 
              

        lv.draw(screen)

        pygame.display.flip()
        clock.tick(60)




if __name__ == "__main__":
    main_loop()