import psycopg2
import csv
import json
from datetime import datetime
from connect_to_db import connect_and_load


def parse_date(value):
    if not value or value.strip() == "":
        return datetime.now().isoformat()
    v = value.strip()
    try:
        dt = datetime.strptime(v, "%Y-%m-%d")
        return dt.isoformat()
    except Exception:
        pass
    try:
        dt = datetime.strptime(v, "%Y.%m")
        return dt.replace(day=1).isoformat()
    except Exception:
        return datetime.now().isoformat()


def convert_to_geography(value):
    try:
        lat_str, lon_str = value.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        return f"SRID=4326;POINT({lon} {lat})"
    except Exception:
        return None


def parse_working_hours(working_hours):
    return json.dumps({"raw": working_hours.strip()})


def str_to_bool(value):
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def parse_pg_array(value):
    if not value or value.strip() == "":
        return []
    s = value.strip()
    if s.startswith("{") and s.endswith("}"):
        s = s[1:-1]
    if not s:
        return []
    items = [item.strip().strip('"') for item in s.split(",")]
    return items


def to_pg_array(arr):
    if not arr:
        return "{}"
    escaped = [item.replace('"', '\\"') for item in arr]
    return "{" + ",".join(f'"{item}"' for item in escaped) + "}"


def load_csv_to_db(conn, csv_path):
    with conn.cursor() as cursor, open(csv_path, newline="", encoding="latin-1") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            try:
                venue_id = int(row["venue_id"])
                type_ = row["type"].strip()
                name = row["name"].strip()

                logos = parse_pg_array(row.get("logo", ""))
                logo_pg = to_pg_array(logos)  
                location_geo = convert_to_geography(row["location"])
                if location_geo is None:
                    print(f"Skipping venue_id={venue_id} due to invalid location")
                    continue

                plus_code = row.get("plus_code", "").strip() or None
                working_hours_json = parse_working_hours(row.get("working_hours", ""))

                accessibility_pets = str_to_bool(row.get("accessibility_pets", "false"))
                accessibility_disabled = str_to_bool(row.get("accessibility_disabled", "false"))
                seating_inside = int(row.get("seating_inside", "0"))
                seating_outside = int(row.get("seating_outside", "0"))
                reservation_available = str_to_bool(row.get("reservation_available", "false"))
                reservation_price_base = float(row.get("reservation_price_base", "0") or "0")
                reservation_price_per_person = float(row.get("reservation_price_per_person", "0") or "0")
                reservation_phone = row.get("reservation_phone", "").strip()

                images = parse_pg_array(row.get("images", ""))
                features = parse_pg_array(row.get("features", ""))
                music_type = parse_pg_array(row.get("music_type", ""))
                atmosphere = parse_pg_array(row.get("atmosphere", ""))

                images_pg = to_pg_array(images)
                features_pg = to_pg_array(features)
                music_type_pg = to_pg_array(music_type)
                atmosphere_pg = to_pg_array(atmosphere)

                metadata_raw = row.get("metadata", "").strip()
                metadata = json.dumps({}) if metadata_raw in ("", "{}") else metadata_raw

                created_at = parse_date(row.get("created_at"))
                updated_at = parse_date(row.get("updated_at"))

                cursor.execute(
                    """
                    INSERT INTO venues (
                        venue_id, type, name, logo, location, plus_code, address, phone_number, email, website_url,
                        working_hours, accessibility_pets, accessibility_disabled, seating_inside, seating_outside,
                        reservation_available, reservation_price_base, reservation_price_per_person, reservation_phone,
                        images, features, music_type, atmosphere, metadata, created_at, updated_at
                    ) VALUES (
                        %(venue_id)s, %(type)s, %(name)s, %(logo)s::text[], ST_GeogFromText(%(location)s), %(plus_code)s, %(address)s, %(phone_number)s,
                        %(email)s, %(website_url)s, %(working_hours)s::jsonb, %(accessibility_pets)s, %(accessibility_disabled)s,
                        %(seating_inside)s, %(seating_outside)s, %(reservation_available)s, %(reservation_price_base)s,
                        %(reservation_price_per_person)s, %(reservation_phone)s, %(images)s::text[], %(features)s::text[], %(music_type)s::text[],
                        %(atmosphere)s::text[], %(metadata)s, %(created_at)s::timestamptz, %(updated_at)s::timestamptz
                    )
                    ON CONFLICT (venue_id) DO NOTHING;
                    """,
                    {
                        "venue_id": venue_id,
                        "type": type_,
                        "name": name,
                        "logo": logo_pg,
                        "location": location_geo,
                        "plus_code": plus_code,
                        "address": row.get("address", "").strip(),
                        "phone_number": row.get("phone_number", "").strip(),
                        "email": row.get("email", "").strip(),
                        "website_url": row.get("website_url", "").strip(),
                        "working_hours": working_hours_json,
                        "accessibility_pets": accessibility_pets,
                        "accessibility_disabled": accessibility_disabled,
                        "seating_inside": seating_inside,
                        "seating_outside": seating_outside,
                        "reservation_available": reservation_available,
                        "reservation_price_base": reservation_price_base,
                        "reservation_price_per_person": reservation_price_per_person,
                        "reservation_phone": reservation_phone,
                        "images": images_pg,
                        "features": features_pg,
                        "music_type": music_type_pg,
                        "atmosphere": atmosphere_pg,
                        "metadata": metadata,
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )
                conn.commit()
                print(f"Inserted venue_id={venue_id}")
            except Exception as e:
                conn.rollback()
                print(f"Error processing row {idx} venue_id={row.get('venue_id')}: {e}")


def load_catalog_csv(conn, csv_path):
    with conn.cursor() as cursor, open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            try:
                item_id = int(row["item_id"])
                space_id = int(row["space_id"])
                name = row["name"].strip()
                description = row.get("description") or None
                size = row.get("size") or None
                images = parse_pg_array(row.get("images", ""))
                price = float(row["price"])
                item_type = row.get("item_type") or None
                category = row.get("category") or None
                created_at = parse_date(row.get("created_at"))

                images_pg = to_pg_array(images)

                cursor.execute(
                    """
                    INSERT INTO catalog (
                        item_id, space_id, name, description, size, images, price, item_type, category, created_at
                    ) VALUES (
                        %(item_id)s, %(space_id)s, %(name)s, %(description)s, %(size)s, %(images)s::text[], %(price)s,
                        %(item_type)s, %(category)s, %(created_at)s::timestamptz
                    )
                    ON CONFLICT (item_id) DO NOTHING;
                    """,
                    {
                        "item_id": item_id,
                        "space_id": space_id,
                        "name": name,
                        "description": description,
                        "size": size,
                        "images": images_pg,
                        "price": price,
                        "item_type": item_type,
                        "category": category,
                        "created_at": created_at,
                    }
                )
                conn.commit()
                print(f"Inserted catalog item_id={item_id}")
            except Exception as e:
                conn.rollback()
                print(f"Error processing catalog row {idx} item_id={row.get('item_id')}: {e}")


def load_catalog_csv(conn, csv_path):
    with conn.cursor() as cursor, open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            try:
                item_id = int(row["item_id"])
                space_id = int(row["space_id"])
                name = row["name"].strip()
                description = row.get("description") or None
                size = row.get("size") or None
                images = parse_pg_array(row.get("images", ""))
                price = float(row["price"])
                item_type = row.get("item_type") or None
                category = row.get("category") or None
                created_at = parse_date(row.get("created_at"))

                images_pg = to_pg_array(images)

                cursor.execute(
                    """
                    INSERT INTO catalog (
                        item_id, space_id, name, description, size, images, price, item_type, category, created_at
                    ) VALUES (
                        %(item_id)s, %(space_id)s, %(name)s, %(description)s, %(size)s, %(images)s::text[], %(price)s,
                        %(item_type)s, %(category)s, %(created_at)s::timestamptz
                    )
                    ON CONFLICT (item_id) DO NOTHING;
                    """,
                    {
                        "item_id": item_id,
                        "space_id": space_id,
                        "name": name,
                        "description": description,
                        "size": size,
                        "images": images_pg,
                        "price": price,
                        "item_type": item_type,
                        "category": category,
                        "created_at": created_at,
                    }
                )
                conn.commit()
                print(f"Inserted catalog item_id={item_id}")
            except Exception as e:
                conn.rollback()
                print(f"Error processing catalog row {idx} item_id={row.get('item_id')}: {e}")


def load_reviews_csv(conn, csv_path):
    with conn.cursor() as cursor, open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            try:
                review_id = int(row["review_id"])
                space_id = int(row["space_id"])
                username = row["username"].strip()
                rating = int(row["rating"])
                review_text = row.get("review_text") or None
                created_at = parse_date(row.get("created_at"))

                cursor.execute(
                    """
                    INSERT INTO reviews (
                        review_id, space_id, username, rating, review_text, created_at
                    ) VALUES (
                        %(review_id)s, %(space_id)s, %(username)s, %(rating)s, %(review_text)s, %(created_at)s::timestamptz
                    )
                    ON CONFLICT (review_id) DO NOTHING;
                    """,
                    {
                        "review_id": review_id,
                        "space_id": space_id,
                        "username": username,
                        "rating": rating,
                        "review_text": review_text,
                        "created_at": created_at,
                    }
                )
                conn.commit()
                print(f"Inserted review_id={review_id}")
            except Exception as e:
                conn.rollback()
                print(f"Error processing review row {idx} review_id={row.get('review_id')}: {e}")


def main():
    conn = connect_and_load()
    if conn:
        load_csv_to_db(conn, r"data/venues.csv")
        load_catalog_csv(conn, r"data/catalog.csv")
        load_reviews_csv(conn, r"data/reviews.csv")
        conn.close()
        print("Data loaded successfully and connection closed.")
    else:
        print("Failed to load data.")

if __name__ == "__main__":
    main()

