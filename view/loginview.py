from curses import BUTTON1_CLICKED
import pygame 
import time
import sys
import os.path as osp

from LDS import fonts, pictures
from LDS.config import PiConfigParser
from LDS.media import get_filename

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
BLACK = (0, 0, 0)
COLOR_INACTIVE = (255,255,255)
COLOR_ACTIVE = (0,0,0)
FONTPRIMARY = (255,255,255)



class InputBox:

    def __init__(self, rect:tuple, label="", input_text_length=10, hide_text=True, parent=None, color_inactive=COLOR_INACTIVE, bg_color=COLOR_INACTIVE, font_size=32, font_color=FONTPRIMARY):
        self.input_rect_border = pygame.Rect(rect)
        self.rect = rect
        #self.border_color = pygame.Color(color_inactive)
        self.color = bg_color
        self.bg_color = bg_color
        self.font_color = font_color
        self.font_size = font_size
        self.text = label
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
        self.txt_surface = self.font.render(self.text, True, self.font_color)
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
        self.font = pygame.font.Font(fonts.CURRENT, self.font_size)

    def handle_event(self, events):
        for event in events:
            if event.type >= CLEARBUTTON: 
                # if self.active:
                button_event, input_text = self.check_event(event)
                if button_event:                    
                    if self.text == self.label:
                        self.text = ""
                    self.text += input_text  
                    if self.hide_text:
                        self.hidden_input_text += '*'
                    if len(self.text) > self.max_input_length:
                        self.text = self.text[:-1]
                        self.hidden_input_text = self.hidden_input_text[:-1]
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
                    self.txt_surface = self.font.render(self.hidden_input_text, True, self.font_color)
                else:
                    self.txt_surface = self.font.render(self.text, True, self.font_color)
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
                #self.border_color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        
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
                    self.txt_surface = self.font.render(self.hidden_input_text, True, self.font_color)
                else:
                    self.txt_surface = self.font.render(self.text, True, self.font_color)

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
        pygame.draw.rect(screen, self.bg_color, self.input_rect_border)
        # self.input_rect.w = self.input_rect-2
        pygame.draw.rect(screen, self.bg_color, self.input_rect)
        # Blit the text.
        screen.blit(self.txt_surface, (self.input_rect_border.x+5, self.input_rect_border.y+5))
        


