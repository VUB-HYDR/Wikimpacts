# Wikimpacts
Wikimapcts is the first version of climate impact dataset creating by generative AI GPT4.0


## `open-source-LLMs` Branch

### Data
#### `300_events`: (245 main events datasamples after cleaning)
- `300_events_annotation.xlsx`: validation dataset
- `300_events_infobox.csv`: scraped infobox text from Wikipedia pages



### Scripts for Experiments
#### Latest Expreiments on Main Events Information Extraction
- `Llama2_Run_300_Events.py` and `Mistral_Run_300_Events.py`:
    - Data: 300 main events dataset 
    - Prompt: Infobox + full text updated
    - (With nicely designed experiment log)

- `Mistral_Main_Event_Pipeline.ipynb`: 
    - The ipynb version of the Mistral_Run_300_Events script 
    
#### Some previous experiments
- `Llama2_Reversed_Prompt.ipynb`:
    - Prompt: extracts a single object for each piece of impact information

- `Llama2_Subevent_Extractor.ipynb`:
    - Prompt: 
        1. Use a single prompt template to extract subevents
        2. Ask the model to first extract a list of locations and then extract the subevents related to these location



### Evaluation
- `comparison_300_events.ipynb`: 
    - Post-processing of the output from LLMs
    - Evaluation of Mistral and Llama2's performance on 300 main events dataset

- `comparer_300_events.py` and `normaliser.py`:
    - Slightly adapted Olof's original scripts


### Other
- `wiki_scraping.ipynb`:
    - Example usage of `wikipediaapi`