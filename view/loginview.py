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


class InputBox:

    def __init__(self, rect:tuple, label='label',input_text='', parent=None):
        self.input_rect = pygame.Rect(rect)
        self.color = COLOR_INACTIVE
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
        self.input_rect.width, self.input_rect.height = width+6, height+6
        self.active = False
        
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
                if self.input_rect.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = not self.active
                else:
                    self.active = False
                # Change the current color of the input box.
                self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
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
        self.input_rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.input_rect.x+5, self.input_rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.input_rect, 2)


     


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
            return pygame.event.post(pygame.event.Event(LOGINEVENT))
        else:
            return None
        
        
    def set_font(self):
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)

    def draw(self):
        self.button_text = self.font.render(self.label, True, self.button_color)
        width, height = self.font.size(self.label)
        self.button_rect.width, self.button_rect.height = width+6, height+6
        if self.button_enabled:
            if self.clicked():
                pygame.draw.rect(self.screen, 'dark gray', self.button_rect)
                time.sleep(0.5)
            else:
                pygame.draw.rect(self.screen, 'light gray', self.button_rect)
        else:
            pygame.draw.rect(self.screen, 'blue', self.button_rect)
        self.screen.blit(self.button_text, self.coord)
        



class LoginView(object):
    def __init__(self, screen):
        # Set up the input boxes
        # self.username_box = pg.Rect(200, 200, 400, 50)
        self.passcode_box = InputBox((200, 200, 200, 38), parent=screen)
        # Set up the buttons
        self.login_button = PushButton((200, 338, 200, 38), label='LOG IN', parent=screen)
        self.login_button.enabled(True)

    def get_input_text(self):
        if self.passcode_box.text:
            return self.passcode_box.text

    def draw(self, screen):
        self.passcode_box.update()
        screen.fill((255, 255, 255))
        self.passcode_box.draw(screen)
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


if __name__ == '__main__':
    main_loop()
    pygame.quit()