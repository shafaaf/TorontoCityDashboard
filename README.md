# CVST History Timeline Report Engine

An Intelligent Transportation System web application that performs data analytics and aggregations for transportation and weather data in Toronto. Aim is to help TTC officials and route planners in extracting trends from the past to help in their decision-making to improve the safety and efficiency of public transportation.

Done as part of University of Toronto Computer Engineering Undergraduate Capstone (ECE496) project.
The live web application is available at: http://142.104.17.134:8080/

## Main Technologies Used

* Tornado Python framework
* Elasticsearch
* Spark
* Google Maps APIs

## Background

Connected Vehicles Smart Transportation, or plainly [CVST](http://cvst.ca/) provides a platform for novel applications
and innovations to improve the efficiency and safety of transportation systems. The system
mines and stores a large variety of information related to traffic. However, given the sheer size of
the data available, the [current CVST platform](http://portal.cvst.ca/) makes it challenging for users to rapidly draw
conclusions from the data. This project’s primary objective is to improve the CVST platform by
providing a reporting web application to create visualizations of CVST in the form of charts and
graphs.

More info available under the documents folder.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install first to run the project:
* Git
* Java
* Python 2.7
* Pip
* Elasticsearch
* Spark

### Installation And Basic Setup

A step by step procedure to have a local development env running:

Clone Gitlab project
```
git clone -b shafaafCVST https://shafaaf@gitlab.com/cvst-bi/timeline.git
```

Install Python dependencies
```
pip install -r requirements.txt
```


Run Tornado server
```
./runServer.sh
```

Go to the following url using a browser
```
http://localhost:8080/
```

Note: The following above will have all data snapshots/heatmaps working. For aggregations for a span of time, for weather, CVST data needs to be collected, and stored on Elasticsearch. See below.


## Running The Weather Data Aggregations

To run aggreagtions for a span of time, for example weather, do the following:

Run Elasticsearch instance on local computer/deployment server
```
./elasticsearch
```

Run the python script to setup databased index and shards
```bash
cd elasticDbClient/weather/core
python storeWeatherData.py
```

Run the python script to keep updating data till present time
```bash
cd elasticDbClient/weather/core
python updateWeatherData.py
```
Note: Can kill of script after getting some data. If run again, will continue collecting from where left off.

Note: For above script, can use nohup and & to keep running in the background as takes a while to collect all the data till the present time.
```
sudo nohup python updateWeatherData.py&
```

## Deployment

The web application was deployed on the server with public IP address: 142.104.17.134
To deploy, do the same procedure as the **Getting Started** section above and to run aggregations, follow the **Running The Weather Data Aggregations** section.

Note: Also to keep the weather data always upto date, wrap the Python update scripts using the Python schedule library to run, for example once everyday to always automatically update the data.

## Authors

* **Shafaaf Khaled Hossain** - *shafaaf.hossain@mail.utoronto.ca*
* **Joohyun Lee** -  *joohyun.lee@mail.utoronto.ca*
* **Terry Shi** -  *terry.shi@mail.utoronto.ca*
* **Eric Deng** - *eric.deng@mail.utoronto.ca*


## Acknowledgments

* Alberto Leon-Garcia - Principal Investigator of CVST
* Ali Tizghadam - Project Supervisor
* Hamzeh Khazaei - Technical Advisor
* Nick Burgwin - Project Administrator
* Morteza Moghaddassian
* Bahareh Najafi
* Daiqing Li

## Additional Information

More information can be found under the documents folder in the repo. It includes initial and final project proposals, reports, testing results and final evaluation.
