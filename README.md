# RAG with MPNet Embeddings for Venue Search and Reviews

This repository implements a **Retrieval-Augmented Generation (RAG)** model for querying a PostgreSQL database containing venue information and reviews. The RAG helps find the most relevant venue based on a user’s query, utilizing **MPNet embeddings** for semantic search and ranking. It serves to demonstrate the technologies and methodologies used in building recommendation systems.

## Project Overview

The project is built around three core components:

- **MPNet Embeddings**  
  MPNet embeddings are used for transforming textual data (venue names, reviews, and queries) into dense vectors. These vectors enable semantic search, allowing the system to find venues based on meaning rather than just keyword matches.

- **PostgreSQL Database (with pgvector)**  
  The PostgreSQL database stores:
  - Venue information (name, location, etc.)
  - Reviews associated with each venue
  - MPNet embeddings for venues and reviews

  The pgvector extension enables efficient vector similarity search directly inside the database.

- **RAG Model Logic**  
  The RAG logic processes user queries as follows:
  1. Encodes the user’s query using MPNet embeddings
  2. Searches the vector store (PostgreSQL) for the most similar venues
  3. Ranks and returns the top results

---

### Key Files

- `load_data_to_db`: A script that loads data into the PostgreSQL database from CSV files containing venue and review information.
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

### 3. Create Environment Variables

`cp .env.example .env
`

### 4. Build and Run with Docker

`docker-compose up --build
`
This will:
- Build the Docker image
- Start PostgreSQL with pgvector
- Expose the database for your Python scripts

### 5. Set Up PostgreSQL Database
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
### 6. Load Data into the Database
Use the load_csv_todb.py script to load data from CSV files into the database:

```
python load_data_to_db.py
```
This will load the data from your CSV files (venues, reviews, catalog) into the PostgreSQL database.

### 7. Running the RAG Search

Once the data is loaded, you can run the search.py script to perform a semantic search for venues based on your query. The RAG model will return the most relevant venues based on MPNet embeddings.

To run the search, simply execute the following:

```
python .\rag\search.py
```
You will be prompted to enter a query. The RAG model will search the database and return the relevant venue(s) based on semantic similarity.

File Descriptions

load_data_to_db.py: Loads venue, review, and working area data into the PostgreSQL database.

search.py: Runs the RAG-based search and returns the most relevant venues based on a query.

main.sql: Defines the schema and structure for the PostgreSQL database.

requirements.txt: Lists the required Python packages for the project.

### 8. Example Usage

Once everything is set up, you can run the search pipeline. For example, running the RAG logic might look like this:

`Enter your search query: coworking with free coffee
`

`Initializing PGVector vector store...
`

`Top 5 venues found:`


- ID: 6, Name: Coffee Point, Location: 0101000020E61000000F0BB5A6794739401CEBE2361A584B40

- ID: 1, Name: Free Space, Location: 0101000020E61000009D8026C2864739408E75711B0D584B40

- ID: 10, Name: Desk & Coffee, Location: 0101000020E6100000105839B4C84639409EEFA7C64B574B40

- ID: 13, Name: Creative Hub, Location: 0101000020E6100000D95F764F1E46394064CC5D4BC8574B40

- ID: 3, Name: Forge Station, Location: 0101000020E6100000CF488446B0453940FDC0559E40584B40

This indicates that the system has:

- Encoded your search query
- Performed a similarity search in PostgreSQL
- Returned the top-matching venues along with their locations (in WKB geometry format)

### 8. Technologies Used
- Python
- Sentence-Transformers (MPNet embeddings)
- PostgreSQL
- pgvector
- Docker / Docker Compose

