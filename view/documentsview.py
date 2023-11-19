from tkinter.colorchooser import Chooser
import pygame

# Custom events for documents 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CHOSEEVENT = pygame.USEREVENT + 16

class InmateRow(object):
    def __init__(self, inmate_number, documents, row_number):

        self.documents = documents
        self.row_height = 60
        self.inmate_rect = None
        self.row_color = None 
        self.row_text_color = BLACK
        self.row_text_size = 32

        self.row_num = row_number 
        self.row_num_coord = None

        self.num = len(documents)
        self.num_coord = None

        self.inmate_number = inmate_number 
        self.inmate_num_coord = None

        self.chosen = False


        self.font = pygame.font.Font('freesansbold.ttf', self.row_text_size)

    def draw(self, foreground_rect, screen, event):
        self.inmate_rect = pygame.Rect(foreground_rect.x, foreground_rect.y+60*(self.row_num), foreground_rect.width, self.row_height)
        # pygame.draw.rect(screen, 'dark gray', self.inmate_rect)
        
        if self.hovered(event):
            pygame.draw.rect(screen, 'dark gray', self.inmate_rect)
            clicked = self.clicked(event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'black', self.inmate_rect)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'dark gray', self.inmate_rect)
        else:
            pygame.draw.rect(screen, 'light gray', self.inmate_rect)
        
        screen.blit(self.text_surface(self.row_num+1), (foreground_rect.x+14,foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.inmate_number), (foreground_rect.x+54, foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.num), (foreground_rect.width//2, foreground_rect.y+60*(self.row_num)+14))

    def text_surface(self, text):
        text = str(text)
        text_surface = self.font.render(text, True, self.row_text_color)
        width, height = self.font.size(text)
        return text_surface 
    

    def hovered(self, event):
        if not event:
            return None
        if self.inmate_rect.collidepoint(event.pos):
            return True 
        else:
            return None        

    def clicked(self, event):
        if not event:
            return None
        if event.type==pygame.MOUSEBUTTONDOWN and self.inmate_rect.collidepoint(event.pos):  
            return 'BUTTONDOWN'
        if event.type==pygame.MOUSEBUTTONUP and self.inmate_rect.collidepoint(event.pos):
            pygame.event.post(pygame.event.Event(CHOSEEVENT))
            self.chosen = True
            return 'BUTTONUP'
        else:
            return None
        


class DocumentRow(object):
    def __init__(self, document:tuple, row_number:int):
        self.document_rect = None
        self.row_height = 60
        self.row_num = row_number
        self.document_name = "Document"+str(document[9])+str(self.row_num+1)
        # Change logic to write out the statement relating in the third column
        self.status = document[-1]
        self.row_text_size = 32
        self.row_text_color = BLACK
        self.font = pygame.font.Font('freesansbold.ttf', self.row_text_size)
        self.document = document
        self.chosen = False
        

    def draw(self, foreground_rect, screen, event):
        self.document_rect = pygame.Rect(foreground_rect.x, foreground_rect.y+60*(self.row_num), foreground_rect.width, self.row_height)

        if self.hovered(event):
            pygame.draw.rect(screen, 'dark gray', self.document_rect)
            clicked = self.clicked(event)
            if clicked == 'BUTTONDOWN':
                pygame.draw.rect(screen, 'black', self.document_rect)
            elif clicked == 'BUTTONUP':
                pygame.draw.rect(screen, 'dark gray', self.document_rect)
        else:
            pygame.draw.rect(screen, 'light gray', self.document_rect)

        screen.blit(self.text_surface(self.row_num+1), (foreground_rect.x+14,foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.document_name), (foreground_rect.x+54, foreground_rect.y+60*(self.row_num)+14))
        screen.blit(self.text_surface(self.status), (foreground_rect.width//2, foreground_rect.y+60*(self.row_num)+14))


    def text_surface(self, text):
        text = str(text)
        text_surface = self.font.render(text, True, self.row_text_color)
        width, height = self.font.size(text)
        return text_surface     

    def hovered(self, event):
        if not event:
            return None
        if self.document_rect.collidepoint(event.pos):
            return True 
        else:
            return None 

    def clicked(self, event):
        if not event:
            return None
        if event.type==pygame.MOUSEBUTTONDOWN and self.document_rect.collidepoint(event.pos):  
            return 'BUTTONDOWN'
        if event.type==pygame.MOUSEBUTTONUP and self.document_rect.collidepoint(event.pos):
            pygame.event.post(pygame.event.Event(CHOSEEVENT))
            self.chosen = True
            return 'BUTTONUP'
        else:
            return None



class DocumentsView(object):
    def __init__(self, inmate_documents, selected):
        self.inmate_documents = inmate_documents
        documents = inmate_documents[selected]
        self.document_rows = [DocumentRow(document, doc_num) for doc_num, document in enumerate(documents)]
        self.update_needed = None
        self.chosendocumentrow = None 
    
    def draw(self, foreground_rect, screen):
        for document_row in self.document_rows:
            document_row.draw(foreground_rect, screen, self.update_needed)

    def update(self):
        # When button is clicked, return the inmate number
        for row in self.document_rows:
            if row.chosen == True:
                self.chosendocumentrow = row
                row.chosen = False

class InmateDocumentsView(object):
    def __init__(self, inmate_documents):
        self.inmate_numbers = list(inmate_documents.keys())
        self.inmate_rows = [InmateRow(inmate_number, inmate_documents[inmate_number], row_number) for row_number, inmate_number in enumerate(self.inmate_numbers)]
        self.update_needed = None
        self.choseninmaterow = None

    def draw(self, foreground_rect, screen):
        for inmate_row in self.inmate_rows:
            inmate_row.draw(foreground_rect, screen, self.update_needed)

    def update(self):
        # When button is clicked, return the inmate number
        for row in self.inmate_rows:
            if row.chosen == True:
                self.choseninmaterow = row
                row.chosen = False




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