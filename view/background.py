# -*- coding: utf-8 -*-

import os.path as osp
import pygame
import time 

from LDS import fonts, pictures
from LDS.language import get_translated_text
from LDS.view.loginview import PushButton

ARROW_TOP = 'top'
ARROW_BOTTOM = 'bottom'
ARROW_HIDDEN = 'hidden'
ARROW_TOUCH = 'touchscreen'

BUTTONDOWN = pygame.USEREVENT + 1

def multiline_text_to_surfaces(text, color, rect, align='center'):
    """Return a list of surfaces corresponding to each line of the text.
    The surfaces are next to each others in order to fit the given rect.

    The ``align`` parameter can be one of:
       * top-left
       * top-center
       * top-right
       * center-left
       * center
       * center-right
       * bottom-left
       * bottom-center
       * bottom-right
    """
    surfaces = []
    lines = text.splitlines()
    font = fonts.get_pygame_font(max(lines, key=len), fonts.MONOID,
                                 rect.width, rect.height / len(lines))
    for i, line in enumerate(lines):
        surface = font.render(line, True, color)

        if align.endswith('left'):
            x = rect.left
        elif align.endswith('center'):
            x = rect.centerx - surface.get_rect().width / 2
        elif align.endswith('right'):
            x = rect.right - surface.get_rect().width / 2
        else:
            raise ValueError("Invalid horizontal alignment '{}'".format(align))

        height = surface.get_rect().height
        if align.startswith('top'):
            y = rect.top + i * height
        elif align.startswith('center'):
            y = rect.centery - len(lines) * height / 2 + i * height
        elif align.startswith('bottom'):
            y = rect.bottom - (len(lines) - i) * height
        else:
            raise ValueError("Invalid vertical alignment '{}'".format(align))

        surfaces.append((surface, surface.get_rect(x=x, y=y)))
    return surfaces


class Background(object):

    def __init__(self, image_name, document_name="", color=(0, 0, 0), text_color=(255, 255, 255)):
        self._rect = None
        self._name = image_name
        
        self._document_name = document_name
        self._need_update = False

        self._background = None
        self._background_color = color
        self._background_image = None

        self._overlay = None

        self._texts = []  # List of (surface, rect)
        self._text_border = 20  # Distance to other elements
        self._text_color = text_color

        # Build rectangles around some areas for debuging purpose
        self._show_outlines = True
        self._outlines = []

    def __str__(self):
        """Return background final name.

        It is used in the main window to distinguish backgrounds in the cache
        thus each background string shall be uniq.
        """
        return "{}({})".format(self.__class__.__name__, self._name)

    def _make_outlines(self, size):
        """Return a red rectangle surface.
        """
        outlines = pygame.Surface(size, pygame.SRCALPHA, 32)
        pygame.draw.rect(outlines, pygame.Color(255, 0, 0), outlines.get_rect(), 2)
        return outlines

    def _write_text(self, text, rect=None, align='center'):
        """Write a text in the given rectangle.
        """
        if not rect:
            rect = self._rect.inflate(-self._text_border, -self._text_border)
        if self._show_outlines:
            self._outlines.append((self._make_outlines(rect.size), rect))
        self._texts.extend(multiline_text_to_surfaces(text, self._text_color, rect, align))

    def set_color(self, color_or_path):
        """Set background color (RGB tuple) or path to an image that used to
        fill the background.

        :param color_or_path: RGB color tuple or image path
        :type color_or_path: tuple or str
        """
        if isinstance(color_or_path, (tuple, list)):
            assert len(color_or_path) == 3, "Length of 3 is required for RGB tuple"
            if color_or_path != self._background_color:
                self._background_color = color_or_path
                self._need_update = True
        else:
            assert osp.isfile(color_or_path), "Invalid image for window background: '{}'".format(color_or_path)
            if color_or_path != self._background_image:
                self._background_image = color_or_path
                self._background_color = (0, 0, 0)
                self._need_update = True

    def get_color(self):
        """Return the background color (RGB tuple).
        """
        return self._background_color

    def set_text_color(self, color):
        """Set text color (RGB tuple) used to write the texts.

        :param color: RGB color tuple
        :type color: tuple
        """
        assert len(color) == 3, "Length of 3 is required for RGB tuple"
        if color != self._text_color:
            self._text_color = color
            self._need_update = True

    def set_outlines(self, outlines=True):
        """Draw outlines for each rectangle available for drawing
        texts.

        :param outlines: enable / disable outlines
        :type outlines: bool
        """
        if outlines != self._show_outlines:
            self._show_outlines = outlines
            self._need_update = True

    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        if self._rect != screen.get_rect():
            self._rect = screen.get_rect()
            self._outlines = []

            if self._background_image:
                self._background = pictures.get_pygame_image(
                    self._background_image, (self._rect.width, self._rect.height), crop=True, color=None)
                self._background_color = pictures.get_pygame_main_color(self._background)

            overlay_name = "{}.png".format(self._name)
            if osp.isfile(pictures.get_filename(overlay_name)):
                self._overlay = pictures.get_pygame_image(
                    pictures.get_filename(overlay_name), (self._rect.width, self._rect.height), color=self._text_color, bg_color=self._background_color)

            self.resize_texts()
            self._need_update = True

    def resize_texts(self, rect=None, align='center'):
        """Update text surfaces.
        """
        self._texts = []
        text = get_translated_text(self._name)
        if self._document_name:
            text = text + ": " + str(self._document_name)
        if text:
            self._write_text(text, rect, align)

    def paint(self, screen):
        """Paint and animate the surfaces on the screen.
        """
        if self._background:
            screen.blit(self._background, (0, 0))
        else:
            screen.fill(self._background_color)
        if self._overlay:
            screen.blit(self._overlay, self._overlay.get_rect(center=self._rect.center))
        for text_surface, pos in self._texts:
            screen.blit(text_surface, pos)
        for outline_surface, pos in self._outlines:
            screen.blit(outline_surface, pos)
        self._need_update = False



class IntroBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0, state="intro", count=3):
        Background.__init__(self, state)
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.left_arrow = None
        self.left_arrow_pos = None


        self.font = pygame.font.SysFont("Sans", 50)
        self.timeout = pygame.time.get_ticks() 
        self.time_since_enter = 0
        self.count = count
        

    def resize(self, screen):
        Background.resize(self, screen)
            

    def resize_texts(self):
        """Update text surfaces.
        """
        # if self.arrow_location == ARROW_HIDDEN:
        rect = pygame.Rect(self._text_border, self._text_border,
                            self._rect.width / 2 - 2 * self._text_border,
                            self._rect.height - 2 * self._text_border)
        align = 'center'
        if self._name == 'locked':
            self.text_rect = rect
            self.align = align
        else:
            Background.resize_texts(self, rect, align)
    
        if align == 'center':
            for text_surface in self._texts:
                text_surface[1].x=self._rect.width//2-text_surface[1].width//2
                text_surface[1].y=self._rect.height//2-text_surface[1].height//2
                text_surface = list(text_surface)
                

    def countdown(self):
        if (30-self.time_since_enter//1000) < 0:
            self.timeout = pygame.time.get_ticks()
        self.time_since_enter = pygame.time.get_ticks() - self.timeout
        self.message = '{} attempts: Locked for {} seconds'.format(self.count, str(30-self.time_since_enter//1000))
        # self._write_text(self.message, self.text_rect, align='top-center')
        self.message_box = self.font.render(self.message, True, self._text_color)

        box_width, box_height = self.font.size(self.message)
        self.text_rect.x = self.text_rect.width//2 - box_width//2
        self.text_rect.y = self.text_rect.height//2 - box_height//2
        

    def paint(self, screen):
        Background.paint(self, screen)
        if self._name == 'locked':
            self.countdown()
            screen.blit(self.message_box, (self.text_rect.x, self.text_rect.y))


class LoginBackground(Background):
    def __init__(self):
        Background.__init__(self, "login")
        self.layout0 = None
        self.layout0_pos = None
        self.layout1 = None
        self.layout1_pos = None
        
    def resize(self, screen):
        Background.resize(self, screen)      

    def resize_texts(self):
        """Update text surfaces.
        """
        rect = pygame.Rect(self._text_border, self._text_border,
                           self._rect.width - 2 * self._text_border, self._rect.height * 0.15)
        Background.resize_texts(self, rect)

    def paint(self, screen):
        Background.paint(self, screen)
        


class ChooseInmateDocumentBackground(Background):
    def __init__(self, bkg_string="choose_document"):
        Background.__init__(self, bkg_string)
        self.layout0 = None 
        self.layout0_pos = None 
        self.layout1 = None
        self.layout1_pos = None 

        self.backbutton = None
        self.backbutton_width = 200
        self.backbutton_height = 38

        
        self.button_enabled = True
        self.backbutton_event = pygame.USEREVENT + 17

        self.update_needed = None

        self.lockbutton = None
        self.lockbutton_width = 200
        self.lockbutton_height = 38

        self.lockbutton_event = pygame.USEREVENT + 19


    def resize(self, screen):
        Background.resize(self, screen) 

        #  Create parameters for button 
        self._rect = screen.get_rect()
        self.backbutton_x = self._rect.x+10
        self.backbutton_y = self._rect.y+10  

        self.lockbutton_x = self._rect.width - 250
        self.lockbutton_y = self._rect.y+10

        if self.button_enabled:
            self.backbutton = PushButton((self.backbutton_x, self.backbutton_y, self.backbutton_width, self.backbutton_height), self.backbutton_event, label='<BACK', parent=screen)
            self.backbutton.enabled(True)

            self.lockbutton = PushButton((self.lockbutton_x, self.lockbutton_y, self.backbutton_width, self.backbutton_height), self.lockbutton_event, label='LOCK SCREEN', parent=screen)
            self.lockbutton.enabled(True)
            self.button_enabled = False

    def resize_texts(self):
        """Update text Surfaces
        """
        rect = pygame.Rect(self._text_border, self._text_border,
                           self._rect.width - 2 * self._text_border, self._rect.height * 0.15)
        Background.resize_texts(self, rect)
    
    def paint(self, screen):
        Background.paint(self, screen)
        self.backbutton.draw(self.update_needed)
        self.lockbutton.draw(self.update_needed)

        


class DecryptBackground(Background):
    def __init__(self):
        Background.__init__(self, "decrypt")
        self.layout0 = None
        self.layout0_pos = None
        self.layout1 = None
        self.layout1_pos = None

        self._rect = None
        self.backbutton = None
        self.backbutton_width = 200
        self.backbutton_height = 38

        
        self.backbutton_enabled = True
        self.backbutton_event = pygame.USEREVENT + 17

        self.lockbutton = None
        

        self.lockbutton_event = pygame.USEREVENT + 19

        self.update_needed = None
        
    def resize(self, screen):
        Background.resize(self, screen)

        #  Create parameters for button 
        self._rect = screen.get_rect()
        self.backbutton_x = self._rect.x+60
        self.backbutton_y = self._rect.height-120  

        self.lockbutton_x = self._rect.width - 250
        self.lockbutton_y = self._rect.y+10

        if self.backbutton_enabled:
            self.backbutton = PushButton((self.backbutton_x, self.backbutton_y, self.backbutton_width, self.backbutton_height), self.backbutton_event, label='<BACK', parent=screen)
            self.backbutton.enabled(True)

            self.lockbutton = PushButton((self.lockbutton_x, self.lockbutton_y, self.backbutton_width, self.backbutton_height), self.lockbutton_event, label='LOCK SCREEN', parent=screen)
            self.lockbutton.enabled(True)

            self.backbutton_enabled = False
        

    def resize_texts(self):
        """Update text surfaces.
        """
        rect = pygame.Rect(self._text_border, self._text_border,
                           self._rect.width - 2 * self._text_border, self._rect.height * 0.15)
        Background.resize_texts(self, rect)

    def paint(self, screen):
        Background.paint(self, screen)
        


class CaptureBackground(Background):

    def __init__(self):
        Background.__init__(self, "capture")
        self.left_people = None
        self.left_people_pos = None
        self.right_people = None
        self.right_people_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            images_height = self._rect.height / 4
            size = (images_height * 2, images_height)

            self.left_people = pictures.get_pygame_image("capture_left.png", size=size,
                                                         color=self._text_color)
            self.right_people = pictures.get_pygame_image("capture_right.png", size=size,
                                                          color=self._text_color)

            x = int(self._rect.right - size[0])
            y = int(self._rect.bottom - images_height)

            self.left_people_pos = (0, y)
            self.right_people_pos = (x + size[0] - 1.5 * self.right_people.get_rect().width, y)

    def paint(self, screen):
        Background.paint(self, screen)
        


class ProcessingBackground(Background):

    def __init__(self):
        Background.__init__(self, "processing")

    def resize_texts(self):
        """Update text surfaces.
        """
        rect = pygame.Rect(self._text_border, self._rect.height * 0.8 - self._text_border,
                           self._rect.width - 2 * self._text_border, self._rect.height * 0.2)
        Background.resize_texts(self, rect)


class PrintBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0, print_status="print", question="", document_name="", number_of_pages=""):
        Background.__init__(self, print_status, document_name)
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.right_arrow = None
        self.right_arrow_pos = None
        self.left_arrow = None
        self.left_arrow_pos = None
        self.question = question

        self._rect = None
        self.yesbutton = None
        self.yesbutton_width = 200
        self.yesbutton_height = 38

        self.nobutton_width = 200
        self.nobutton_height = 38
        self.yesbutton_y = None
        self.nobutton_x = None

        self.yesbutton_enabled = True
        
        self.yesbutton_event = (BUTTONDOWN, {'question':question,'answer':'YES'})
        self.nobutton = None

        self.nobutton_event = (BUTTONDOWN, {'question':question,'answer':'NO'})

        self.update_needed = None

        self.document_name = document_name 
        self.num_of_pages = number_of_pages

    def __str__(self):
        """Return background final name.

        It is used in the main window to distinguish backgrounds in the cache
        thus each background string shall be uniq.
        """
        return "{}({})({})".format(self.__class__.__name__, self._name, self.question)

    def resize(self, screen):
        Background.resize(self, screen)
        


    def resize_texts(self):
        """Update text surfaces.
        """
        rect = pygame.Rect(self._rect.x + self._text_border, self._text_border,
                            self._rect.width / 2 - 2 * self._text_border,
                            self._rect.height - 2 * self._text_border)
        align = 'center'
        Background.resize_texts(self, rect, align)

        if self.document_name:
            pages_text = get_translated_text('num_of_pages')
            pages_text = pages_text + ": " + str(self.num_of_pages)
        else:
            pages_text = get_translated_text('')

        if pages_text:
            rect = pygame.Rect(self._rect.x + self._text_border, self._text_border,
                            (self._rect.width / 2 - 2 * self._text_border)*0.65,
                            self._rect.height - 2 * self._text_border)

            self._write_text(pages_text, rect)

        # if self.question == 'capture':
        #     self.question = ''
        question_text = get_translated_text(self.question)
        if question_text:
            rect = pygame.Rect(self._rect.x + self._text_border, self._text_border,
                               self._rect.width/2 - 2 * self._text_border, self._rect.height - 2 * self._text_border)
            self._write_text(question_text, rect)

        # hold the height of each rectangle after drawing on the screen
        height = 0
        if self._name != 'capture_again':
            if align == 'center':     
                for text_surface in self._texts:
                    text_surface[1].x=(self._rect.width//2-text_surface[1].width//2)
                    text_surface[1].y=(self._rect.height//2-text_surface[1].height//2)+height
                    text_surface = list(text_surface)
                    height = text_surface[1].height + height
                    if self._texts[-1]:
                        self.nobutton_y = text_surface[1].y+height
                        self.yesbutton_y = text_surface[1].y+height 

            self.yesbutton_x = self._rect.width//2 - self.yesbutton_width
            self.nobutton_x = self._rect.width//2 + self.nobutton_width
        else:
            if self.arrow_location == ARROW_BOTTOM:
                rect = pygame.Rect(self._rect.width / 2 + self._text_border, self._text_border,
                                self._rect.width / 2 - 2 * self._text_border,
                                self._rect.height * 0.6 - self._text_border)
                align = 'bottom-center'
            Background.resize_texts(self, rect, align)

            self.yesbutton_x = self._rect.width*0.75 - self.yesbutton_width
            self.nobutton_x = self._rect.width*0.75 + self.nobutton_width
        
        if self.yesbutton_y is None:
            self.yesbutton_y = self._rect.height * 0.75
            self.nobutton_y = self._rect.height * 0.75
        

    def paint(self, screen):
        Background.paint(self, screen)

        if self.yesbutton_enabled:
            self.yesbutton = PushButton((self.yesbutton_x, self.yesbutton_y, self.yesbutton_width, self.yesbutton_height), self.yesbutton_event, label='YES', parent=screen)
            self.yesbutton.enabled(False)

            self.nobutton = PushButton((self.nobutton_x, self.nobutton_y, self.nobutton_width, self.nobutton_height), self.nobutton_event, label='NO', parent=screen)
            self.nobutton.enabled(False)

            self.yesbutton_enabled = False
        


class FinishedBackground(Background):

    def __init__(self):
        Background.__init__(self, "finished")
        self.left_people = None
        self.left_people_pos = None
        self.right_people = None
        self.right_people_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            left_rect = pygame.Rect(10, 0, self._rect.width * 0.4, self._rect.height * 0.5)
            left_rect.top = self._rect.centery - left_rect.centery
            right_rect = pygame.Rect(0, 0, self._rect.width * 0.3, self._rect.height * 0.5)
            right_rect.top = self._rect.centery - right_rect.centery
            right_rect.right = self._rect.right - 10

            self.left_people = pictures.get_pygame_image("finished_left.png", size=left_rect.size,
                                                         color=self._text_color)
            self.right_people = pictures.get_pygame_image("finished_right.png", size=right_rect.size,
                                                          color=self._text_color)

            self.left_people_pos = self.left_people.get_rect(center=left_rect.center).topleft
            self.right_people_pos = self.right_people.get_rect(center=right_rect.center).topleft

            if self._show_outlines:
                self._outlines.append((self._make_outlines(left_rect.size), left_rect.topleft))
                self._outlines.append((self._make_outlines(right_rect.size), right_rect.topleft))

    def resize_texts(self):
        """Update text surfaces.
        """
        rect = pygame.Rect(0, 0, self._rect.width * 0.35, self._rect.height * 0.4)
        rect.center = self._rect.center
        rect.bottom = self._rect.bottom - 10
        Background.resize_texts(self, rect)

    def paint(self, screen):
        Background.paint(self, screen)
        if self.left_people:
            screen.blit(self.left_people, self.left_people_pos)
        if self.right_people:
            screen.blit(self.right_people, self.right_people_pos)


class FinishedWithImageBackground(FinishedBackground):

    def __init__(self, foreground_size):
        FinishedBackground.__init__(self)
        self._name = "finishedwithimage"
        self.foreground_size = foreground_size

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update:
            # Note: '0.9' ratio comes from PiWindow._update_foreground() method which
            # lets a margin between window borders and fullscreen foreground picture
            frgnd_rect = pygame.Rect(0, 0, *pictures.sizing.new_size_keep_aspect_ratio(
                self.foreground_size, (self._rect.size[0] * 0.9, self._rect.size[1]*0.9)))
            xmargin = abs(self._rect.width - frgnd_rect.width) // 2
            ymargin = abs(self._rect.height - frgnd_rect.height) // 2

            if xmargin > 50:
                margin = min(xmargin, self._rect.height // 3)
            elif ymargin > 50:
                margin = min(ymargin, self._rect.width // 3)
            else:  # Too small
                self.left_people = None
                self.right_people = None
                return

            left_rect = pygame.Rect(0, 0, margin, margin)
            right_rect = pygame.Rect(0, 0, margin, margin)
            left_rect.bottom = self._rect.bottom
            right_rect.right = self._rect.right

            self.left_people = pictures.get_pygame_image("finished_left.png", size=left_rect.size,
                                                         color=self._text_color)
            self.right_people = pictures.get_pygame_image("finished_right.png", size=right_rect.size,
                                                          color=self._text_color)

            self.left_people_pos = self.left_people.get_rect(center=left_rect.center).topleft
            self.right_people_pos = self.right_people.get_rect(center=right_rect.center).topleft

            if self._show_outlines and left_rect and right_rect:
                self._outlines.append((self._make_outlines(left_rect.size), left_rect.topleft))
                self._outlines.append((self._make_outlines(right_rect.size), right_rect.topleft))


class OopsBackground(Background):

    def __init__(self):
        Background.__init__(self, "oops")


class WrongPasswordBackground(Background):
    def __init__(self):
        Background.__init__(self, "wrong_password")
