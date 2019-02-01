# OpenReq Improving requirements quality by features

This plugin was created as a result of the OpenReq project funded by the European Union Horizon 2020 Research and Innovation programme under grant agreement No 732463.

The following technologies are used:

* DBPedia Spotlight (https://www.dbpedia-spotlight.org/)
* SPARQL Language (https://www.w3.org/TR/rdf-sparql-query/)
* Spacy (https://spacy.io/)
* PyOrient (http://www.orientdb.com)
* Pyphen (https://pypi.org/project/Pyphen/)
* Morph_IT (https://github.com/giodegas/morphit-lemmatizer/tree/master/master)

## Public APIs

The API is documented by using Swagger2:
https://api.openreq.eu/#/services/prs-improving-requirements-quality-features

## What the microservice does

We aim to carry out a platform which may help to:

* make requirements features explicit, in order to make identification and requirement quality classification straightforward
* provide requirement structure

Our approach consists in:

* Identifying requirements candidate paragraphs keeping title/section dependencies.
* Using machine learning-based tools to build a dependency logical structure of each paragraphs (subject, actions, complementary objects).
* Defining very weak dependency trees among concept, allowing to extend it or include dependecies from external ontologies.
* Giving a set of metrics to classify existing requirements using feature-based classifiers

### Steps

1) Conversion in free text
2) Parsing of word document in Blocks keeping dependendeces (title/section)
3) Paragraph enrichment
4) Building of OpenReq Ontology

The workflow is based on the following steps:

1) Conversion in free text
2) Parsing of word document in Blocks, keeping dependendences (title/section)
3) Paragraph enrichment
4) Production of OpenReq Ontology

## How to install

### Using `docker-compose up`
Make sure that `docker-compose` is [installed](https://docs.docker.com/compose/install/) (not included in normal docker installation)! Then go to the root folder of task_3_3 and type `docker-compose up`. Docker will then automatically build and run the two containers (`spotlight` and `openreq_t_33`). Also after building, the containers can be run at any time by `docker-compose up`.

### Using pure docker

#### Build docker `spotlight`
Clone **spotlight-docker** repo (`git clone https://github.com/dbpedia-spotlight/spotlight-docker`); next `cd` with `bash` into `spotlight-docker/v1.0/english` and generate the `spotlight` container via `sudo docker build -f Dockerfile  -t english_spotlight .`
*Please note that the `docker-spotlight` repo has been added as a submodule to the internal DataScience gitlab.* 

#### Build docker `openreq`
Go inside the `task_3_3` folder and generate the `openreq` container via `sudo docker build . -t openreq_t_33`. If you are behind a proxy, you have to specify an env and use `sudo docker build . --network=host --build-arg "HTTPS_PROXY=$https_proxy" -t openreq_t_33`.

#### How to run docker container
First generate bridge to connect containers
sudo docker network create [name][subnet]
(**use**: `sudo docker network create db_req_bridge --subnet 172.31.38.152/20`)

specify docker run options
sudo docker run [net][name][ip][port][container][entrypoint]
(**use**: `sudo docker run --net db_req_bridge -i --name db --ip 172.31.32.3 -p 2222:80  english_spotlight spotlight.sh`)
(**use**: `sudo docker run --net db_req_bridge -it --name req --ip 172.31.32.2 -p 10602:5008 openreq_t_33`)

## How to use
The platform comes with a set of micrososervices that are internally called by a unique entrypoint (/uploader). Therefore, altohugh all microservices have been documented, only the `/uploader` endpoint is responsible of making 
the whole workflow running. In particular, "/prettify" service format the output of enpoint workflow according to OpenReq ontology. 
Therefore, the Microservice has one entrypoint at the position:
`http://217.172.12.199:10602/prs-improving-requirements-quality-features/uploader`

with the following code:

```
files = [('file', (filename, open(filename, 'rb'), 'application/octet'))]
  
response = requests.post("http://217.172.12.199:10602/prs-improving-requirements-quality-features/upolader/num_par", files=files)`
```

being filename the name of the file to be uploaded and num_par the number of paragraph. The user should pass a document and the number of sub-blocks that should be parsed (each sub block may be represented by a title, a list of paragraph and so on).
The full processing stage may require several minutes, depending on the infrastructure performance and the size of the document to be uploaded. No GUI is provided (a json-like output is provided, according to OpenReq Ontology). 
The output is compliant to OpenReq JSON structure.

## Note for developers
None

## Sources
None

#### Appendix:
 ensure to change IP:PORT in `config.json` of `app.py` if -- and only **if** -- other IP/ports are used for the bridge
e.g. from "http://localhost:42001/rest/annotate", " to "http://172.31.37.91:11111/rest/annotate"

## How to contribute
See OpenReq project contribution link: [guidelines](https://github.com/OpenReqEU/OpenReq/blob/master/CONTRIBUTING.md)

## License
Free use of this software is granted under the terms of the EPL version 2 (EPL2.0).

