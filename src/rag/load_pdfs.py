import fitz
import os

from .chunk_class import Chunk

#This function loads the pdfs and parses them into an array of chunk objects
#Follows bad practice and needs to be broken up but for now i've just imported it from the notebook where i made it


def parse_pdfs(path,image_folder):
    #path = "..//corpus//"
    #image_folder = "images/"
    os.makedirs(image_folder,exist_ok=True)
    buffer = ""
    data_frames = []

    for pdf_file in os.listdir(path):
        if not pdf_file.endswith(".pdf"):
            continue
        doc = fitz.open(path + pdf_file)
        file_name = os.path.splitext(pdf_file)[0]

        header = ""
        text_buffer = ""
        images = []
        last_images = [] #Found buffering images leads to them being on the correct chunk more often
        at_header = True
        page_start = 0
        
        for page_num, page in enumerate(doc):
            for img_index, img in enumerate(page.get_images(full=True), start=1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]




                if base_image["width"] > 250 and base_image["height"] > 250:
                    image_filename = f"{file_name}_p{page_num+1}_{img_index}.{image_ext}"
                    image_path = os.path.join(image_folder, image_filename)
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)

                    # Store the image path in the current section's image list
                    images.append(image_path)
            
            
            blocks = page.get_text("dict")["blocks"]
            

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = span["size"]  # font size
                        if not text:
                            continue
                        
                        if size >= 15:  # heuristic: large font = header
                            if at_header:
                                header += text
                            if not at_header:
                                if last_images == []:
                                    last_images = images
                                # data_frame = {
                                #     "Text": text_buffer,
                                #     "metadata": {
                                #         "Header": header,
                                #         "Images": last_images,
                                #         "page_start": page_start,
                                #         "page_end": page_num
                                #     }
                                #}
                                #data_frames.append(data_frame)
                                new_chunk = Chunk(header,text_buffer,images,page_start,page_num)
                                data_frames.append(new_chunk)
                                
                                header = text
                                text_buffer = ""
                                last_images = images
                                images = []
                                at_header = True
                                page_start = page_num
                            

                        else:
                            text_buffer += text
                            at_header = False

    #Dont forget the last one
    if text_buffer:
        # data_frame = {
        #     "Text": text_buffer,
        #     "metadata": {
        #     "Header": header,
        #     "Images": images,
        #     "page_start": page_start,
        #     "page_end": page_num
        #     }
        # }  
        # data_frames.append(data_frame)
        new_chunk = Chunk(header,text_buffer,last_images,page_start,page_num)
        data_frames.append(new_chunk)
    return data_frames


   

        
        

    