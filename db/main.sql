CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;

DROP SCHEMA IF EXISTS venues CASCADE;
CREATE SCHEMA venues;

SET search_path TO public, venues;

DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS catalog CASCADE;
DROP TABLE IF EXISTS venues CASCADE;

CREATE TABLE venues (
    venue_id SERIAL PRIMARY KEY,
    type VARCHAR(255) CHECK (type IN ('restaurant', 'bar', 'coworking', 'studio')) NOT NULL,
    name VARCHAR(255) NOT NULL,
    logo VARCHAR(255)[],         
    location GEOGRAPHY(POINT,4326) NOT NULL,
    plus_code TEXT,
    address VARCHAR(255),
    phone_number VARCHAR(255),  
    email VARCHAR(150),
    website_url VARCHAR(255),
    working_hours VARCHAR(255),  
    accessibility_pets BOOLEAN DEFAULT FALSE,
    accessibility_disabled BOOLEAN DEFAULT FALSE,
    seating_inside SMALLINT CHECK (seating_inside >= 0),
    seating_outside SMALLINT CHECK (seating_outside >= 0),
    reservation_available BOOLEAN DEFAULT FALSE,
    reservation_price_base DECIMAL(10,2) DEFAULT 0.0,
    reservation_price_per_person DECIMAL(10,2) DEFAULT 0.0,
    reservation_phone VARCHAR(255), 
    images VARCHAR(255)[],     
    features VARCHAR(255)[],     
    music_type VARCHAR(255)[],
    atmosphere VARCHAR(255)[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE catalog (
    item_id SERIAL PRIMARY KEY,
    space_id INTEGER NOT NULL REFERENCES venues(venue_id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    size VARCHAR(64),
    images VARCHAR(255)[], 
    price DECIMAL(10,2) NOT NULL,
    item_type VARCHAR(50),  
    category VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
    review_id SERIAL PRIMARY KEY,
    space_id INTEGER NOT NULL REFERENCES venues(venue_id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5) NOT NULL,
    review_text TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