class PushButton:
    def __init__(self, rect:tuple, user_event, label:str='Button', parent=None, label_clicked=None, font_color=FONTPRIMARY, font_size=32, button_color=(128,128,128), button_hover_color=(128,128,128), border_radius=3):
        if label.endswith('.png') or label.endswith('.jpg'):
            self.icon, self.icon_clicked = self.use_icon(label, label_clicked)
            self.label = None
        else:
            self.label = label
            self.icon = None
            self.icon_clicked = None
        self.button_color = button_color 
        self.button_hover_color = button_hover_color
        self.font_color = font_color
        self.font_size = font_size
        self.button_rect = pygame.Rect(rect)
        self.coord = [self.button_rect.x+3, self.button_rect.y+3]
        self.button_enabled = True
        self.button_clicked = False 
        self.button_released = True
        self.event = user_event
        self.border_radius = border_radius
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
                self.button_enabled = True
            elif enabled == 'False':
                self.button_color = COLOR_INACTIVE 
                self.button_enabled = False

        if isinstance(enabled, bool):
            if enabled == True:                
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
        self.font = pygame.font.Font(fonts.CURRENT, self.font_size)

    def draw(self, event):
        # Do this for text
        if self.label:
            self.button_text = self.font.render(self.label, True, self.font_color)
            width, height = self.font.size(self.label)
            self.coord[0]=self.button_rect.centerx-width//2
            self.coord[1]=self.button_rect.centery-height//2

        if self.button_enabled:
            pygame.draw.rect(self.screen, self.button_color, self.button_rect, 0, self.border_radius)
            if self.icon:
                self.screen.blit(self.icon, self.icon.get_rect(center=self.button_rect.center))
            else:
                self.screen.blit(self.button_text, self.coord) 
            clicked = self.clicked(event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(self.screen, self.button_hover_color, self.button_rect, 0, self.border_radius)
                if self.icon_clicked:
                    self.screen.blit(self.icon_clicked, self.icon_clicked.get_rect(center=self.button_rect.center))
                else:
                    self.screen.blit(self.button_text, self.coord)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(self.screen, self.button_color, self.button_rect, 0, self.border_radius)
                if self.icon:
                    self.screen.blit(self.icon, self.icon.get_rect(center=self.button_rect.center))
                else:
                    self.screen.blit(self.button_text, self.coord)
        else:
            pygame.draw.rect(self.screen, COLOR_INACTIVE, self.button_rect, 0, self.border_radius)
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
    def __init__(self, button_color, x,y,width,height, label='', label_clicked='', font_color=FONTPRIMARY, font_face=fonts.CURRENT, font_size=60, button_hover_color=(128,128,128), border_radius=3):
        if label.endswith('.png') or label.endswith('.jpg'):
            self.icon, self.icon_clicked = self.use_icon(label, label_clicked)
            self.label = None
        else:
            self.label = label
            self.icon = None
            self.icon_clicked = None
        self.color = button_color
        self.hover_color = button_hover_color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.over = False
        self.button_enabled = True
        self.button_rect = pygame.Rect(self.x, self.y, self.width,self.height)
        self.font_color = font_color 
        self.border_radius = border_radius
        self.font_size = font_size
        self.font_face = font_face


    def draw(self,window,event):
        #Call this method to draw the button on the screen
        if self.button_enabled:
            pygame.draw.rect(window, self.color, self.button_rect,0, self.border_radius)
            clicked = self.clicked(window, event)
            if clicked=='BUTTONDOWN':
                pygame.draw.rect(window, self.hover_color, self.button_rect, 0, self.border_radius)
            elif clicked=='BUTTONUP':
                pygame.draw.rect(window, self.color, self.button_rect, 0, self.border_radius)
        else:   
            pygame.draw.rect(window, (0,0,255), self.button_rect,0, self.border_radius)  
        
        if self.label != '' or self.icon:
            font = pygame.font.SysFont(self.font_face, self.font_size)
            text = font.render(self.label, 1, self.font_color)
            if self.icon:
                window.blit(self.icon, self.icon_clicked.get_rect(center=self.button_rect.center))
            else:
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
            if self.label == 'X':
                BUTTON_EVENT= CLEARBUTTON
            elif self.label == 'del_icon.png':
                BUTTON_EVENT = BACKSPACEBUTTON
            else:
                BUTTON_EVENT = pygame.USEREVENT+5+int(self.label)
            pygame.event.post(pygame.event.Event(BUTTON_EVENT))
            return 'BUTTONUP'
        else:
            return None
        
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


        

class LoginView(object):
    def __init__(self, screen, label, dimensions, config):
        font_primary_color = config.gettyped("WINDOW", "font_primary_color")
        font_secondary_color = config.gettyped("WINDOW", "font_secondary_color")
        app_bg_primary_color = config.gettyped("WINDOW", "app_bg_primary")
        app_bg_secondary_color = config.gettyped("WINDOW", "app_bg_secondary")
        th_bg_color = config.gettyped("WINDOW", "th_bg")
        btn_primary_radius = config.gettyped("WINDOW", "btn_primary_radius")
        btn_secondary_radius = config.gettyped("WINDOW", "btn_secondary_radius")
        btn_num_radius = config.gettyped("WINDOW", "btn_num_radius")

        number_button_color = config.gettyped("WINDOW", "btn_bg_num")
        number_button_color_hover = config.gettyped("WINDOW", "btn_bg_num_hover")
        unlock_button_color = config.gettyped("WINDOW", "btn_bg_green")
        unlock_button_color_hover = config.gettyped("WINDOW", "btn_bg_green_hover")
        input_login_bg = config.gettyped("WINDOW", "input_login_bg")

        self.update_needed = None
        self._d = dimensions
        
        self._r = pygame.Rect(int(self._d['startrowgridx']-self._d['marginx']), int(self._d['startrowgridy']), int(self._d['unlock_x']), (int(self._d['fourthrowy']+self._d['inputheight'])))
        self._rc = app_bg_secondary_color

        self.passcode_box = InputBox(((self._d['startrowgridx']-self._d['marginx']), self._d['startrowgridy'], self._d['unlock_x'], self._d['inputheight']), parent=screen, bg_color=input_login_bg, font_size=32, font_color=font_primary_color, label='Enter CO Unlock Code')
        self.passcode_box.key_pad_rect = [pygame.Rect(self._d['startrowgridx'], self._d['startrowgridy'], self._d['gridwidth'], self._d['inputheight'])]
        
        # the numbers for the calcaltor self._d['btn_num_x'] self._d['btn_num_y']
        s_1s = button(number_button_color,self._d['firstcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '1', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_2s = button(number_button_color,self._d['secondcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '2', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_3s = button(number_button_color,self._d['thirdcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '3', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['firstrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_4s = button(number_button_color,self._d['firstcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '4', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_5s = button(number_button_color,self._d['secondcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '5', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_6s = button(number_button_color,self._d['thirdcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '6', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['secondrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_7s = button(number_button_color,self._d['firstcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '7', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_8s = button(number_button_color,self._d['secondcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '8', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_9s = button(number_button_color,self._d['thirdcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '9', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['thirdrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        #s_clears = button(number_button_color,self._d['firstcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y'], 'X')
        #self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['firstcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y']))
        
        self.login_button = PushButton((self._d['firstcolumnx'], self._d['fourthrowy'], self._d['btn_num_x'], self._d['btn_num_y']),LOGINEVENT, label, screen, font_color=font_secondary_color, button_color=unlock_button_color, button_hover_color=unlock_button_color_hover, border_radius=btn_primary_radius[0])
        self.login_button.enabled(True)

        s_0s = button(number_button_color,self._d['secondcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y'], '0', button_hover_color=number_button_color_hover, border_radius=btn_num_radius[0])
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['secondcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y']))

        s_back = button(app_bg_secondary_color,self._d['thirdcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y'], label='del_icon.png')
        self.passcode_box.key_pad_rect.append(pygame.Rect(self._d['thirdcolumnx'],self._d['fourthrowy'],self._d['btn_num_x'],self._d['btn_num_y']))
        
        self.numbers = [s_1s,s_2s,s_3s,s_4s,s_5s,s_6s,s_7s,s_8s,s_9s,s_0s,s_back]


    def get_input_text(self):
        if self.passcode_box.text:
            return self.passcode_box.text

    def draw(self, screen):   
        pygame.draw.rect(screen, self._rc, self._r)
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
                #print(pass_code) 
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