==============================================
Astound Conversation Workflow Execution Engine
==============================================


**Local development**

#. Install

   - Docker machine on mac
   - AWS CLI
   - NODE/NPM

#. python_utils is a utility submodule for this Repo, to initialize:

   - Inside PyCharm, right click ``python_utils`` and ``Mark Directory as`` -> ``Sources root`` then execute the following ::

        git submodule init
        git submodule update

#. A login script to access Astound docker image repository, ~/bin/ecr-login.sh::

    #!/bin/bash
    cmd=$(aws ecr get-login | sed 's/-e none //')
    eval $cmd

#. A config file to specify aws reagion, ``~/.aws/config`` ::

    [default]
    region = us-east-1

#. A credential file to store aws ecr login keys, ``~/.aws/credentials`` ::

    [ecr]
    aws_access_key_id=ASK_ADMIN_FOR_THIS
    aws_secret_access_key=ASK_ADMIN_FOR_THIS

   Note: An alternative to above two steps is to use ``aws configure``

#. pycharm config

    Add a remote interpreter using docker-compose.local.yml

        | Settings -> Project:Illusionist -> Interpreter -> Add -> Docker Compose
        | Select Server as Docker and docker-compose.local.yml as configuration file

    Add a configuration using the docker compose interpreter

        | Select the debugger dropdown and chose to edit configurations
        | *Script path*: /usr/local/bin/flask
        | *Parameters*: run -h 0.0.0.0 -p 3000 --no-reload
        | *Environment variables*: PYTHONUNBUFFERED=1;CONFIG_ENV=local

#. Install UI dependencies ::

    cd ui && npm install

#. start docker compose in pycharm, then access a workflow, e.g. 'adidas_luke' ::

    http://localhost:2000/simulator/adidas_luke

**Swagger**

Swagger expose for api access endpoint at ``http://<host>:3000/spec``

Swagger ui is served seperately. To run it in local, download the swagger ui docker and run on port 3500 ::

    docker pull swaggerapi/swagger-ui
    docker run -p 3500:8080 -e API_URL=http://localhost:3000/spec swaggerapi/swagger-ui

**Documentation**

Automated documentation build with Sphinx. In ./docs dir, build html page. ::

    cd doc
    make html

Document can be found in http://<host>/illusionist/docs
for example: http://localhost:3000/illusionist/docs
