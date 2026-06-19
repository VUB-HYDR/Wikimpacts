*** This is the classification process for English Wikipedia articles related to climate disasters.***
#Files description
[] Classfication_wikipedia.py is a script used for training the BERT model, and the training data is shuffled_training_dataset.csv
[] DistilBertForSequenceClassification_WIKI_Natural_disaster is our trained model, and in https://huggingface.co/liniiiiii/DistilBertForSequenceClassification_WIKI_Natural_disaster
[] wikipedia_dataset_preforclassify_20240229.csv contains all articles we collected using the keywords searching
[] Classifier_implement.py is a script to implement the classification model, the command you can refer to use this model is:
```shell
poetry run python3 BERT_Classification_EN_Wikipedia/Classifier_implement.py  --filename wikipedia_dataset_preforclassify_20240229.csv  --file_dir BERT_Classification_EN_Wikipedia
```
It takes long time to run for the all articles we collected, and we recommand to run it for new articles in Wikipedia after day 20240229.
