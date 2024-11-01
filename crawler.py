import argparse
import logging
import os.path
import re
import time
import urllib.request
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import bs4.element

from graph_drawer import read_kit_file

NAMETABLE_CLASS = "v_phase_one-section dashboard-content"
KIT_INFO_REGEX = "Kit:[\d\D]*<br>"


def fetch_matches_page(code):
    request = urllib.request.Request(
        f"https://app.gedmatch.com/OneToManyFreeOriginalResults.php?kit={code}&xsubmit=Display+Results")
    request.add_header("Cookie", f"PHPSESSID={os.environ["PHPSESSID"]}")
    request.add_header("Referer", "https://app.gedmatch.com/")
    request.add_header("Sec-Ch-Ua", '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"')
    request.add_header("Sec-Ch-Ua-Mobile", "?0")
    request.add_header("Sec-Ch-Ua-Platform", "macOS")
    request.add_header("Sec-Fetch-Dest", "document")
    request.add_header("Sec-Fetch-Mode", "navigate")
    request.add_header("Sec-Fetch-Site", "same-origin")
    request.add_header("Sec-Fetch-User", "?1")
    request.add_header("User-Agent",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    result = urllib.request.urlopen(request)
    contents = result.read()
    logging.info("Response headers: ", result.headers)
    logging.getLogger().handlers[0].flush()

    return contents


def fetch_intersections_page(main_kit, rel_kit):
    data = {
        "kit1": main_kit,
        "kit2": rel_kit,
        "largest_threshold": "10",
        "shared_threshold": "10",
        "diff_threshold": "99",
        "xsubmit": "Display Results"
    }
    request = urllib.request.Request("https://app.gedmatch.com/people_match2.php", urlencode(data).encode())

    request.add_header("Cookie", f"PHPSESSID={os.environ["PHPSESSID"]}")
    request.add_header("Referer", "https://app.gedmatch.com/")
    request.add_header("Sec-Ch-Ua", '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"')
    request.add_header("Sec-Ch-Ua-Mobile", "?0")
    request.add_header("Sec-Ch-Ua-Platform", "macOS")
    request.add_header("Sec-Fetch-Dest", "document")
    request.add_header("Sec-Fetch-Mode", "navigate")
    request.add_header("Sec-Fetch-Site", "same-origin")
    request.add_header("Sec-Fetch-User", "?1")
    request.add_header("User-Agent",
                       "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    result = urllib.request.urlopen(request)
    contents = result.read()
    logging.info("Response headers: ", result.headers)
    logging.getLogger().handlers[0].flush()

    return contents


def write_to_file(kit_info, table_lines, kit):
    current_dir = os.path.dirname(__file__)

    file = open(os.path.join(current_dir, f"tables/{kit}.csv"), "x")

    # file.write(kit_info + "\n\n")

    file.writelines(",".join(line) + "\n" for line in table_lines)

    file.close()

    logging.info(f"Written {kit} to file")
    logging.getLogger().handlers[0].flush()


def parse_page(page, tags_info):
    parsed_html = BeautifulSoup(page, features="html.parser")
    entries = filter(lambda x: isinstance(x, bs4.element.Tag),
                     parsed_html.body.find('table', tags_info).children)

    lines = []

    for entry in entries:
        cols = entry.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        lines.append(cols)

    return lines


def get_kit_info(page):
    return re.search(KIT_INFO_REGEX, str(page)).group()[:-8]


def main():
    parser = argparse.ArgumentParser(prog="GEDMatch crawler")
    parser.add_argument("-k", "--kit")  # kit for which to get direct matches
    parser.add_argument("-r", "--recursion_depth")  # for how many direct matches get their matches
    parser.add_argument("-o", "--offset")  # offset to the prev param

    args = parser.parse_args()

    main_kit = args.kit
    if main_kit is None:
        print("No kit number given")
        exit(1)

    main_page = fetch_matches_page(main_kit)

    lines = parse_page(main_page, None)

    kit_info = get_kit_info(main_page)

    write_to_file(kit_info, lines, main_kit)

    codes = []

    for line in lines[1:]:
        codes.append(line[0])

    # get first 5 relatives
    for code in codes[0:5]:
        relative_page = fetch_matches_page(code)
        rel_lines = parse_page(relative_page)
        write_to_file(get_kit_info(relative_page), rel_lines, code)
        time.sleep(3)


def intsec_main():
    parser = argparse.ArgumentParser(prog="GEDMatch crawler")
    parser.add_argument("-k", "--kit")  # kit for which to get direct matches
    parser.add_argument("-r", "--recursion_depth")  # for how many direct matches get their matches
    parser.add_argument("-o", "--offset")  # offset to the prev param

    args = parser.parse_args()

    main_kit = args.kit
    if main_kit is None:
        print("No kit number given")
        exit(1)

    reader = read_kit_file(main_kit)

    kit_info = next(reader)
    next(reader)  # skip empty line

    rel_kits = []
    for line in reader:
        rel_kits.append(line[0])

    for kit in rel_kits[55:70]:
        intersection_page = fetch_intersections_page(main_kit, kit)
        lines = parse_page(intersection_page, {"class": "results-table"})
        write_to_file("kit_info", lines[2:], f"{main_kit}-{kit}")  # TODO 2 empty lines
        time.sleep(1)


if __name__ == '__main__':
    intsec_main()
