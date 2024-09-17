# Property Sales Dashboard Using Real Data Crawled from Real Estate Website

This repository consists of an implementation of a dashboard containing data scraped from a real estate website: [Imovirtual](https://www.imovirtual.com/), a Portuguese real estate website offering homes, apartments, and other properties for sale and rent. Using MongoDB as the database, it crawls raw data, cleans it, and makes it ready to be used in the dashboard.

Both the dashboard and the scripts to crawl the data were implemented using Python. The dashboard uses the [Dash](https://dash.plotly.com/) and [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) frameworks. To scrape the data, it uses [Requests](https://requests.readthedocs.io/en/latest/), asynchronous requests with [HTTPX](https://www.python-httpx.org/), and [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/).

By setting the environmental variables, the script can store the scraped raw data in three different sources: MongoDB using [pymongo](https://pymongo.readthedocs.io/en/stable/#), an AWS S3 bucket as a JSON file (using [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)), and local storage as a JSON file.

It's possible to run the dashboard using Docker Compose.

## Table of Contents

- [How it works](#how-it-works)
  - [Data Ingestion](#data-ingestion)
  - [Dashboard](#dashboard)
- [How to run this project](#how-to-run-this-project)
  - [Data Ingestion](#data-ingestion)
  - [Dash with Docker](#dash-with-docker)
  - [MongoDB local backup](#mongodb-local-backup)
- [Further Improvements](#further-improvements)

## How it works

The project is divided into two blocks that can work separately, each inside the `src` folder:

- **Data Ingestion**: Responsible for crawling the data, consolidating it in the database while avoiding duplicates, and preparing the data for use in the dashboard.
- **Dashboard**: Uses the cleaned and filtered data from the database.

<img src="media/diag.png" style="width: 100%;" alt="Description of the image">


### Data Ingestion

All the code related to data ingestion is inside the `src/ingestion` folder. It creates three collections in MongoDB:

- A raw collection for storing the crawled data.
- A consolidated collection that maintains an historical record of the data.
- A dashboard collection used by the dashboard.

The raw collection, which comes from the crawler, can store data in MongoDB, an AWS S3 bucket as a JSON file, or locally as a JSON file, depending on the settings in the `.env` file.

The consolidation process creates a new collection in MongoDB and removes duplicate values from the raw data. It compares the raw data with the consolidated collection, allowing only new advertisements to be inserted and updating advertisements that are no longer available on the website. It filters unique entries using the same ID retrieved from the website for each advertisement. The goal of consolidation is to maintain a historical record of advertisements, even if they are no longer available on the website.

For the data used in the dashboard, a new collection is created. This pipeline extracts data from one of the previous collections (raw or consolidated), filters and transforms it so that it is ready for use in the dashboard.

For this specific website, it was possible to use asynchronous requests. In the first request, pagination information is retrieved for our search. This allows us to make an initial request to obtain this information, construct a block of URLs for requests, and perform asynchronous requests. After the requests, the data is extracted.

### Dashboard

All the data used in the dashboard is loaded directly from the MongoDB collection designed for it. The folder and file structures inside `src/dash` were designed to load the data from MongoDB only once, and the components import the data from the same source file.

To build the graphs and manipulate the data, it uses [Plotly](https://plotly.com/python/) and [Pandas](https://pandas.pydata.org/docs/index.html).


## How to run this project

All the steps here were intended to a `bash` terminal.

This section shows how to run the project.  

Regardless of the method, start with the following steps:

1 - Clone the repo locally:
```bash
git clone https://github.com/lealre/madr-fastapi.git
```

2 - Access the project directory:
```bash
cd madr-fastapi
```

### Data Ingestion

### Dash with Docker

### MongoDB local Backup

The script [mongo_backup.sh](mongo_backup.sh) dumps the database to local storage in a file format. It uses the paths and container name specified in `.env` file.

The script first dumps the database content to a file inside the container, and it then copies the dump file from the container to the local storage.

Make the script executable:
```bash
chmod +x mongo_backup.sh
```

Execute the backup script:
```bash
./mongo_backup.sh
```

The `.env` file should contain the following variables:
```
CONTAINER_NAME="container-name"
BACKUP_PATH="/path/in/container"
LOCAL_BACKUP_PATH="/local/path/to/export"
```

## Further Improvements