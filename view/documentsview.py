# from tkinter.colorchooser import Chooser
import pygame

from LDS import fonts, pictures
from LDS.config import PiConfigParser
from LDS.media import get_filename

# Custom events for documents 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CHOSEEVENT = pygame.USEREVENT + 16

# Row to be inherited by every other row
class Row(object):
    pass
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
        self.row_text_size = 22

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
        gap=20
        pad=5
        r_radius=20
        r_border=10
        

        self.inmate_rect = pygame.Rect(foreground_rect.x+gap, foreground_rect.y+(self.row_height+10)*(self.row_num), foreground_rect.width-(gap*2), self.row_height+pad+2)
        
        if not self.documents:
            pygame.draw.rect(screen, (101,101,103), self.inmate_rect, border_radius=r_radius)
            pygame.draw.rect(screen, (33,33,35), self.inmate_rect, r_border, border_radius=r_radius)
            self.row_text_color = (255,255,255)
            
        if self.documents:
            pygame.draw.rect(screen, 'white', self.inmate_rect, border_radius=r_radius)            
            pygame.draw.rect(screen, 'black', self.inmate_rect, r_border, border_radius=r_radius)
            
            clicked = self.clicked(screen, event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'white', self.inmate_rect, border_radius=r_border)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'light gray', self.inmate_rect, border_radius=r_border)
            

        
        
        screen.blit(self.text_surface(self.inmate_identifier)[0], (foreground_rect.x+(gap*2), foreground_rect.y+r_border+pad+2+((60)*(self.row_num))))
        screen.blit(self.text_surface(self.num)[0], ((foreground_rect.width//100)*30+gap+pad, foreground_rect.y+r_border+pad+2+((60)*(self.row_num))))
        total_pages_count_x = foreground_rect.width-self.text_surface(self.total_pages)[1]-gap
        InmateRow.set_total_pages_x(foreground_rect)
        if InmateRow.total_pages_x is not None and total_pages_count_x < InmateRow.total_pages_x:
            InmateRow.total_pages_x = total_pages_count_x
        screen.blit(self.text_surface(self.total_pages)[0], (InmateRow.total_pages_x-(gap*2), foreground_rect.y+r_border+pad+2+((60)*(self.row_num))))

    def text_surface(self, text):
        text = str(text)
        text_surface = self.font.render(text, True, self.row_text_color)
        width, height = self.font.size(text)
        return text_surface, width

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

    def __init__(self,  document:tuple=None, row_number:int=0, _d=None, config=None, row_num_text="",document_name="", status="", num_of_pages=""):
        self._d=_d
        self.document_rect = None
        self.row_height = self.row_height = self._d['row_height']
        self.row_num = row_number
        self.row_num_text = row_num_text
        self.document_name = document_name
        self.status = status
        self.page_count = num_of_pages
        self.document = document 
        if document:
            self.document_name = str(document[20][:13])
            self.status = document[11]
            self.row_num = row_number + 1
            self.row_num_text = self.row_num
            self.page_count = document[8]            
            self.document = document        

        # Change logic to write out the statement relating in the third column
        self.row_text_color = BLACK
        self.row_text_size = 22
        self.font = pygame.font.Font(fonts.CURRENT, self.row_text_size)
        
        self.chosen = False
        
    def draw(self, foreground_rect, screen, event, offset):
        # Move to dict
        gap=20
        pad=5
        r_radius=20
        r_border=10  

        if self.document and self.row_num % offset == 0:
            self.row_num = offset 
        else:
            self.row_num = self.row_num % offset    
                
        self.document_rect = pygame.Rect(foreground_rect.x+gap, foreground_rect.y+(self.row_height+10)*(self.row_num), foreground_rect.width-(gap*2), self.row_height+pad+2)    
        
        if not self.document:
            pygame.draw.rect(screen, (101,101,103), self.document_rect, border_radius=r_radius)
            pygame.draw.rect(screen, (33,33,35), self.document_rect, r_border, border_radius=r_radius)
            self.row_text_color = (255,255,255)

        if self.document:
            pygame.draw.rect(screen, 'white', self.document_rect, border_radius=r_radius)            
            pygame.draw.rect(screen, 'black', self.document_rect, r_border, border_radius=r_radius)            
            clicked = self.clicked(screen, event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'white', self.document_rect)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'light grey', self.document_rect)
                        
        screen.blit(self.text_surface(self.document_name)[0], (foreground_rect.x+(gap*2), foreground_rect.y+r_border+pad+2+((60)*(self.row_num))))
        screen.blit(self.text_surface(self.status)[0], ((foreground_rect.width//100)*30+gap+pad, foreground_rect.y+r_border+pad+2+((60)*(self.row_num))))
        page_count_title_x = foreground_rect.width-self.text_surface(self.page_count)[1]-gap

        DocumentRow.set_page_count_x(foreground_rect)
        if DocumentRow.page_count_x is not None and page_count_title_x < DocumentRow.page_count_x:
            DocumentRow.page_count_x = page_count_title_x

        screen.blit(self.text_surface(self.page_count)[0], (DocumentRow.page_count_x-(gap*2), foreground_rect.y+r_border+pad+2+(60)*(self.row_num)))        
        

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


class StaffRow(DocumentRow):
    def __init__(self, document:tuple=None, row_number:int=0, _d=None, config=None, row_num_text="",document_name="", status="", num_of_pages=""):
        self._d=_d
        self.document_rect = None
        self.row_height = self.row_height = self._d['row_height']
        self.row_num = row_number
        self.row_num_text = row_num_text
        self.document_name = document_name
        self.status = status
        self.page_count = num_of_pages
        
        if document:
            self.document_name = str(document[0])
            self.row_num = row_number + 1
            self.row_num_text = self.row_num
            self.staff = document
        self.document = document
        # Change logic to write out the statement relating in the third column
        self.row_text_size = 22

        self.row_text_color = BLACK
        self.font = pygame.font.Font(fonts.CURRENT, self.row_text_size)

        self.chosen = False
    def draw(self, foreground_rect, screen, event, offset):
        DocumentRow.draw(self, foreground_rect, screen, event, offset)


# View to be inherited by other Views
class View(object):
    def __init__(self):

        self.gap = self._d['h']-(int(self._d["row_height"]*2)) - (int(self._d["btn_handf_y"]*2))
        self.offset = int(self.gap//self._d["row_height"])
      
        self._offset = self.offset - 1
        self.start = 1
        self.end = self.start + self._offset
        self.change_view = None
    
    def draw(self, foreground_rect, screen):
        pass


class DocumentsView(object):
    def __init__(self, inmate_documents, selected, _d, config):
        self._d = _d
        self._c = config
        self.inmate_documents = inmate_documents
        self.documents = inmate_documents[selected]
        self.document_rows = [DocumentRow(document, doc_num, _d, config) for doc_num, document in enumerate(self.documents)]
        self.update_needed = None
        self.chosendocumentrow = None 
        self.titlerow = DocumentRow(_d=self._d, config=self._c, row_num_text="S/N", document_name="Document", status="Status", num_of_pages="Number of Pages")
        self.document_rows.insert(0, self.titlerow)

        self.gap = _d["h"]-_d["footer"]-_d["header"]
        #self.offset = int(self.gap//_d["row_height"])
        self.offset = int(5)

        
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
        self.offset = int(5)
        
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
        

class StaffView(DocumentsView):
    def __init__(self, staff_dict, selected, _d, _c):
        self._d = _d
        self._c = _c
        self.inmate_documents = staff_dict
        self.documents = staff_dict[selected]
        self.document_rows = [StaffRow(document, doc_num, self._d, self._c) for doc_num, document in enumerate(self.documents)]
        self.update_needed = None
        self.chosenStaffRow = None 
        self.titlerow = StaffRow(_d=self._d, config=self._c, row_num_text="S/N", document_name="Staff Number")
        self.document_rows.insert(0, self.titlerow)
        
        self.gap = self._d['h']-(int(self._d["row_height"]*2)) - (int(self._d["btn_handf_y"]*2))
        self.offset = int(self.gap//self._d["row_height"])
        
        self._offset = self.offset - 1
        self.start = 1
        self.end = self.start + self._offset
        self.change_view = None

    def draw(self, foreground_rect, screen):
        DocumentsView.draw(self, foreground_rect, screen)

    # When button is clicked, return the inmate number
    def update(self):
        for row in self.document_rows:
            if row.chosen == True:
                self.chosenStaffRow = row
                row.chosen = False
