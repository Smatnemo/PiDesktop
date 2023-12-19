from curses import BUTTON1_CLICKED
import pygame 
import time
import sys
import os.path as osp

from LDS import fonts, pictures
from LDS.config import PiConfigParser
from LDS.media import get_filename

pygame.init()
vid_info = pygame.display.Info()
DEFAULT_SIZE = vid_info.current_w, vid_info.current_h
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font('freesansbold.ttf', 20)

LOGINEVENT = pygame.USEREVENT + 3
CLEARBUTTON = pygame.USEREVENT + 4
BUTTON_0 = pygame.USEREVENT + 5
BUTTON_1 = pygame.USEREVENT + 6
BUTTON_2 = pygame.USEREVENT + 7
BUTTON_3 = pygame.USEREVENT + 8
BUTTON_4 = pygame.USEREVENT + 9
BUTTON_5 = pygame.USEREVENT + 10
BUTTON_6 = pygame.USEREVENT + 11
BUTTON_7 = pygame.USEREVENT + 12
BUTTON_8 = pygame.USEREVENT + 13
BUTTON_9 = pygame.USEREVENT + 14
BACKSPACEBUTTON = pygame.USEREVENT + 15


button_events = [BUTTON_0,BUTTON_1, BUTTON_2, BUTTON_3, BUTTON_4, BUTTON_5, BUTTON_6, BUTTON_7, BUTTON_8, BUTTON_9]
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)




