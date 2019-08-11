from bs4 import BeautifulSoup
from datetime import datetime
import logging
import re
import requests


URL = "https://apps.co.marion.or.us/jailrosters/mccf_roster.html#"


def get(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def parse_date(text):
    if not text:
        # The field is able to be missing and lack of presence
        # does not need to be logged.
        return None

    try:
        dt = datetime.strptime(text, "%m/%d/%Y")
    except ValueError as e:
        logging.error(e)
        return None
    return dt.date()


BAIL_PATTERN = re.compile(r"Initial Bail = \$([\d,]+)", flags=re.IGNORECASE)


def parse_bail(row):
    text = row.find("span").text

    match = BAIL_PATTERN.search(text)
    if match is None:
        return None

    bail_match = match.group(1)
    bail = int(bail_match.replace(",", ""))
    return bail


def parse_personal(row):
    cells = row.findChildren("td")
    values = [cell.text.strip() for cell in cells]
    sid, name, date_booked, court_date, release_date = values
    return {
        "booking_id": sid,
        "name": name,
        "date_booked": parse_date(date_booked),
        "court_date": parse_date(court_date),
        "release_date": parse_date(release_date),
    }


def parse_height(text):
    try:
        inches = int(text[-2:])
        feet = int(text[:-2])
        height = (12 * feet) + inches
    except ValueError as e:
        logging.error(e)
        height = None
    return height


def parse_weight(text):
    try:
        weight = int(text)
    except ValueError as e:
        logging.error(e)
        weight = None
    return weight


def parse_attributes(row):
    text = row.find("span").text
    values = [cell.strip() for cell in text.split("|")]
    _, _, race, sex, height_text, weight_text, hair, eyes, _ = values
    return {
        "race": race,
        "sex": sex,
        "height": parse_height(height_text),
        "weight": parse_weight(weight_text),
        "hair": hair,
        "eyes": eyes,
    }


def parse_charges(rows):
    charges = []
    authority = None
    skip_next = False
    for row in rows:
        if skip_next:
            skip_next = False
            continue

        cells = row.findChildren("td")
        if len(cells) == 3:
            # Begins a new table of charges, with values
            # describing the charging authority.
            authority_cell = cells[1]
            if not authority_cell.text.startswith("Authority:"):
                raise RuntimeError
            _, authority = map(str.strip, authority_cell.text.split(":", 1))
            # The next row will be headings for the table of charges.
            skip_next = True
        elif len(cells) == 5:
            # Row with a charge.
            values = [cell.text.strip() for cell in cells]
            _, name, statute, description, release = values
            charges.append({
                "authority": authority,
                "name": name,
                "statute": statute,
                "description": description,
                "release": release,
            })
        else:
            if len(cells) == 1:
                cell = cells[0]
                class_list = cell.attrs["class"]
                if "noPrint" in class_list:
                    # Row used for spacing.
                    continue

            # Should be unreachable.
            raise RuntimeError

    return charges


def scrape(url=URL):
    page = get(url)
    soup = BeautifulSoup(page, features="lxml")
    container = soup.find(attrs={"id": "data"})
    table = next(container.children)

    header = table.find_next("tr")
    columns = [cell.text.strip() for cell in header.findChildren("th")]
    expected_columns = ["SID", "Name", "Lodged", "Court", "Release"]

    if columns != expected_columns:
        raise RuntimeError(
            f"Expected table columns {expected_columns}, "
            f"instead found {columns}"
        )

    # Each row of the master table is itself a table.
    out = []
    subtables = table.findChildren("tbody")
    for subtable in subtables:
        rows = subtable.findChildren("tr")

        personal_row, attributes_row, *charge_rows, bail_row = rows
        personal = parse_personal(personal_row)
        attributes = parse_attributes(attributes_row)
        bail = parse_bail(bail_row)
        charges = parse_charges(charge_rows)

        out.append({
            **personal,
            **attributes,
            "bail": bail,
            "charges": charges,
        })

    return out
