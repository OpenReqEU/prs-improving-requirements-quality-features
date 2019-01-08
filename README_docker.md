# How to use docker containers

# using `docker-compose up`
Make sure that `docker-compose` is [installed](https://docs.docker.com/compose/install/) (not included in normal docker installation)! Then go to the root folder of task_3_3 and type `docker-compose up`. Docker will then automatically build and run the two containers (`spotlight` and `openreq_t_33`). Also after building, the containers can be run at any time by `docker-compose up`.

##

# alternative: ***NOT*** using `docker-compose up`
## Build docker `spotlight`
Clone **spotlight-docker** repo (`git clone https://github.com/dbpedia-spotlight/spotlight-docker`); next `cd` with `bash` into `spotlight-docker/v1.0/english` and generate the `spotlight` container via `sudo docker build -f Dockerfile  -t english_spotlight .`
*Please note that the `docker-spotlight` repo has been added as a submodule to the internal DataScience gitlab.* 
###
## Build docker `openreq`
Go inside the `task_3_3` folder and generate the `openreq` container via `sudo docker build . -t openreq_t_33`. If you are behind a proxy, you have to specify an env and use `sudo docker build . --network=host --build-arg "HTTPS_PROXY=$https_proxy" -t openreq_t_33`.
###
## How to run docker container

### first generate bridge to connect containers
sudo docker network create [name][subnet]
(**use**: "sudo docker network create db_req_bridge --subnet 172.31.38.152/20")
###
### ensure that IPs are in env `noProxy` of the docker `config.json`
e.g.:
{
 "proxies":
 {
   "default":
   {
     "httpProxy": "http://192.168.10.1:3128", #eng proxy
     "httpsProxy": "https://192.168.10.1:3128", #eng proxy
     "noProxy": "localhost,127.0.0.1,193.109.207.65,172.31.32.2,172.31.32.3"
   }
 }
}

### specify docker run options
sudo docker run [net][name][ip][port][container][entrypoint]
(**use**: `sudo docker run --net db_req_bridge -i --name db --ip 172.31.32.3 -p 2222:80  english_spotlight spotlight.sh`)
(**use**: `sudo docker run --net db_req_bridge -it --name req --ip 172.31.32.2 -p 10602:5007 openreq_t_33`)

###
## Appendix:
 ensure to change IP:PORT in `config.json` of `app.py` if -- and only **if** -- other IP/ports are used for the bridge
e.g. from "http://localhost:42001/rest/annotate", " to "http://172.31.37.91:11111/rest/annotate"