class InputBox:

    def __init__(self, rect:tuple, label='label',input_text='', input_text_length=10, hide_text=True, parent=None, color_inactive=COLOR_INACTIVE, font_size=32):
        self.input_rect_border = pygame.Rect(rect)
        self.rect = rect
        self.border_color = pygame.Color(color_inactive)
        self.color = pygame.Color(color_inactive)
        self.text_field_color = WHITE
        self.font_size = font_size
        self.text = input_text
        self.max_input_length = input_text_length
        self.label = label
        self.input_text = ''
        if hide_text:
            self.hide_text = hide_text
            self.hidden_input_text = ''
        if not parent:
            self.iniScreen()
        else:
            self.screen = parent
            self.set_font()
        self.txt_surface = self.font.render(self.text, True, self.color)
        width, height = self.font.size(self.text)
        self.input_rect_border.width, self.input_rect_border.height = width+6, height+6
        self.active = False
        self.key_pad_rect = [pygame.Rect(rect)]
        # Create input rectangle to be 2 pixels less than the input_rect_border
        self.input_rect = pygame.Rect(rect[0]+2, rect[1]+2, rect[2]-4, rect[3]-4)
        
    def iniScreen(self):
        pygame.init()
        self.set_font()
        self.screen = pygame.display.set_mode(DEFAULT_SIZE, pygame.RESIZABLE)

    def set_font(self):
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)

    def handle_event(self, events):
        for event in events:
            if event.type >= CLEARBUTTON: 
                # if self.active:
                button_event, input_text = self.check_event(event)
                if button_event:
                    if len(self.text) >= self.max_input_length:
                        self.text = self.text
                    else:
                        self.text = self.text + input_text
                        if self.hide_text:
                            self.hidden_input_text += '*'
                elif event.type==BACKSPACEBUTTON:
                    self.text = self.text[:-1]
                    if self.hide_text:
                        self.hidden_input_text = self.hidden_input_text[:-1]
                elif event.type==CLEARBUTTON:
                    self.text = ''
                    if self.hide_text:
                        self.hidden_input_text = ''
                    
                # Render updated text on text surface
                if self.hidden_input_text:
                    self.txt_surface = self.font.render(self.hidden_input_text, True, self.color)
                else:
                    self.txt_surface = self.font.render(self.text, True, self.color)
            if event.type == pygame.MOUSEBUTTONDOWN:     
                
                # If the user clicked on the input_box rect.
                if self.input_rect_border.collidepoint(event.pos):
                    # Toggle the active variable.
                    self.active = True
                elif self.active:
                    for rect in self.key_pad_rect:
                        if rect.collidepoint(event.pos):
                            self.active = True
                else:
                    self.active = False
                # Change the current color of the input box.
                self.border_color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        
            if event.type == pygame.KEYDOWN:
                # if self.active:
                if event.key == pygame.K_RETURN:
                    pygame.event.post(pygame.event.Event(LOGINEVENT))
                    self.input_text = self.text
                    self.text = ''
                    if self.hide_text:
                        self.hidden_input_text = self.text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1] 
                    if self.hide_text:
                        self.hidden_input_text = self.hidden_input_text[:-1]
                else:
                    if len(self.text) >= self.max_input_length:
                        self.text = self.text
                    else:
                        self.text += event.unicode
                        if self.hide_text:
                            self.hidden_input_text += '*'
                # Re-render the text.
                if self.hidden_input_text:
                    self.txt_surface = self.font.render(self.hidden_input_text, True, self.color)
                else:
                    self.txt_surface = self.font.render(self.text, True, self.color)

    def check_event(self, event):
        for text,button in enumerate(button_events):
            if event.type == button:
                return event, str(text)
        return None,""
        

    def update(self):
        # Resize the box if the text is too long.
        width = max(self.rect[2], self.txt_surface.get_width()+10)
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
    def __init__(self, rect:tuple, user_event, label:str='Button', parent=None, label_clicked=None):
        if label.endswith('.png') or label.endswith('.jpg'):
            self.icon, self.icon_clicked = self.use_icon(label, label_clicked)
            self.label = None
        else:
            self.label = label
            self.icon = None
            self.icon_clicked = None
        self.button_color = COLOR_INACTIVE 
        self.text_color = WHITE
        self.font_size = 32
        self.button_rect = pygame.Rect(rect)
        self.coord = [self.button_rect.x+3, self.button_rect.y+3]
        self.button_enabled = True
        self.button_clicked = False 
        self.button_released = True
        self.event = user_event
        if not parent:
            self.iniScreen()
        else:
            self.screen = parent
            self.set_font()
        
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
    def clicked(self, event):
        if not event:
            return None
        if event.type == pygame.FINGERUP or event.type == pygame.FINGERDOWN:
            w, h = self.screen.get_size()
            event.pos = (w*event.x), (h*event.y)
        if (event.type==pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN) and self.button_rect.collidepoint(event.pos) and self.button_enabled:
            return 'BUTTONDOWN'
        if (event.type==pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP) and self.button_rect.collidepoint(event.pos) and self.button_enabled:
            if isinstance(self.event, tuple):
                pygame.event.post(pygame.event.Event(self.event[0], self.event[1]))
            else:
                pygame.event.post(pygame.event.Event(self.event))
            return 'BUTTONUP'
        else:
            return None
    
    def hovered(self, event):
        if not event:
            return None
        try:
            if self.button_rect.collidepoint(event.pos) and self.button_enabled:
                return True 
            else:
                return None
        except:
            pass
        
    def set_font(self):
        self.font = pygame.font.Font('freesansbold.ttf', self.font_size)

    def draw(self, event):
        # Do this for text
        if self.label:
            self.button_text = self.font.render(self.label, True, self.button_color)
            width, height = self.font.size(self.label)
            self.coord[0]=self.button_rect.centerx-width//2
            self.coord[1]=self.button_rect.centery-height//2

        if self.button_enabled:
            pygame.draw.rect(self.screen, 'dark gray', self.button_rect, 0, 3)
            if self.icon:
                self.screen.blit(self.icon, self.icon.get_rect(center=self.button_rect.center))
            else:
                self.screen.blit(self.button_text, self.coord) 
            clicked = self.clicked(event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(self.screen, 'black', self.button_rect, 0, 3)
                if self.icon_clicked:
                    self.screen.blit(self.icon_clicked, self.icon_clicked.get_rect(center=self.button_rect.center))
                else:
                    self.screen.blit(self.button_text, self.coord)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(self.screen, 'dark gray', self.button_rect, 0, 3)
                if self.icon:
                    self.screen.blit(self.icon, self.icon.get_rect(center=self.button_rect.center))
                else:
                    self.screen.blit(self.button_text, self.coord)
        else:
            pygame.draw.rect(self.screen, 'blue', self.button_rect, 0, 3)
            if self.icon:
                self.screen.blit(self.icon, self.icon.get_rect(center=self.button_rect.center))
            else:
                self.screen.blit(self.button_text, self.coord)
        
        
    
    def use_icon(self, icon, icon_clicked=None):
        # Write code to resize image when given icon
        size = (64,64)
        icon_path = get_filename(icon)
        icon = pictures.get_pygame_image(icon_path, size, vflip=False, color=None)
        icon_color = None
        if icon_clicked:
            icon_path = get_filename(icon_clicked)
            icon_color = None
        icon_clicked = pictures.get_pygame_image(icon_path, size, vflip=False, color=icon_color)
        return icon, icon_clicked






class button(object):
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
        self.text_color = WHITE


    def draw(self,window,event):
        #Call this method to draw the button on the screen
        if self.button_enabled:
            pygame.draw.rect(window, 'light gray', self.button_rect,0, 3)
            clicked = self.clicked(window, event)
            if clicked=='BUTTONDOWN':
                pygame.draw.rect(window, 'black', self.button_rect, 0, 3)
            elif clicked=='BUTTONUP':
                pygame.draw.rect(window, 'light gray', self.button_rect, 0, 3)
        else:   
            pygame.draw.rect(window, 'blue', self.button_rect,0, 3)  
 
        if self.text != '':
            font = pygame.font.SysFont('comicsans', 60)
            text = font.render(self.text, 1, WHITE)
            window.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))


    def hovered(self, event):
        if not event:
            return None
        try:
            if self.button_rect.collidepoint(event.pos) and self.button_enabled:
                return True 
            else:
                return None 
        except:
            pass
        
    def clicked(self, screen, event):
        if not event:
            return None
        if event.type == pygame.FINGERUP or event.type == pygame.FINGERDOWN:
            w, h = screen.get_size()
            event.pos = (w*event.x), (h*event.y)
    
        if (event.type==pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERDOWN) and self.button_rect.collidepoint(event.pos) and self.button_enabled:
            return 'BUTTONDOWN'
        if (event.type==pygame.MOUSEBUTTONUP or event.type==pygame.FINGERUP) and self.button_rect.collidepoint(event.pos) and self.button_enabled:
            if self.text == 'X':
                BUTTON_EVENT= CLEARBUTTON
            elif self.text == '<':
                BUTTON_EVENT = BACKSPACEBUTTON
            else:
                BUTTON_EVENT = pygame.USEREVENT+5+int(self.text)
            pygame.event.post(pygame.event.Event(BUTTON_EVENT))
            return 'BUTTONUP'
        else:
            return None


        

