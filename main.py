import logging
import os.path
import re
import time
import urllib.request
from bs4 import BeautifulSoup
import bs4.element

NAMETABLE_CLASS = "v_phase_one-section dashboard-content"
KIT_INFO_REGEX = "Kit:[\d\D]*<br>"


def fetch_page(code):
    request = urllib.request.Request(
        f"https://app.gedmatch.com/OneToManyFreeOriginalResults.php?kit={code}&xsubmit=Display+Results")
    request.add_header("Cookie", "PHPSESSID=lr57bv29mggj4p02qnnblbuisp")
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
    contents = urllib.request.urlopen(request).read()
    return contents


def write_to_file(kit_info, table_lines, code):
    current_dir = os.path.dirname(__file__)

    file = open(os.path.join(current_dir, f"tables/{code}.csv"), "x")

    file.write(kit_info + "\n\n")

    file.writelines(",".join(line) + "\n" for line in table_lines)

    file.close()

    logging.info(f"Written {code} to file")
    logging.getLogger().handlers[0].flush()


def parse_page(page):
    parsed_html = BeautifulSoup(page, features="html.parser")
    entries = filter(lambda x: isinstance(x, bs4.element.Tag), parsed_html.body.find('table').children)

    lines = []

    for entry in entries:
        cols = entry.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        lines.append(cols)

    return lines


def get_kit_info(page):
    return re.search(KIT_INFO_REGEX, str(page)).group()[:-8]


def main():
    main_user_code = "DE5484843"
    main_page = fetch_page(main_user_code)

    lines = parse_page(main_page)

    kit_info = get_kit_info(main_page)

    write_to_file(kit_info, lines, main_user_code)

    codes = []

    for line in lines[1:]:
        codes.append(line[0])

    # get first 50 relatives
    for code in codes[0:50]:
        relative_page = fetch_page(code)
        rel_lines = parse_page(relative_page)
        write_to_file(get_kit_info(relative_page), rel_lines, code)
        time.sleep(3)


if __name__ == '__main__':
    main()
