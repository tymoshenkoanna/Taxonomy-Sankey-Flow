import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import re

# Ensure the output shows up in JupyterLab in the output notebook below the code. Can use either "notebook" or "notebook_connected" the later one doesn't load the whole library into my .py code
pio.renderers.default = "notebook_connected"

# 1. Load Data
file_path = "/Users/annatymoshenko/Desktop/Docs/Data Visualisation/st_relations.csv"
df = pd.read_csv(file_path, sep=';') #in raw file the delimeter is set on ";" --> always check before working

df.columns = [c.strip() for c in df.columns]  


# 2. Precise Column Mapping 
# Column B: Pillar (pillar_name)
# Column H: L1 Category (cat_l1)
# Column I: L2 Category (cat_l2)
# Column J: L3 Category (cat_l3)
# Column E: clusters
# Column G: Relevant L3 categories for each cluster (cat_in_cluster)

#crucial step when working with the data of this type

df['cat_l1'] = df['cat_l1'].ffill()
df['cat_l2'] = df['cat_l2'].ffill()
df['cat_l3'] = df['cat_l3'].ffill()
df['clusters'] = df['clusters'].ffill()

# 3. Build Hierarchical Links
# A Sankey diagram needs a list of [Source, Target] pairs
links = []

# Level 1: L1 Category (H) -> L2 Category (I)
l1_to_l2 = df[['cat_l1', 'cat_l2']].drop_duplicates() # connecting L1 to L2, because names in L2 appear multiple times due to the file structure - drop duplicate command is used
for _, row in l1_to_l2.iterrows(): #loop that goes through your cleaned list of relationships row by row; "_" is a technical placeholder for the "index" (the row number), which is is not needed here; row contains the actual names (e.g., L1: "Finance", L2: "Personal Finance")
    links.append({'source': row['cat_l1'], 'target': row['cat_l2']}) # I am implementing the command "Go from Source A to Target B"

# Level 2: L2 Category (I) -> L3 Category (J) - same logic as above, only to the following sub categories
l2_to_l3 = df[['cat_l2', 'cat_l3']].drop_duplicates()
for _, row in l2_to_l3.iterrows():
    links.append({'source': row['cat_l2'], 'target': row['cat_l3']})

# Cluster to Pillar


# Level 3: L3 Category (Mapped from G) -> clusters (E) - the idea is to eventually map the L3 category to clusters, to show the complexity. In the column G I am listing all categories that are related to each cluster in the same row (Categories listed in G2 are connected to the cluster in cell E2, and they are listed there as text with the ";" delimeter)
# This is where we split the multi-line text in Column G
def clean_split(text):
    if pd.isna(text): return [] #if a cell is empty, it tells the code "don't do anything here, just return an empty list."
    return [t.strip() for t in re.split(r'[\n;]', str(text)) if t.strip()]#t.strip() removes any accidental leading or trailing spaces so that " Budget" becomes "Budget; re.split tells the code to cut the text every time it sees a New Line (\n) OR a Semicolon (;)

cluster_map = df[['clusters', 'cat_in_cluster']].dropna() #focuses only on the relationship between  Cluster names (Column E) and the list of L3 categories (Column G), throwing away any rows where these are missing
for _, row in cluster_map.iterrows(): # goes through each cluster one by one
    l3_items = clean_split(row['cat_in_cluster']) # calling the "clean_split" function that was defined earlier
    for item in l3_items:#for each item extracted by the function "clean_split"
        links.append({'source': item, 'target': row['clusters']}) # takes every single category from G Column and liks it to the cluster in column E
        
# Level 4 Cluster to Pillars
pillar_name = df['pillar_name'].iloc[0]
right_pillar = f"{pillar_name} (Total)"

unique_clusters = df['clusters'].unique()
for cluster in unique_clusters:
    links.append({'source': cluster, 'target': right_pillar})

    
# Convert to DataFrame and remove duplicates
links_df = pd.DataFrame(links).drop_duplicates()#creating a structured table from the above outputs

#defining unique L2 colours
unique_l2 = df['cat_l2'].unique().tolist()
unique_clusters = df['clusters'].unique().tolist()
green_shades = ["#4FB065", "#A7D4B1", "#195928"]
l2_color_map = {name: green_shades[i % len(green_shades)] for i, name in enumerate(unique_l2)}
l3_to_l2_map = df.set_index('cat_l3')['cat_l2'].to_dict()

# 4. Create Node IDs

nodes = list(pd.unique(links_df[['source', 'target']].values.ravel('K'))) 
# translating the output to the plotly language. Each category is getting the unique identifier by it

node_dict = {node: i for i, node in enumerate(nodes)} #assign a a unique number to every name in the list that was created above

# 5. Build Sankey Figure and color map 
node_colors = []
for name in nodes:
    # PILLAR & CLUSTERS: Orange
    if pillar_name in name or name == right_pillar or name in unique_clusters:
        node_colors.append("#FF8C00") 
    # L2 CATEGORIES: Distinct Green Shades
    elif name in unique_l2:
        node_colors.append(l2_color_map[name])
    # 3. L3 CATEGORIES: Find parent L2 and steal its color
    elif name in l3_to_l2_map:
        parent_l2 = l3_to_l2_map[name]
        parent_color = l2_color_map.get(parent_l2, "#90EE90") # Fallback to light green
        node_colors.append(parent_color)
        
    # 4. FALLBACK: Light Green (for any nodes not captured above)
    else:
        node_colors.append("#195928")

fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,#vertical padding between boxes
      thickness = 20, # controls the horizontal width of the vertical boxes.
      line = dict(color = "black", width = 0.5),
      label = nodes, # gives the boxes their names. It uses the master list of unique names we created earlier
      color = node_colors
    ),
    link = dict(
      source = links_df['source'].map(node_dict).tolist(),# tells the connecting ribbon where to start
      target = links_df['target'].map(node_dict).tolist(), # tells the connecting ribbon where to end
      value = [1] * len(links_df), #defines the thickness of the flowing lines
      color = "rgba(200, 200, 200, 0.6)"
  ))])

fig.update_layout(
    title_text="Hierarchical Content Flow: Finance, Business & Markets",
    font_size=10,
    height=800
)

# Display in Jupyter
fig.show()
