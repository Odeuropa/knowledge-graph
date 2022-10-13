# European Olfactory Knowledge Graph

Series of scripts, procedures and dumps for deploying the EOKG on GraphDB and Docker.

#### Requirements

- Docker
- NodeJS
- Python

## GraphDB

Download latest version of GraphDB free by registering on the [product website](https://www.ontotext.com/products/graphdb/graphdb-free/). Place the obtained zip in the `graphdb` folder.
We will use version 9.8.0.

If you have the new Mac M1, run:

    export DOCKER_DEFAULT_PLATFORM=linux/amd64  


Then, run:

    make free VERSION=9.8.0 -f graphdb/Makefile

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
    python3 scripts/load_dump.py text-annotation
    python3 scripts/load_dump.py royal-society-corpus
    python3 scripts/load_dump.py old-bailey-corpus
    python3 scripts/load_dump.py eebo
    python3 scripts/load_dump.py gutenberg
    python3 scripts/load_dump.py image-annotation

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

    python convert_text.py -i ./input/text-annotation
    python convert_text.py -i ./input/royal-society-corpus --lang en
    python convert_text.py -i ./input/old-bailey-corpus --lang en
    python convert_text.py -i ./input/gutenberg --lang en
    python convert_text.py -i ./input/eebo --lang en
    python convert_img.py


The URI pattern is described in a separate [README](URI-patterns.md)
