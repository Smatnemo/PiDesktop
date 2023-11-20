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
        self.foreground_rect.height = 0.75 * height 
        self.foreground_rect.y = self.foreground_rect.y + (0.25 * height)
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
    def __init__(self, inmate_documents):
        Foreground.__init__(self, "choose_inmate")
        # inmate_documents argument is a tuple
        self.inmate_documents_view = InmateDocumentsView(inmate_documents) 
        # Make sure that drawn inmates documents view should stop at 10 pixels before the button 
        
        self.previousbutton = None
        self.previousbutton_width = 200
        self.previousbutton_height = 38
 
        self.button_enabled = True
        self.previousbutton_event = pygame.USEREVENT + 17

        self.update_needed = None

        self.nextbutton = None
        self.nextbutton_width = 200
        self.nextbutton_height = 38

        self.nextbutton_event = pygame.USEREVENT + 18

    def resize(self, screen):
        Foreground.resize(self, screen)

        #  Create parameters for button
        self._rect = screen.get_rect() 
        self.nextbutton_x = self.foreground_rect.x+10
        self.nextbutton_y = self._rect.height-150  

        self.previousbutton_x = self.foreground_rect.width - 210
        self.previousbutton_y = self._rect.height-150

        if self.button_enabled:
            self.previousbutton = PushButton((self.previousbutton_x, self.previousbutton_y, self.previousbutton_width, self.previousbutton_height), self.previousbutton_event, label='PREVIOUS', parent=screen)
            self.previousbutton.enabled(True)

            self.nextbutton = PushButton((self.nextbutton_x, self.nextbutton_y, self.nextbutton_width, self.nextbutton_height), self.nextbutton_event, label='NEXT', parent=screen)
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
    def __init__(self, inmate_documents, selected_inmate):
        Foreground.__init__(self, "chosen_inmate")
        # self.selected_inmate_documents = inmate_documents[selected_inmate]
        self.document_view = DocumentsView(inmate_documents, selected_inmate)

    def resize(self, screen):
        Foreground.resize(self, screen)

    def paint(self, screen):
        Foreground.paint(self, screen)
        self.document_view.draw(self.foreground_rect, screen)
        self.document_view.update()


# class ChooseDocumentForeground(Foreground):
#     def __init__(self):
#         Foreground.__init__(self, "choose_document")

# class ChosenDocumentForeground(Foreground):
#     def __init__(self, document):
#         Foreground.__init__(self, "chosen_document")

class NoDocumentForeground(Foreground):
    def __init__(self):
        Foreground.__init__(self, "No_documents")


        
