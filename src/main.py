from rag.rag_class import Rag



def main():
    ragger = Rag("..//rag//images", "..//corpus//")
    print(ragger.query("Parental Controls"))



if __name__ == "__main__":
    main()