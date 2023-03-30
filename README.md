# European Olfactory Knowledge Graph

Series of scripts, procedures and dumps for deploying the EOKG on GraphDB and Docker.

#### Requirements

- Docker
- NodeJS
- Python

## GraphDB

Download the latest version of GraphDB free by registering on the [product website](https://www.ontotext.com/products/graphdb/graphdb-free/). Place the obtained zip in the `graphdb` folder.
We will use version 10.1.1.

If you have the new Mac M1, run:

    export DOCKER_DEFAULT_PLATFORM=linux/amd64  


Then, run:

    make free VERSION=10.1.1 -f graphdb/Makefile

    docker-compose up -d

> For more details look at the [graphdb-docker](https://github.com/Ontotext-AD/graphdb-docker#building-a-docker-image-based-on-the-free-edition) repository.

Create the GraphDB repository

    pip install -r scripts/requirements.txt
    python3 scripts/create_repo.py

Upload vocabularies

    python3 scripts/load_vocabularies.py

Upload ontologies (Odeuropa + CRM + CRMsci + REO)

    python3 scripts/load_dump.py ontology

Upload dumps

    python3 scripts/load_dump.py getty
    python3 scripts/load_dump.py geonames
    python3 scripts/load_dump.py image-annotation
    python3 scripts/load_dump.py text-annotation
    python3 scripts/load_dump.py british-library
    python3 scripts/load_dump.py royal-society-corpus
    python3 scripts/load_dump.py old-bailey-corpus
    python3 scripts/load_dump.py gutenberg
    python3 scripts/load_dump.py gutenberg_it
    python3 scripts/load_dump.py eebo
    python3 scripts/load_dump.py gallica
    python3 scripts/load_dump.py grimm
    python3 scripts/load_dump.py bibbleue
    python3 scripts/load_dump.py dbnl
    python3 scripts/load_dump.py dbnl_nl1
    python3 scripts/load_dump.py dbnl_nl3
    python3 scripts/load_dump.py dta
    python3 scripts/load_dump.py dta_de2
    python3 scripts/load_dump.py wikisource
    python3 scripts/load_dump.py liberliber
    python3 scripts/load_dump.py dlib
    python3 scripts/load_dump.py dlib_sl0000
    python3 scripts/load_dump.py dlib_sl0001
    python3 scripts/load_dump.py dlib_sl0002
    python3 scripts/load_dump.py dlib_sl0003
    python3 scripts/load_dump.py dlib_sl0004
    python3 scripts/load_dump.py dlib_sl0005
    python3 scripts/load_dump.py dlib_sl0006
    python3 scripts/load_dump.py dlib_sl0007
    python3 scripts/load_dump.py dlib_sl0008
    python3 scripts/load_dump.py dlib_sl0009
    python3 scripts/load_dump.py dlib_sl0010
    python3 scripts/load_dump.py dlib_sl0011
    python3 scripts/load_dump.py dlib_sl0012
    python3 scripts/load_dump.py dlib_sl0013
    python3 scripts/load_dump.py dlib_sl0014
    python3 scripts/load_dump.py dlib_sl0015
    python3 scripts/load_dump.py dlib_sl0016
    python3 scripts/load_dump.py dlib_sl0017
    python3 scripts/load_dump.py dlib_sl0018
    python3 scripts/load_dump.py dlib_sl0019
    python3 scripts/load_dump.py dlib_sl0020
    python3 scripts/load_dump.py dlib_sl0021
    python3 scripts/load_dump.py dlib_sl0022
    python3 scripts/load_dump.py dlib_sl0023
    python3 scripts/load_dump.py dlib_sl0024
    python3 scripts/load_dump.py dlib_sl0025
    python3 scripts/load_dump.py dlib_sl0026
    python3 scripts/load_dump.py dlib_sl0027
    python3 scripts/load_dump.py dlib_sl0028
    python3 scripts/load_dump.py dlib_sl0029
    python3 scripts/load_dump.py dlib_sl0030
    python3 scripts/load_dump.py dlib_sl0031
    python3 scripts/load_dump.py dlib_sl0032
    python3 scripts/load_dump.py dlib_sl0033
    python3 scripts/load_dump.py dlib_sl0034
    python3 scripts/load_dump.py dlib_sl0035
    python3 scripts/load_dump.py dlib_sl0036
    python3 scripts/load_dump.py dlib_sl0037
    python3 scripts/load_dump.py dlib_sl0038
    python3 scripts/load_dump.py dlib_sl0039
    python3 scripts/load_dump.py dlib_sl0040
    python3 scripts/load_dump.py dlib_sl0041
    python3 scripts/load_dump.py dlib_sl0042
    python3 scripts/load_dump.py dlib_sl0043
    python3 scripts/load_dump.py dlib_sl0044
    python3 scripts/load_dump.py dlib_sl0045
    python3 scripts/load_dump.py dlib_sl0046
    python3 scripts/load_dump.py dlib_sl0047
    python3 scripts/load_dump.py dlib_sl0048
    python3 scripts/load_dump.py dlib_sl0049
    python3 scripts/load_dump.py dlib_sl0050
    python3 scripts/load_dump.py dlib_sl0051
    python3 scripts/load_dump.py dlib_sl0052
    python3 scripts/load_dump.py dlib_sl0053
    python3 scripts/load_dump.py dlib_sl0054
    python3 scripts/load_dump.py dlib_sl0055
    python3 scripts/load_dump.py dlib_sl0056
    python3 scripts/load_dump.py dlib_sl0057
    python3 scripts/load_dump.py dlib_sl0058
    python3 scripts/load_dump.py dlib_sl0059

## Apache Configuration and dereferencing

In `graphdb/config.yml` it is possible to configure the basic information about the database server, as well as the list of base paths to dereference
([more details](https://github.com/pasqLisena/list2dereference) about the used tool and syntax).

Running the following script (requires NodeJS installed)

    npx list2dereference graphdb/config.yml

2 files will be produced:
- data.odeuropa.org.conf is the configuration file for Apache and saved in `/etc/apache2/sites-available/`
- script_graphdb.sh should be run inside the Docker container using `docker exec -it odeuropa_graphdb bash`

> This procedure should be repeated when new base paths for dereferencing are needed

### Skosmos

Configure `skosmos/config.ttl` (see [instructions](https://github.com/NatLibFi/Skosmos/wiki/Configuration)).

Install skosmos using docker

    docker build -t skosmos https://github.com/silknow/skosmos
    docker run -d -p 8872:80 -v /home/semantic/odeuropa/knowledge-graph/skosmos:/config --name odeuropa_skosmos skosmos


# Data conversion from raw

    cd populate
    pip install -r requirements.txt
    spacy download en_core_web_sm
    spacy download fr_core_news_sm
    spacy download nl_core_news_sm
    spacy download de_core_news_sm
    spacy download it_core_news_sm

    python convert_img.py
    python convert_text.py -i ./input/text-annotation
    python convert_text.py -i ./input/royal-society-corpus --lang en
    python convert_text.py -i ./input/british-library --lang en
    python convert_text.py -i ./input/old-bailey-corpus --lang en
    python convert_text.py -i ./input/gutenberg --lang en
    python convert_text.py -i ./input/gutenberg_it --lang it
    python convert_text.py -i ./input/eebo --lang en
    python convert_text.py -i ./input/gallica --lang fr
    python convert_text.py -i ./input/grimm --lang fr
    python convert_text.py -i ./input/bibbleue --lang fr
    python convert_text.py -i ./input/dbnl --lang nl
    python convert_text.py -i ./input/dbnl_nl1 --lang nl
    python convert_text.py -i ./input/dbnl_nl3 --lang nl
    python convert_text.py -i ./input/liberliber --lang it
    python convert_text.py -i ./input/wikisource --lang it
    python convert_text.py -i ./input/dta --lang de
    python convert_text.py -i ./input/dta_de2 --lang de
    python convert_text.py -i ./input/dlib --lang sl --batch --metadata ris


The URI pattern is described in a separate [README](URI-patterns.md).

## Funding acknowledgement

<img src="https://github.com/Odeuropa/.github/raw/main/profile/eu-logo.png" width="80" height="54" align="left" alt="EU logo" />

This work has been realised in the context of [Odeuropa](https://odeuropa.eu/), a research project that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 101004469.

