from .load_pdfs import parse_pdfs


from sentence_transformers import SentenceTransformer, util


class Rag:
    def __init__(self, image_folder, corpus_folder,*, model_name = "all-MiniLM-L6-v2"):
        self.image_folder = image_folder
        self.corpus_folder = corpus_folder
        self.model = SentenceTransformer(model_name) #Vector Embedding model
        print(f"Vector Embedding Model set to: {model_name}")
        print("Processing PDFs")
        self.Chunks = self.process_pdfs()
        print(f"Done Processing PDFs \nSuccesfully stored {len(self.Chunks)} Chunks")
        self.pdf_embeddings = self.embed_chunks()
        print(f"All Chunks Successfully embed in Length: {len(self.pdf_embeddings)}")

    def process_pdfs(self):
        return parse_pdfs(self.corpus_folder, self.image_folder)


    def embed_chunks(self):
        text_to_embed = [(f"Section: {chunk.get_header()} Text: {chunk.get_text()}") for chunk in self.Chunks] #Extract the header and texts from the chunks
        return self.model.encode(text_to_embed, convert_to_tensor = True)


    def print_chunks(self):
        for chunk in self.Chunks:
            print(chunk.to_json())

    def query(self,query):
        query_embedding = self.model.encode(query,convert_to_tensor=True) #Embed the query with same model
        similarities = util.cos_sim(query_embedding, self.pdf_embeddings)[0] 
        best_index = int(similarities.argmax())
        chunk = self.Chunks[best_index]
        data = {
            "header":chunk.get_header(),
            "text":chunk.get_text(),
            "images": chunk.get_images()
        }
        return data




