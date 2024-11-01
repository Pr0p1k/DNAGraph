import os
import csv
import yaml
from typing import Dict, Any

TABLES_PATH = "tables2"
LIMIT = 70


def read_kit_file(code):
    current_dir = os.path.dirname(__file__)

    filename = os.path.join(current_dir, f"{TABLES_PATH}/{code}.csv")

    file = open(filename, "r")

    csvreader = csv.reader(file)

    return csvreader


def calc_edge_color(mrca):
    mrca = float(mrca)
    if mrca <= 4.1:
        return "green"
    elif mrca <= 4.5:
        return "yellow"
    elif mrca <= 5.0:
        return "orange"
    else:
        return "red"


GRAPH: dict[Any, Any] = dict()
# {
# "code": [(code, mrca)]
# }
IGNORE_LIST = ["AR8211960"]


with open(os.path.dirname(__file__) + "/supervised/known_countries.yml", "r") as locations_yaml_file:
    output = yaml.safe_load(locations_yaml_file)

KNOWN_LOCATIONS = output


def main():
    me_code = "DE5484843"
    reader = read_kit_file(me_code)

    kit_info = next(reader)
    next(reader)  # skip empty line

    rel_kits = []
    for line in reader:
        rel_kits.append(line)

    graph_file = open(os.path.dirname(__file__) + "/graph.gv", "w")

    GRAPH[me_code] = []

    graph_file.write("graph {\n")
    graph_file.write("graph [outputorder=edgesfirst];\nnode [style=filled fillcolor=white];\n")
    for kit in rel_kits[1:LIMIT]:
        GRAPH[me_code].append((kit[0], kit[6]))

    for kit in rel_kits[1:LIMIT]:
        reader = read_kit_file(f"{me_code}-{kit[0]}")

        for line in reader:
            if len(line) == 0:
                continue

            rel_code = line[0]

            if rel_code == me_code:
                continue

            mrca = line[8]
            if kit[0] in GRAPH:
                GRAPH[kit[0]].append((rel_code, mrca))
            else:
                GRAPH[kit[0]] = [(rel_code, mrca)]

            if rel_code in GRAPH:
                GRAPH[rel_code].append((kit[0], mrca))
            else:
                GRAPH[rel_code] = [(kit[0], mrca)]
            # graph_file.write(f"{kit[0]} -- {rel_code}[label={mrca}]\n")  # Me -- {rel_code}[label={line[5]}]\n

    # set country clusters
    for country, kit_list in KNOWN_LOCATIONS.items():
        graph_file.write(f'subgraph cluster_{country} {{ \n label = "{country}"\n style=filled;\n color=lightgrey;\n')
        for kit in kit_list:
            graph_file.write(kit + "\n")
        graph_file.write("}\n")

    # draw my direct connections
    for kit in rel_kits[1:LIMIT]:
        if kit[0] in GRAPH and len(GRAPH[kit[0]]) > 0:  # only those that are connected with someone else
            graph_file.write(f"{me_code} -- {kit[0]}[label={kit[6]} color=blue]\n")

    drawn_set = set()

    for kit, matches in GRAPH.items():
        if len(matches) > 1:
            for match in matches:
                if match[0] in GRAPH and len(GRAPH[match[0]]) > 1 \
                        and kit != me_code and (kit, match[0]) not in drawn_set \
                        and kit not in IGNORE_LIST and match[0] not in IGNORE_LIST:
                    drawn_set.add((match[0], kit))
                    graph_file.write(f"{kit} -- {match[0]}[color={calc_edge_color(match[1])}]\n")

    graph_file.write("}\n")

    graph_file.close()


if __name__ == '__main__':
    main()