class LoginView(object):
    def __init__(self, screen, label, dimensions, config):
        color_inactive = config.get("WINDOW","inactive_color")
        self.update_needed = None
        self._d = dimensions
        
        self.passcode_box = InputBox((self._d['startrowgridx'], self._d['startrowgridy'], self._d['gridwidth'], self._d['inputheight']), parent=screen, color_inactive=color_inactive, font_size=32)
        self.passcode_box.key_pad_rect = [pygame.Rect(self._d['startrowgridx'], self._d['startrowgridy'], self._d['gridwidth'], self._d['inputheight'])]
        
        # the numbers for the calcaltor
        s_1s = button((0,255,0),self._d['firstcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey'], '1')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_2s = button((0,255,0),self._d['secondcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey'], '2')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_3s = button((0,255,0),self._d['thirdcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey'], '3')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['firstrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_4s = button((0,255,0),self._d['firstcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey'], '4')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_5s = button((0,255,0),self._d['secondcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey'], '5')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_6s = button((0,255,0),self._d['thirdcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey'], '6')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['secondrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_7s = button((0,255,0),self._d['firstcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey'], '7')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_8s = button((0,255,0),self._d['secondcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey'], '8')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_9s = button((0,255,0),self._d['thirdcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey'], '9')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['thirdrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_clears = button((0,255,0),self._d['firstcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey'], 'X')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_0s = button((0,255,0),self._d['secondcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey'], '0')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey']))

        s_back = button((0,255,0),self._d['thirdcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey'], '<')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['fourthrowy'],self._d['iconsizex'],self._d['iconsizey']))
        

        self.numbers = [s_1s,s_2s,s_3s,s_4s,s_5s,s_6s,s_7s,s_8s,s_9s,s_clears,s_0s,s_back]
        

        # Set up the buttons
        self.login_button = PushButton((self._d['firstcolumnx'], self._d['loginbuttony'], self._d['gridwidth'], self._d['iconsizey']),LOGINEVENT, label, screen)
        self.login_button.enabled(True)

    def get_input_text(self):
        if self.passcode_box.text:
            return self.passcode_box.text

    def draw(self, screen):
        self.passcode_box.update()
        self.passcode_box.draw(screen)
        for button in self.numbers:
            button.draw(screen, self.update_needed)
        self.login_button.draw(self.update_needed)



def main_loop():
    clock = pygame.time.Clock()

    lv = LoginView(screen)
    done = False

    
    while not done:
        events = list(pygame.event.get())
        
        for event in events:
            if event.type == pygame.QUIT:
                done = True        
            if event.type == LOGINEVENT:
                pass_code = lv.get_input_text() 
                lv.passcode_box.text=''
                lv.passcode_box.txt_surface = lv.passcode_box.font.render(lv.passcode_box.text, True, lv.passcode_box.color)
                print(pass_code) 
            if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.MOUSEMOTION\
                or event.type==pygame.MOUSEBUTTONUP or event.type==pygame.FINGERUP or event.type==pygame.FINGERDOWN:
                lv.update_needed=event
            else:
                lv.update_needed=None
            
        lv.passcode_box.handle_event(events)  

        lv.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)




if __name__ == "__main__":
    main_loop()