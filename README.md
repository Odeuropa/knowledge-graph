# European Olfactory Knowledge Graph

Series of scripts, procedures and dumps for deploying the EOKG on GraphDB and Docker.

## GraphDB

Download latest version of GraphDB free by registering on the [product website](https://www.ontotext.com/products/graphdb/graphdb-free/). Place the obtained zip in the `graphdb` folder.
We will use version 9.8.0.

Then, run:

    make free VERSION=9.8.0 -f graphdb/Makefile

    docker-compose

> For more details look at the [graphdb-docker](https://github.com/Ontotext-AD/graphdb-docker#building-a-docker-image-based-on-the-free-edition) repository.

Create the GraphDB repository

    python scripts/create_repo.py

Upload vocabularies

    python scripts/load_vocabularies.py