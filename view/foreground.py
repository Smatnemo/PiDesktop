import pygame


from LDS.language import get_translated_text
from LDS.view.background import multiline_text_to_surfaces
from LDS.view.documentsview import InmateDocumentsView, DocumentsView
from LDS.view.loginview import PushButton

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Foreground(object):
    def __init__(self, name, color=WHITE):
        self.foreground_color = color
        self.foreground_rect = None
        self._name = name

    def __str__(self):
        """Return foreground final name.

        It is used in the main window to distinguish foregrounds in the cache
        thus each foreground string shall be uniq.
        """
        return "{}({})".format(self.__class__.__name__, self._name)
    
    
    def resize(self, screen):
        """Resize objects to fit to the screen.
        """
        self.foreground_rect = screen.get_rect()
        # Reduce the height by 20 percent and make self._rect have 20 percent less height than screen
        height = self.foreground_rect.height
        self.foreground_rect.height = height - 94
        self.foreground_rect.y = self.foreground_rect.y + 94
        # Write code to determine the height of each row based on screen size

    def resize_texts(self, rect=None, align='center'):
        """Update text surfaces.
        """
        self._texts = []
        text = get_translated_text(self._name)
        

    def paint(self, screen):
        """Paint and animate the surfaces on the screen.
        """
        # use screen to get width of foreground window
        pygame.draw.rect(screen, self.foreground_color, self.foreground_rect)
    
        
class ChooseInmateDocumentForeground(Foreground):
    """
    Attributes
    attr inmate_documents: a dictionary with inmate number and their associated documents
    type inmate_documents: dictionary
    """
    def __init__(self, inmate_documents, _d, config=None):
        Foreground.__init__(self, "choose_inmate")
        # inmate_documents argument is a tuple
        self._d = _d
        self._c = config
        self.inmate_documents_view = InmateDocumentsView(inmate_documents, self._d, config) 
        
        self.previousbutton = self.nextbutton = None
        self.previousbutton_width = self.nextbutton_width = self._d['btn_handf_x']
        self.previousbutton_height = self.nextbutton_height = self._d['btn_handf_y']
        self.previousbutton_event = pygame.USEREVENT+1, {'change_view':"previous"}
        self.nextbutton_event = pygame.USEREVENT+1, {'change_view':"next"}

        self.button_enabled = True
        self.update_needed = None

    def resize(self, screen):
        Foreground.resize(self, screen)

        #  Create parameters for button
        self._rect = screen.get_rect() 
        # X Positions
        self.nextbutton_x = self._rect.width - self._d['pad'] - int(self._d['row_height']//2) - self._d['btn_handf_x']
        self.previousbutton_x = self._rect.x + self._d['pad'] + int(self._d['row_height']//2)
        # Y Positions
        self.nextbutton_y = self.previousbutton_y = self._rect.height - self._d['pad'] - int(self._d['row_height']//4) - self._d['btn_handf_y']    

        if self.button_enabled:
            self.previousbutton = PushButton((self.previousbutton_x, self.previousbutton_y, self.previousbutton_width, self.previousbutton_height),
                                             self.previousbutton_event, label='PREVIOUS',
                                             font_color=self._c.gettyped("WINDOW", "font_secondary_color"),
                                             button_color=self._c.gettyped("WINDOW", "btn_bg_green"),
                                             button_hover_color=self._c.gettyped("WINDOW", "btn_bg_green_hover"),
                                             border_radius=self._c.gettyped("WINDOW", "btn_primary_radius")[0],
                                             parent=screen)
            self.previousbutton.enabled(True)

            self.nextbutton = PushButton((self.nextbutton_x, self.nextbutton_y, self.nextbutton_width, self.nextbutton_height), self.nextbutton_event,
                                          label='NEXT',
                                          font_color=self._c.gettyped("WINDOW", "font_secondary_color"),
                                          button_color=self._c.gettyped("WINDOW", "btn_bg_green"),
                                          button_hover_color=self._c.gettyped("WINDOW", "btn_bg_green_hover"),
                                          border_radius=self._c.gettyped("WINDOW", "btn_primary_radius")[0],
                                          parent=screen)
            self.nextbutton.enabled(True)
            self.button_enabled = False

    def paint(self, screen):
        Foreground.paint(self, screen)
        self.inmate_documents_view.draw(self.foreground_rect, screen)
        self.inmate_documents_view.update()
        # Draw buttons
        self.nextbutton.draw(self.update_needed)
        self.previousbutton.draw(self.update_needed)
        


class ChosenInmateDocumentForeground(Foreground):
    def __init__(self, inmate_documents, selected_inmate, _d, config):
        Foreground.__init__(self, "chosen_inmate")
        self._d = _d
        self._c = config

        self.document_view = DocumentsView(inmate_documents, selected_inmate, self._d, config)

        self.previousbutton = None
        self.previousbutton_width = 200
        self.previousbutton_height = 38
 
        self.button_enabled = True
        self.previousbutton_event = pygame.USEREVENT + 1, {'change_view':'previous'}

        self.update_needed = None

        self.nextbutton = None
        self.nextbutton_width = 200
        self.nextbutton_height = 38

        self.nextbutton_event = pygame.USEREVENT + 1, {'change_view':'next'}

        

    def resize(self, screen):
        Foreground.resize(self, screen)

        #  Create parameters for button
        self._rect = screen.get_rect() 
        self.nextbutton_x = self.foreground_rect.width - 210
        self.nextbutton_y = self._d['bottombuttony']

        self.previousbutton_x = self.foreground_rect.x+10
        self.previousbutton_y = self.nextbutton_y

        if self.button_enabled:
            self.previousbutton = PushButton((self.previousbutton_x, self.previousbutton_y, self.previousbutton_width, self.previousbutton_height), self.previousbutton_event, label='PREVIOUS', parent=screen)
            self.previousbutton.enabled(True)

            self.nextbutton = PushButton((self.nextbutton_x, self.nextbutton_y, self.nextbutton_width, self.nextbutton_height), self.nextbutton_event, label='NEXT', parent=screen)
            self.nextbutton.enabled(True)
            self.button_enabled = False

    def paint(self, screen):
        Foreground.paint(self, screen)
        self.document_view.draw(self.foreground_rect, screen)
        self.document_view.update()

        # Draw buttons
        self.nextbutton.draw(self.update_needed)
        self.previousbutton.draw(self.update_needed)


class NoDocumentForeground(Foreground):
    def __init__(self):
        Foreground.__init__(self, "No_documents")


        
