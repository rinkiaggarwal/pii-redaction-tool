import spacy
nlp = spacy.load("en_core_web_sm")
text = "The Offer Price, Vritti Chauhan or Bhavani Singh (as determined by the Lead Managers, in accordance with the SEBI ICDR Regulations), and Equity Shares by way of the Book Building Process, as stated under."
for ent in nlp(text).ents:
    if ent.label_ == "PERSON":
        print(f"PERSON: {ent.text}")
