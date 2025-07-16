import os
import psycopg2
from pgvector.psycopg2 import register_vector
from langchain_postgres.vectorstores import PGVector
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("DB_URL environment variable missing")

def get_embeddings(model_choice="mpnet"):
    if model_choice == "mpnet":
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    else:
        raise ValueError("Only 'mpnet' is supported in this version.")

def create_tables():
    connection = psycopg2.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    register_vector(cursor)

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS venues (
            venue_id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            features TEXT[],
            music_type TEXT,
            atmosphere TEXT
            -- note: don't include embedding_mpnet here,
            -- because we want to add it separately if missing
        );
    """)

    cursor.execute("""
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'venues'
          AND column_name = 'embedding_mpnet';
    """)
    exists = cursor.fetchone()

    if not exists:
        print("embedding_mpnet column not found, creating it...")
        cursor.execute("""
            ALTER TABLE venues
            ADD COLUMN embedding_mpnet vector(768);
        """)
        print("embedding_mpnet column created.")
    else:
        print("embedding_mpnet column already exists.")

    connection.commit()
    cursor.close()
    connection.close()

    connection = psycopg2.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    register_vector(cursor)

    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS venues (
            venue_id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            features TEXT[],
            music_type TEXT,
            atmosphere TEXT,
            embedding_mpnet VECTOR(768)
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()

def store_embeddings(embedding_model):
    print("Connecting to database to store embeddings...")

    connection = psycopg2.connect(DB_URL)
    cursor = connection.cursor()

    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    register_vector(cursor)
    print("Vector registered successfully.")

    cursor.execute("""
        SELECT venue_id, name, location, features, music_type, atmosphere
        FROM venues
    """)
    venues = cursor.fetchall()
    print(f"Fetched {len(venues)} venues from the database.")

    vector_store = get_vectorstore(embedding_model)

    documents = []
    ids = []
    texts = []
    venue_ids = []

    for venue in venues:
        venue_id, name, location, features, music_type, atmosphere = venue
        text_representation = f"{' '.join(features)} {music_type} {atmosphere}"
        texts.append(text_representation)
        venue_ids.append(venue_id)

        doc = Document(
            page_content=text_representation,
            metadata={
                "name": name,
                "location": location,
                "features": features,
                "music_type": music_type,
                "atmosphere": atmosphere,
                "venue_id": venue_id,
            },
        )

        documents.append(doc)
        ids.append(venue_id)

    print(f"Generating embeddings for {len(texts)} venues...")

    embeddings = embedding_model.embed_documents(texts)
    column_name = "embedding_mpnet"

    print(f"Embeddings generated. Example embedding snippet: {embeddings[0][:5]}")

    for venue_id, embedding in zip(venue_ids, embeddings):
        cursor.execute(
            f"""
            UPDATE venues
            SET {column_name} = %s
            WHERE venue_id = %s
            """,
            (embedding, venue_id),
        )

    connection.commit()
    print(f"Embeddings stored for {len(venues)} venues in {column_name}.")
    cursor.close()
    connection.close()

    print("Adding documents to vector store...")
    vector_store.add_documents(documents, ids=ids)
    print("Documents added to vector store.")

def get_vectorstore(embedding_model):
    print("Initializing PGVector vector store...")

    vector_store = PGVector(
        embeddings=embedding_model,
        collection_name="venues",
        connection=DB_URL,
        use_jsonb=True,
    )
    return vector_store
