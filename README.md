# Taxonomy-Sankey-Flow
A Python-based visualization tool that transforms multi-level .xlxs  and .csv taxonomies into interactive Plotly Sankey diagrams, featuring automated parent-child color inheritance and multi-pillar routing logic

This is my Python script for turning a messy CSV file into a Sankey Diagram. I used this to visualize how different finance and business categories flow into each other and eventually group into big clusters.
This code is the base for the bigger taxonomy and is the first attempt to visualize the flow.

What this script does
-- Cleans the Data: It uses .ffill() to fill in empty gaps in the spreadsheet so the hierarchy doesn't break.
-- Splits Complex Cells: In my file, some cells had multiple categories separated by ; or new lines. I wrote a function to split those up so every item gets its own ribbon in the chart.
-- Automatic Coloring: I set it up so that "Level 2" categories get shades of green, and the final "Clusters" and "Pillars" turn orange.
-- Connects Everything: It automatically builds the "Source" and "Target" points that the diagram needs to draw the lines.

Code is written in Anaconda and JupiterLab, source file st_relations.csv stored locally
