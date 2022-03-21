------------------------------------------------------------
Proj 1: Readme 
Matthew Duran (md3420)
Ethan Garry (epg2136)
------------------------------------------------------------

Current Status:

Run ./getSpanBert.sh 
	This should create a folder called SpanBert (not uploaded to GH — too big)
	MD: we should probably do the sourcing within the file, and have like a pre-program and post-program shell script
		* this is a lateeeer issue
		
Check in SpanBert/pretrained_spanbert and SpanBert/pytorch_pretrained_bert. If there is nothing in these folders run the following commands:
cd SpanBert
./download_finetuned.sh

You can now run:
Source setup.sh
./test.sh

In spanbert.py

Comment out this line:

def __init__(self, pretrained_dir, model="spanbert-base-cased"):
 And replace with:
def __init__(self, pretrained_dir, model="bert-base-cased"):

Not sure if this is ok, but spanbert-base-cased doesn’t appear to be a model anymore…? Maybe ask about on Ed.

Add:

'SUBJ=LOCATION': 'unused24'

To the special_tokens dictionary.

Right now the application makes request to google —> parses (tokenizer.py) it —> limits text to 20k chars (tokenizer.py) —> 
attempts to extract relations using “extract_relations” in the spacy_help_functions.py but keeps running into bugs…
