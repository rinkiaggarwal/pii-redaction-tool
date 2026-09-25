import re
import spacy

nlp = spacy.load('en_core_web_lg')

text = "Contact Person: Eric Bacha/ Sachin Gawade/ Pravin Teli/ Siddharth Jadhav/ Tushar Gavankar is here."

def process_delimited_names(text):
    entities = []
    # Match sequences of Title Case words separated by /, ,, or ;
    # E.g. "Eric Bacha/ Sachin Gawade"
    pattern = r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*\s*(?:[/,;]\s*[A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)+)\b'
    for match in re.finditer(pattern, text):
        span_text = match.group(1)
        # split by delimiters
        segments = re.split(r'[/,;]', span_text)
        current_idx = match.start(1)
        for seg in segments:
            seg_stripped = seg.strip()
            if seg_stripped:
                # evaluate as independent candidate
                doc = nlp(seg_stripped)
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        # calculate exact start/end
                        start_in_seg = seg.find(ent.text)
                        ent_start = current_idx + start_in_seg
                        ent_end = ent_start + len(ent.text)
                        entities.append((ent.label_, ent.text, ent_start, ent_end))
            current_idx += len(seg) + 1 # +1 for the delimiter
    return entities

print(process_delimited_names(text))
