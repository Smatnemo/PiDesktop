import pygame

# Custom events for documents 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class InmateRow(object):
    def __init__(self, inmate_number, documents):
        self.inmate_number = inmate_number 
        self.documents = documents

    def draw(self):
        pass
    
    def update(self):
        pass 

    def handle_events(self, events):
        pass

    def hovered(self, event):
        if not event:
            return None
        if self.button_rect.collidepoint(event.pos) and self.button_enabled:
            return True 
        else:
            return None        

    def clicked(self, event):
        self.button_text = self.font.render(self.label, True, self.button_color)
        width, height = self.font.size(self.label)
        self.button_rect.width, self.button_rect.height = width+6, height+6
        
        if self.button_enabled:
            if self.hovered(event):
                pygame.draw.rect(self.screen, 'dark gray', self.button_rect)
                clicked = self.clicked(event)
                if clicked == 'BUTTONDOWN':
                    pygame.draw.rect(self.screen, 'black', self.button_rect)
                elif clicked == 'BUTTONUP':
                    pygame.draw.rect(self.screen, 'dark gray', self.button_rect)
            else:
                pygame.draw.rect(self.screen, 'light gray', self.button_rect)
        else:
            pygame.draw.rect(self.screen, 'blue', self.button_rect)
        self.screen.blit(self.button_text, self.coord)
        


class DocumentRow(object):
    def __init__(self, document:tuple):
        pass

    def draw(screen):
        pass

    def handle_events(self, events):
        pass 

    def hovered(self, event):
        pass 

    def clicked(self, event):
        pass



class DocumentsView(object):
    def __init__(self, documents):
        self.document_rows = [DocumentRow(document) for document in documents]
    
    def draw(self, screen, foreground_rect):
        for document_row in self.document_rows:
            document_row.draw(screen)


class InmateDocumentsView(object):
    def __init__(self, inmate_documents):
        self.inmate_numbers = list(inmate_documents.keys())
        self.inmate_rows = [InmateRow(inmate_number, inmate_documents[inmate_number]) for inmate_number in self.inmate_numbers]


    def draw(self, foreground_rect, screen):
        for inmate_row in self.inmate_rows:
            inmate_row.draw(screen, foreground_rect)

    def update(self):
        pass




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