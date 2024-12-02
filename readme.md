# DNA relations visualizer

## About
### Visualize DNA relations from GEDMatch
#### Prerequisites:
1. Your DNA file is uploaded to GEDMatch and you know your kit number
2. Login to GEDMatch and get your PHPSESSID from cookies (since there's no API)

## Run
1. Execute the [crawler.py](/crawler.py) with params:
   1. **-k** *kit_number* - the kit number for which the graph is to be drawn
   2. **-r** *int* - for how many direct matches get their matches
   3. **-o** *int* - offset to the previous param
   4. ENV: PHPSESSID - the PHPSESSID from gedmatch cookies
2. Optionally, if you know where some kits are from, you can add country info to [known_countries.yml](/supervised/known_countries.yml)
3. Execute the [graph_drawer.py](/graph_drawer.py) to draw the graph into *graph.gv* file
4. Go to https://dreampuf.github.io/GraphvizOnline/ and paste contents of graph.gv into the editor

## Result
### The result will look something like this depending on the engine chosen (here it's osage)
![graph](/graphviz.svg)