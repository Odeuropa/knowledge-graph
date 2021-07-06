# European Olfactory Knowledge Graph

Series of scripts, procedures and dumps for deploying the EOKG on GraphDB and Docker.

#### Requirements

- Docker
- NodeJS
- Python

## GraphDB

Download latest version of GraphDB free by registering on the [product website](https://www.ontotext.com/products/graphdb/graphdb-free/). Place the obtained zip in the `graphdb` folder.
We will use version 9.8.0.

Then, run:

    make free VERSION=9.8.0 -f graphdb/Makefile

    docker-compose up -d

> For more details look at the [graphdb-docker](https://github.com/Ontotext-AD/graphdb-docker#building-a-docker-image-based-on-the-free-edition) repository.

Create the GraphDB repository

    python3 scripts/create_repo.py

Upload vocabularies

    python3 scripts/load_vocabularies.py

## Apache Configuration and dereferencing

In `graphdb/config.yml` it is possible to configure the basic information about the database server, as well as the list of base paths to dereference
([more details](https://github.com/pasqLisena/list2dereference) about the used tool and syntax).

Running the following script (requires NodeJS installed)

    npx list2dereference graphdb/config.yml

2 files will be produced:
- data.odeuropa.org.conf is the configuration file for Apache and saved in `/etc/apache2/sites-available/`
- script_graphdb.sh should be run inside the Docker container using `docker exec -it odeuropa_graphdb bash`

> This procedure should be repeated when new base paths for dereferencing are needed
