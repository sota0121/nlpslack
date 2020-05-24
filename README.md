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
- [x] Feature embedding
  - Word2vec
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

## Examples

### Create wordcloud images by users

```bash
$ docker exec -it nlpslack python nlpslack/main.py 0
```

**or**

```bash
$ docker exec -it nlpslack bash
root@xxx:/dev> python nlpslack/main.py 0
```

Then you can find wordcloud images in `(docker)dev/nlpslack/data/wc_by_usr`

### Create weekly wordcloud image

```bash
$ docker exec -it nlpslack python nlpslack/main.py 1 --term w
```

**or**

```bash
$ docker exec -it nlpslack bash
root@xxx:/dev> python nlpslack/main.py 1 --term w
```

### Check option

```bash
$ docker exec -it nlpslack python nlpslack/main.py -h
```

**or**

```bash
$ docker exec -it nlpslack bash
root@xxx:/dev> python nlpslack/main.py -h
```