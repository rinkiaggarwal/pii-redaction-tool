import spacy
nlp = spacy.load("en_core_web_lg")
text = "KSH International Limited is a company. ICICI Securities and HDFC Bank are involved. Nuvama is also here."
for ent in nlp(text).ents:
    if ent.label_ == "ORG":
        print("ORG:", ent.text)
