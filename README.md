# nlpslack

## Description

This is nlp sandbox with using slack messages.
There are some functions bellow.

- [x] Generate Wordcloud image each user
- [x] Generate Wordcloud weekly or monthly image
- [ ] Vectorize the content of each user's post and save as KVS
- [ ] Recommend users who are interested in a given word

## Features

- [x] Get messages via Slack API (require: API key)
- [x] Basic preparation
  - cleaning
  - morphological analysis
  - normalization
  - stop words removal
- [x] Visualization
  - Wordcloud
- [ ] Feature embedding
  - Word2vec
  - Doc2vec
- [x] Weighting factor
  - tf-idf
- [ ] Similarity search
  - with Word2vec
  - with Doc2vec
  - with Elasticsearch
  - ... etc

## Prerequisites

- install [Docker](https://docs.docker.com/get-docker/)
- Get [Slack API key](https://api.slack.com/)
  - channels api
  - users api

## Getting started

### Save Slack API key

Save as `nlpslack/data/conf/credentials.json`

```json
{
    "channel_api_key": "YOUR_CHANNELS_API_KEY",
    "user_api_key": "YOUR_USERS_API_KEY"
}
```

### Build Docker Image and execute container

```bash
$ docker-compose up -d
```

### Execute Python script

```bash
$ docker exec -it nlpslack python nlpslack/main.py [opt]
```

### Enter the container

```bash
$ docker exec -it nlpslack bash
```

## Usage

### (1) Generate Wordcloud image each user (comming soon)

```bash
$ docker exec -it nlpslack python nlpslack/main.py wc u
```

Then you can find wordcloud images in `(docker)dev/nlpslack/data/wc_by_usr`


### (2) Generate Wordcloud weekly or monthly image (comming soon)

```bash
# Generate Wordcloud weekly image
$ docker exec -it nlpslack python nlpslack/main.py wc t --term w
# Generate Wordcloud monthly image
$ docker exec -it nlpslack python nlpslack/main.py wc t --term m
```

Then you can find wordcloud images in `(docker)dev/nlpslack/data/wc_by_term`


### (3) Vectorize the content of each user's post and save as KVS (comming soon)

```bash
$ docker exec -it nlpslack python nlpslack/main.py vec -o KVS_PATH
```

Then you can find KVS file ( **\*.json** ) in KVS_PATH  
default KVS_PATH : `(docker)dev/nlpslack/data/content_features.json`

### (4) Recommend users who are interested in a given word (comming soon)

**require: (3) is done**

If execute, I show recommended user's name and similarity score.

```bash
$ docker exec -it nlpslack python nlpslack/main.py search --word SAMPLE
$ Recommended users are bellow ...
$ Key word: "SAMPLE"
$ 1. User03: 0.8799
$ 2. User11: 0.7653
$ 3. User05: 0.3442
```

### (5) View command args

```bash
$ docker exec -it nlpslack python nlpslack/main.py -h
```
