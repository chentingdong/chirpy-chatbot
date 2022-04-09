# Illusionist System Design

## System Design

* Infrusture:

<img src="./illusionist-system.jpg" width="1024"/>

* API and data flow:

<img src="./illusionist-dataflow.jpg" width="1024"/>

* Data modals in relational DB.
  
<img src="./illusionist-datamodel.jpg" width="1024"/>

## Bot Designer
Design a single bot conversation using FSM and behavior driven NLP engine.
This is the simplest demo bot that search the knowledge base of our client to find a specific form, based on semantic search.

<img src="./illusionist-bot.jpg" width="1024"/>

## Bot Manager. 
Support multiple tenant, multiple user, with different UI designs. 

<img src="./illusionist-bot-manager.jpg" width="1024"/>

## Realtime bot: 
One example of action bot, injecting external APIs to accomplish certain actions during the conversation. 
This bot help an employee to choose a company provided list of cell phones, managed by the company in ServiceNow.
One action node make an API call to ServiceNow and guide the user to finish the ordering process.

<img src="./illusionist-realtime-yelp.jpg" width="1024"/>


## Bot Simulator 
Used for realtime conversation debugging. Target user bot creater.

<img src="./illusionist-bot-simulator.jpg" width="1024"/>


## NLP analysis:
This tool compares one sentences to a bot pool, visulize whether the bog engine is picking the correct answer. Green is good, red is wrong.

<img src="./illusionist-nlp-perf-report.jpg" width="1024"/>
