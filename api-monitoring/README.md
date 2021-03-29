# Illusionist Smoketest

#Installation

git clone  https://github.com/nevaai/illusionist.git

cd api-monitoring

pip install -r requirements.txt

#Usage:

pytest -q -s smoke_illusionist.py --env environment --conversation 'Conversation ID in Bot testing framework' --workflow 'workflow Name'

Ex: pytest -q -s smoke_illusionist.py --env https://api-dev.aineva.com/illusionist/ --conversation 2 --workflow main_flow

Availble Conversations: conversations saved in Bot Testing Framework(2,3,5,all, etc...)

Bot Testing Framework: http://bot-testing-framework.aineva.com/#/

Available workflows: 'main_flow','adidas','albertsons_updated'

Available Environments :


Staging Host:    https://api-stg.aineva.com/illusionist


Production Host:    https://api-prod.aineva.com/illusionist


adidas-demo Host:   https://illusionist-demo-adidas.aineva.com/illusionist


adidas-dev Host:    https://illusionist-dev-adidas.aineva.com/illusionist


albertsons-dev Host:   http://illusionist-dev-albertsons.aineva.com/illusionist


albertsons-demo Host:   http://albertsons.demo.aineva.com/illusionist


albertsons-demo Host:    http://albertsons.demo.aineva.com/illusionist
