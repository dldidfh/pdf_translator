from docx import Document

class WordManager():
    def __init__(self, save_path):
        self.save_path = save_path
        self.doc = Document()
    
    def add_para(self, text):
        self.doc.add_paragraph(text)


    def page_sep(self):
        self.doc.add_page_break()

    def save(self):
        self.doc.save(self.save_path)
