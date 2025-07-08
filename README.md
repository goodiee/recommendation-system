# RAG with MPNet Embeddings for Venue Search and Reviews

This repository implements a **Retrieval-Augmented Generation (RAG)** model for querying a PostgreSQL database containing venue information and reviews. The RAG helps find the most relevant venue based on a user’s query, utilizing **MPNet embeddings** for semantic search and ranking.

## Project Overview

This project consists of three main components:

1. **MPNet Embeddings**: Used for semantic search and ranking of venues and reviews.
2. **PostgreSQL Database**: Stores data related to venues, reviews, and working areas, along with their embeddings.
3. **RAG Model**: Performs the search and ranking of venues based on user queries, using the embeddings stored in the database.

### Key Files

- `load_csv_todb.py`: A script that loads data into the PostgreSQL database from CSV files containing venue and review information.
- `search.py`: A script that performs semantic search queries using the RAG model.
- `main.sql`: SQL file that defines the structure of the database tables.
- `requirements.txt`: The list of dependencies for the project.
  
## Database Structure

The PostgreSQL database contains three main tables:

1. **venues**: Stores information about various venues (e.g., name, location, description).
2. **reviews**: Contains user reviews for venues (e.g., review text, rating).
3. **catalog**: Describes different working areas for venues (e.g., area name, description).

The **MPNet embeddings** for venues and reviews are stored in the database and are used for semantic similarity search.

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### 2. Install Dependencies
Install the required Python packages:

```
pip install -r requirements.txt
```
### 3. Set Up PostgreSQL Database
Make sure you have PostgreSQL installed and running. Create a new database and load the schema from main.sql:


-- Connect to your PostgreSQL server
```
psql -h localhost -U postgres
```
-- Create a new database
```
CREATE DATABASE your_database;
```
-- Execute the SQL schema
```
\i main.sql
```
###4. Load Data into the Database
Use the load_csv_todb.py script to load data from CSV files into the database:

```
python load_csv_todb.py
```
This will load the data from your CSV files (venues, reviews, catalog) into the PostgreSQL database.

5. Running the RAG Search
Once the data is loaded, you can run the search.py script to perform a semantic search for venues based on your query. The RAG model will return the most relevant venues based on MPNet embeddings.

To run the search, simply execute the following:

```
python search.py
```
You will be prompted to enter a query. The RAG model will search the database and return the relevant venue(s) based on semantic similarity.

File Descriptions
load_csv_todb.py: Loads venue, review, and working area data into the PostgreSQL database.

search.py: Runs the RAG-based search and returns the most relevant venues based on a query.

main.sql: Defines the schema and structure for the PostgreSQL database.

requirements.txt: Lists the required Python packages for the project.

Example Usage

What is the best venue for a quiet evening out?
The system will return relevant venues based on the query, using semantic search over MPNet embeddings.
You can modify the dataset (usually found in data/ folder or within specific CSV files) to experiment with different input data for generating recommendations.
