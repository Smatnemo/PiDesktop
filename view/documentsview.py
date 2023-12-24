# from tkinter.colorchooser import Chooser
import pygame

from LDS import fonts, pictures
from LDS.config import PiConfigParser
from LDS.media import get_filename

# Custom events for documents 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CHOSEEVENT = pygame.USEREVENT + 16

class InmateRow(object):
    total_pages_x = None
    row_y = None
    def __init__(self, inmate_number=None, documents:list=None, row_number:int=0, config=None, _d=None):
        self._d = _d
        self.documents = documents
        self.row_height = self._d['row_height']
        self.inmate_rect = None
        self.row_color = None 
        self.row_text_color = BLACK
        self.row_text_size = 32

        self.row_num = row_number 
        self.row_num_coord = None
            
        self.num_coord = None
        self.inmate_number = inmate_number
        self.inmate_num_coord = None
        self.total_pages = 0
        if self.documents: 
            for document in self.documents:
                self.total_pages += document[8]
            self.num = len(documents)
            self.row_num = row_number + 1
            self.inmate_identifier = str(self.documents[0][19][0])+str(inmate_number)
        #self.row_num_text = row_number + 1

        if not self.inmate_number:
            self.inmate_identifier = "Inmate Identifier"
            self.num = "Document count"
            #self.row_num_text = "S/N"
            self.total_pages = "Total Pages"

        self.chosen = False


        self.font = pygame.font.Font(fonts.CURRENT, self.row_text_size)

    def draw(self, foreground_rect, screen, event, offset):
        if self.documents and self.row_num % offset == 0:
            self.row_num = offset 
        else:
            self.row_num = self.row_num % offset

        # Move to dict
        gap=24
        pad=5
        r_radius=20
        r_border=15

        self.inmate_rect = pygame.Rect(foreground_rect.x+gap, foreground_rect.y+60*(self.row_num), foreground_rect.width-(gap*2), self.row_height)
        
        if self.documents:
            pygame.draw.rect(screen, 'white', self.inmate_rect)
            clicked = self.clicked(screen, event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'dark grey', self.inmate_rect)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'light gray', self.inmate_rect)
            
        pygame.draw.rect(screen, 'black', self.inmate_rect, r_border, border_radius=r_radius)
        
        #screen.blit(self.text_surface(self.row_num_text)[0], (foreground_rect.x+14,foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.inmate_identifier)[0], (foreground_rect.x+gap+pad, foreground_rect.y+60*(self.row_num)))
        screen.blit(self.text_surface(self.num)[0], ((foreground_rect.width//100)*40+gap+pad, foreground_rect.y+60*(self.row_num)))
        total_pages_count_x = foreground_rect.width-self.text_surface(self.total_pages)[1]-14
        InmateRow.set_total_pages_x(foreground_rect)
        if InmateRow.total_pages_x is not None and total_pages_count_x < InmateRow.total_pages_x:
            InmateRow.total_pages_x = total_pages_count_x
        screen.blit(self.text_surface(self.total_pages)[0], (InmateRow.total_pages_x, foreground_rect.y+60*(self.row_num)+14))

    def text_surface(self, text):
        text = str(text)
        text_surface = self.font.render(text, True, self.row_text_color)
        width, height = self.font.size(text)
        return text_surface, width, 

    @classmethod
    def set_total_pages_x(cls, foreground_rect):
        if InmateRow.total_pages_x is None:
            cls.total_pages_x = foreground_rect.width
    
    @classmethod 
    def set_row_y(cls, foreground_rect, offset):
        if cls.row_y is None:
            cls.row_y = foreground_rect.y
        

    def hovered(self, event):
        if not event:
            return None
        try:
            if self.inmate_rect.collidepoint(event.pos):
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
        if (event.type==pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERDOWN) and self.inmate_rect.collidepoint(event.pos):  
            return 'BUTTONDOWN'
        if (event.type==pygame.MOUSEBUTTONUP or event.type==pygame.FINGERUP) and self.inmate_rect.collidepoint(event.pos):
            pygame.event.post(pygame.event.Event(CHOSEEVENT))
            self.chosen = True
            return 'BUTTONUP'
        else:
            return None
        


class DocumentRow(object):
    page_count_x = None

    def __init__(self, document:tuple=None, row_number:int=0, _d=None, config=None):
        self._d=_d
        self.document_rect = None
        self.row_height = self.row_height = self._d['row_height']
        self.row_num = row_number
        self.row_num_text = "S/N"
        self.document_name = "Document Name"
        self.status = "Status"
        self.page_count = "Number of pages"
        if document:
            self.document_name = str(document[20][:13])
            self.status = document[11]
            self.row_num = row_number + 1
            self.row_num_text = self.row_num
            self.page_count = document[8]

            
        self.document = document

        # Change logic to write out the statement relating in the third column
        self.row_text_size = 32
        self.row_text_color = BLACK
        self.font = pygame.font.Font(fonts.CURRENT, self.row_text_size)
        
        self.chosen = False
        
    def draw(self, foreground_rect, screen, event, offset):
        if self.document and self.row_num % offset == 0:
            self.row_num = offset 
        else:
            self.row_num = self.row_num % offset
        self.document_rect = pygame.Rect(foreground_rect.x, foreground_rect.y+60*(self.row_num), foreground_rect.width, self.row_height)
        
        if self.document:
            pygame.draw.rect(screen, 'light gray', self.document_rect)
            clicked = self.clicked(screen, event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'light gray', self.document_rect)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'white', self.document_rect)
        

        pygame.draw.rect(screen, 'black', self.document_rect, 2) 
        
        #screen.blit(self.text_surface(self.row_num_text)[0], (foreground_rect.x+14,foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.document_name)[0], (foreground_rect.x+14, foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.status)[0], (foreground_rect.width//2, foreground_rect.y+60*(self.row_num)+14))
        page_count_title_x = foreground_rect.width-self.text_surface(self.page_count)[1]-10

        DocumentRow.set_page_count_x(foreground_rect)
        if DocumentRow.page_count_x is not None and page_count_title_x < DocumentRow.page_count_x:
            DocumentRow.page_count_x = page_count_title_x
        screen.blit(self.text_surface(self.page_count)[0], (DocumentRow.page_count_x, foreground_rect.y+60*(self.row_num)+14))


    def text_surface(self, text):
        text = str(text)
        text_surface = self.font.render(text, True, self.row_text_color)
        width, height = self.font.size(text)
        return text_surface, width, height    
    
    @classmethod 
    def set_page_count_x(cls, foreground_rect):
        if DocumentRow.page_count_x is None:
            cls.page_count_x = foreground_rect.width

    def hovered(self, event):
        if not event:
            return None
        try:
            if self.document_rect.collidepoint(event.pos):
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
        if (event.type==pygame.MOUSEBUTTONDOWN or event.type==pygame.FINGERDOWN) and self.document_rect.collidepoint(event.pos):  
            return 'BUTTONDOWN'
        if (event.type==pygame.MOUSEBUTTONUP or event.type==pygame.FINGERUP) and self.document_rect.collidepoint(event.pos):
            pygame.event.post(pygame.event.Event(CHOSEEVENT))
            self.chosen = True
            return 'BUTTONUP'
        else:
            return None



class DocumentsView(object):
    def __init__(self, inmate_documents, selected, _d, config):
        self._d = _d
        self._c = config
        self.inmate_documents = inmate_documents
        self.documents = inmate_documents[selected]
        self.document_rows = [DocumentRow(document, doc_num, _d, config) for doc_num, document in enumerate(self.documents)]
        self.update_needed = None
        self.chosendocumentrow = None 
        self.titlerow = DocumentRow(_d=self._d, config=self._c)
        self.document_rows.insert(0, self.titlerow)

        self.gap = _d["h"]-_d["footer"]-_d["header"]
        self.offset = int(self.gap//_d["row_height"])
        
        self._offset = self.offset - 1
        self.start = 1
        self.end = self.start + self._offset
        self.change_view = None
    
    def draw(self, foreground_rect, screen):
        self.document_rows[0].draw(foreground_rect, screen, self.update_needed, self.offset)
        if self.change_view:
            if self.change_view.change_view=='next' and self.end < len(self.document_rows):
                self.start = self.end
                self.end = self.start + self._offset
                self.change_view = None
            elif self.change_view.change_view=='previous' and (self.start - self._offset) > 0:
                self.start = self.start - self._offset
                self.end = self.end - self._offset
                self.change_view = None
        for document_row in self.document_rows[self.start:self.end]:
            document_row.draw(foreground_rect, screen, self.update_needed, self._offset)

    def update(self):
        # When button is clicked, return the inmate number
        for row in self.document_rows:
            if row.chosen == True:
                self.chosendocumentrow = row
                row.chosen = False

    def update_view(self, inmate_number, blob, decrypted=None, printed=None):
        doc = list(self.chosendocumentrow.document)
        if decrypted:
            doc[13] = 1
              
        if printed:
            doc[12] = 1
            doc[11] = 'printed'
            doc[16] = blob
            doc = tuple(doc)

        self.chosendocumentrow.document = doc 

        for i, document in enumerate(self.documents):
            if document[0] == self.chosendocumentrow.document[0]:
                self.documents[i] = self.chosendocumentrow.document

        self.inmate_documents[inmate_number] = self.documents            


class InmateDocumentsView(object):
    def __init__(self, inmate_documents, _d, config):
        self.inmate_numbers = list(inmate_documents.keys())
        self._d = _d
        self._c = config
        self.inmate_rows = [InmateRow(inmate_number, inmate_documents[inmate_number], row_number, _d=self._d, config=config) for row_number, inmate_number in enumerate(self.inmate_numbers)]
        self.update_needed = None
        self.choseninmaterow = None
        self.titlerow = InmateRow(_d=self._d, config=self._c)
        self.inmate_rows.insert(0, self.titlerow)        
                
        self.gap = self._d['h']-(int(self._d["row_height"]*2)) - (int(self._d["btn_handf_y"]*2))
        self.offset = int(self.gap//self._d["row_height"])
        
        self._offset = self.offset - 1
        self.start = 1
        self.end = self.start + self._offset
        self.change_view = None
        
    def draw(self, foreground_rect, screen):
        self.inmate_rows[0].draw(foreground_rect, screen, self.update_needed, self.offset)
        if self.change_view:
            if self.change_view.change_view=='next' and self.end < len(self.inmate_rows):
                self.start = self.end
                self.end = self.start + self._offset                 
                self.change_view = None
            elif self.change_view.change_view=='previous' and (self.start - self._offset) > 0:
                self.start = self.start - self._offset
                self.end = self.end - self._offset
                self.change_view = None
        # print("This is the offset", self.offset)
        for inmate_row in self.inmate_rows[self.start:self.end]:
            inmate_row.draw(foreground_rect, screen, self.update_needed, self._offset)

    def update(self):
        # When button is clicked, return the inmate number
        for row in self.inmate_rows:
            if row.chosen == True:
                self.choseninmaterow = row
                row.chosen = False

    def limit_view(self):
        """update x_limit and y_limit
        """
        # Divide the list based on the available height of the screen
        




def main():
    clock = pygame.time.Clock()
    done = False 

    while not done:
        events = list(pygame.event.get())
        
        pygame.display.update()
        clock(60)
    pygame.quit()


if __name__ == "__main__":
    main()