class Chunk:
    def __init__(self,header,text,images,page_start,page_end):
        self.text = text
        self.images = images
        self.header = header
        self.valid = True
        self.page_start = page_start
        self.page_end = page_end

    def is_valid(self):
        if self.text.count(".") > 40:
            self.valid = False

        

        return self.valid

    def to_json(self):
        return {
            "images": self.images,
            "header": self.header,
            "text": self.text,
            
            "page_start": self.page_start,
            "page_end": self.page_end,
            "validity": self.valid
            
        }
    
    def get_text(self):
        return self.text
    
    def get_images(self):
        return self.images
    
    def get_header(self):
        return self.header