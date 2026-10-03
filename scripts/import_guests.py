"""
Import event guests into Neo4j.

CSV columns expected (header names can vary):
  name (required), email, phone_number,
  "What company do you work for?" or company/role,
  "What is your LinkedIn profile?" or website/linkedin

USC Startup Mixer sheet:
  name, first_name, last_name, email, addition info, school, role

Usage:
  python3 scripts/import_guests.py path/to/guests.csv
"""

import csv
import re
import sys
import time
from neo4j import GraphDatabase

LINKEDIN_RE = re.compile(
    r"(https?://(?:www\.)?linkedin\.com/[^\s\"']+|(?:www\.)?linkedin\.com/in/[^\s\"']+)",
    re.IGNORECASE,
)

NEO4J_URI      = "neo4j+s://398ffc2d.databases.neo4j.io"
NEO4J_USER     = "398ffc2d"
NEO4J_PASSWORD = "pxYFawIJyzFYV_kd6IkXOc-qjNT5heD-WCGS-EgY6Jg"
NEO4J_DATABASE = "398ffc2d"


def normalize_row(row):
    """Strip BOM from Excel-exported headers."""
    return {(k or "").lstrip("\ufeff").strip(): v for k, v in row.items()}


def first(row, *keys):
    for key in keys:
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def extract_linkedin(text):
    if not text:
        return ""
    match = LINKEDIN_RE.search(text.replace("\n", " "))
    if not match:
        return ""
    url = match.group(1).strip().rstrip(".,)")
    if not url.startswith("http"):
        url = "https://" + url.lstrip("/")
    return url


def build_name(row):
    name = first(row, "name")
    if name:
        return name
    first_name = first(row, "first_name")
    last_name = first(row, "last_name")
    if first_name and last_name:
        return f"{first_name} {last_name}"
    return first_name or last_name


def build_role(row):
    company = first(row, "What company do you work for?", "company")
    student_role = first(row, "role")
    school = first(row, "school")
    parts = [p for p in (company, school, student_role) if p]
    if company:
        return company
    if school and student_role:
        return f"{school} — {student_role}"
    return student_role or school


def load_guests(path):
    guests = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = normalize_row(raw)
            name = build_name(row)
            if not name:
                continue
            extra = first(row, "addition info")
            guests.append({
                "name":      name,
                "role":      build_role(row),
                "location":  first(row, "location", "school"),
                "website":   extract_linkedin(extra)
                    or first(row, "What is your LinkedIn profile?", "linkedin", "website"),
                "email":     first(row, "email"),
                "phone":     first(row, "phone_number", "phone"),
                "guestId":   first(row, "guest_id"),
                "createdAt": int(time.time() * 1000),
            })
    return guests

MERGE_QUERY = """
UNWIND $guests AS g
MERGE (u:User {name: g.name})
ON CREATE SET
    u.role      = g.role,
    u.location  = g.location,
    u.website   = g.website,
    u.email     = g.email,
    u.phone     = g.phone,
    u.guestId   = g.guestId,
    u.createdAt = g.createdAt
ON MATCH SET
    u.role      = CASE WHEN u.role IS NULL OR u.role = '' THEN g.role ELSE u.role END,
    u.location  = CASE WHEN u.location IS NULL OR u.location = '' THEN g.location ELSE u.location END,
    u.website   = CASE WHEN u.website IS NULL OR u.website = '' THEN g.website ELSE u.website END,
    u.email     = CASE WHEN u.email IS NULL OR u.email = '' THEN g.email ELSE u.email END,
    u.phone     = CASE WHEN u.phone IS NULL OR u.phone = '' THEN g.phone ELSE u.phone END,
    u.guestId   = CASE WHEN u.guestId IS NULL OR u.guestId = '' THEN g.guestId ELSE u.guestId END
RETURN count(u) AS total
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/import_guests.py path/to/guests.csv", file=sys.stderr)
        sys.exit(1)

    guests = load_guests(sys.argv[1])
    print(f"Loaded {len(guests)} guests from CSV.")

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(MERGE_QUERY, guests=guests)
            record = result.single()
            print(f"Done. {record['total']} nodes merged into Neo4j.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        driver.close()


if __name__ == "__main__":
    main()
