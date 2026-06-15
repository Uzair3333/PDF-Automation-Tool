from pypdf import PdfReader

class extractor():

    def __init__(self, path):
        self.reader = PdfReader(path)
        self.pages = self.reader.pages
        self.text = ""
        self.no_of_pages = len(self.pages)
        self.first_page_text = ""
        self.success = True

    def text_extractor(self):
            if self.no_of_pages > 0:
                for page in self.pages:
                    txt = page.extract_text()
                    if txt is not None:
                        self.text += txt
                    else:
                        print("no text in pdf")
                        continue
                
                
                self.first_page_text = self.pages[0].extract_text()
            else:
                self.success = False
        

    def text_saver(self):
        try:
            with open("text.txt", 'w') as file:
                file.write(self.text)
        except Exception as e:
            print(e)
            self.success = False
        
    
    def output(self):
        if self.success == True:
            print("Succesfully wrote the whole text in text.txt.")
    
        print("-----First Page Text-----")
        print(self.first_page_text)

        print(f"Number of pages: {self.no_of_pages}")
