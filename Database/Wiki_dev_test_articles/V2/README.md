In Wikimpacts 2.0, we address single-event articles, multi-event articles, and non-English articles.

For single events, we utilize the same development and test sets as in version 1.0.

For multi-event articles, we employ the o3 mini model to determine the relevance of each item in tables and lists; the development and test sets used are those obtained after this filtering process.

For non-English articles, we use the gpt4o model to translate them into English. In addition to articles sourced from Wikidata, our French-speaking annotator also manually identified nine extra articles, which we have included in the evaluation set.