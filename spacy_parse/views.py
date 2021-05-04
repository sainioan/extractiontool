from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from project.models import Pdf
from document.models import Pdf
from document.pdf_reader import pdf_to_txt
import spacy
from spacy.symbols import nsubj, VERB
import en_core_web_lg
import json
#from django.views.generic.edit import CreateView
from django.views.decorators.http import require_POST, require_GET
#from django.contrib.sessions.models import Session
#from django.http import JsonResponse
#from django.http import HttpResponse



current_pdf_id = []
@login_required
def parse(request, pk):
    parse_result = {}
    current_pdf_id.clear()
    current_pdf_id.append(pk)
    # if request.method == 'POST':
    nlp = spacy.load("en_core_web_lg")

    pdf = Pdf.objects.get(pk=pk)
    file_path = pdf.filex.path

    pdf_to_txt(pdf.filex.name, file_path)

    with open(file_path+".txt", 'r', encoding="utf-8") as file:
        text = file.read().replace('\n', ' ')

    # nlp.add_pipe("merge_entities")
    # nlp.add_pipe("merge_noun_chunks")

    # ruler = nlp.add_pipe("entity_ruler", before="ner").from_disk(
    #         "./patterns_scientificNames.jsonl")

    doc = nlp(text)

    sentences_with_traits = []
    trait_words = ["weight",
                       "height",
                       "width",
                       "breadth",
                       "length",
                       "mass",
                       "body",
                       "tail",
                       "area",
                       "thickness",
                       "constriction",
                       "count",
                       "number",
                       "ratio",
                       "head-body",
                       "longevity",
                       "litter",
                       "size",
                       "range",
                       "index",
                       "ear",
                       "forearm"
                       ]
    #string_sentences = []
    for sentence in doc.sents:
        for trait in trait_words:
            if trait in sentence.text:
                sentences_with_traits.append(sentence)
                break

    trait_text = ""
    for sent in sentences_with_traits:
        #string_sentences.append(sent.text)
        trait_text += sent.text

    nlp.add_pipe("merge_entities")
    nlp.add_pipe("merge_noun_chunks")

    ruler = nlp.add_pipe("entity_ruler", before="ner").from_disk(
            "./patterns_scientificNames.jsonl")


    trait_doc = nlp(trait_text)
    json_sentences = []
    for sentence in trait_doc.sents:
        ents_in_sentence = [] 
        for entity in trait_doc.ents:
            start = sentence.find(entity)
            end = start + len(entity.text) 
            # tarvitaan erikseen luuppi joka kerää
            # entityt lauseesta
            
            ents_in_sentence.append(entity)
            json_sentence = {
                "content" : sentence.text, 
                "annotation" : [
                    {
                        "label": [entity.label_],
                        "points": [{"text": entity.text, "start": start, "end": end}],
                    }
                ]
            }
            print(json_sentence)
            json_sentences.append(json_sentence)

    quantity_ner_labels = ["QUANTITY", "MONEY", "PERCENT", "CARDINAL"]
    scientificnames = [
        ent.text for ent in trait_doc.ents if ent.label_ == "SCIENTIFICNAME"]
    quantities = [
        ent.text for ent in trait_doc.ents if ent.label_ in quantity_ner_labels]

    entities = []
    for entity in trait_doc.ents:
        entities.append(entity)
    #number_of_sentences = len(sentences_with_traits)
    #data = trait_doc.to_json()
    #json_sentences = json.dumps(string_sentences)
    parse_result = {
                    'sentences': sentences_with_traits, 
                    'scientificnames': scientificnames, 
                    'quantities': quantities,
                    'entities' : entities
                    }
        
    return render(request, 'parse.html', parse_result)
