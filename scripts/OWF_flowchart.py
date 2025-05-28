
# CONDA ENV: graphviz

from graphviz import Graph, Digraph, Source
import json
import os


    
models_path = '../model_json/CST/Parent'
model_template = os.path.join(
    models_path, '{region}.json')

fill_colors = {
    'storage': 'blue',
    'catchment': 'lightblue',
    'discharge': 'lightblue',
    'input': 'lightblue',
    'output': 'pink'
}

font_colors = {
    'storage': 'white'
}

node_shapes = {
    'storage': 'rect'
}

font_sizes = {
    'storage': 14
}

subgraph_attrs = {
    'style': 'filled',
    'color': '#f0f0f0'
}


def create_digraph(nodes, edges, node_lookup, up_nodes, down_nodes, 
    focal_system, filename, focal_names=None, output_format='png'):

    print('creating ' + focal_system)
    all_nodes = []
    all_edges = []    
    focal_nodes = None
    all_focal_names = []
    
    subgraphs = {}
    
    parent = Digraph(name=focal_system, format=output_format)
    
    if focal_names:
        focal_nodes = [node for node in nodes if node['name'] in focal_names]
        all_focal_names = focal_names[:]
        for focal_name in focal_names:
    #         print(focal_name)
            all_focal_names.extend([n['name'] for n in up_nodes.get(focal_name, []) if n['name'] not in all_focal_names])
            all_focal_names.extend([n['name'] for n in down_nodes.get(focal_name, []) if n['name'] not in all_focal_names])
    #         up_node_names = [n['name'] for n in up_nodes.get(node['name'], [])]
    #         down_node_names = [n['name'] for n in down_nodes.get(node['name'], [])]

    def add_node(node, subgraph, color='black'):
        if node['name'] in all_nodes:
            return

        all_nodes.append(node['name'])
        label = node['name'].replace('_', ' ')

        fontsize = str(font_sizes.get(node['type'], 14))
        fillcolor = fill_colors.get(node['type'], 'lightgray')
        fontcolor = font_colors.get(node['type'], 'black')
        shape = node_shapes.get(node['type'], 'ellipse')

        if node['type'] == 'storage':
            if node['name'].find('_') >= 0:
                label = label.title()
            else: # this is a WTP
                fillcolor = 'grey'
                fontcolor = 'black'

        if node['name'].find('evap') > 0:
            fillcolor = 'mediumseagreen'
        if node['name'].find('precip') > 0:
            fillcolor = 'steelblue'
        elif node['name'].find('Dtot') > 0:
            fillcolor = 'salmon'
        elif node['name'].find('Denv') > 0:
            fillcolor = 'limegreen'
        
        
        elif node['name'] == 'meta_downstream_carreno':
            fillcolor = 'peachpuff'

                
        graphprops = dict(
            shape=shape,
            color=color,
            style='filled',
            fontcolor=fontcolor,
            fillcolor=fillcolor,
            label=label,
            fontsize=fontsize,
            ratio = "1"
        )

        if all_focal_names and node['name'] not in all_focal_names:
            for prop in ['style', 'fillcolor', 'fontcolor', 'color']:
                graphprops.pop(prop, None)
#             graphprops['fillcolor'] = 'lightgrey'

        subgraph.node(node['name'], **graphprops)
        
    for node in nodes:
        
        region = node.get('region')
        if region not in subgraphs:
            # note: subgraph name must start with "cluster_"
            subgraphs[region] = Digraph(name='cluster_{}'.format(region), graph_attr=subgraph_attrs)
        subgraph = subgraphs[region]
        
        _down_nodes = down_nodes.get(node['name'], [])
        _up_nodes = up_nodes.get(node['name'], [])
        if _up_nodes or _down_nodes:
            add_node(node, subgraph)

        for down_node in _down_nodes:
            edge = (node['name'], down_node['name'])
            if edge in all_edges:
                continue
            all_edges.append(edge)
            add_node(down_node, subgraph)
            color = 'black'
            if all_focal_names and not (edge[0] in all_focal_names and edge[1] in all_focal_names):
                color = 'grey'
            graph = subgraph if node['region'] == down_node['region'] else parent
            graph.edge(edge[0], edge[1], color=color)

        for up_node in _up_nodes:
            edge = (up_node['name'], node['name'])
            if edge in all_edges:
                continue
            all_edges.append(edge)
            add_node(up_node, subgraph)

            color = 'black'
            if all_focal_names and not (edge[0] in all_focal_names and edge[1] in all_focal_names):
                color = 'grey'
            
            graph = subgraph if node['region'] == down_node['region'] else parent
            graph.edge(edge[0], edge[1], color=color)
    
    for child in subgraphs.values():
        parent.subgraph(child)
    parent.render(filename, view=False)
    return parent
    #del parent

# setup model
nodes = []
edges = []
node_lookup = {}
up_nodes = {}
down_nodes = {}

exclude = ['Dtot_output_node']

for region in ['OWF_CST']:
    with open(model_template.format(region=region)) as f:
        model = json.load(f)
        edges.extend([e for e in model['edges'] if not(e[0] in exclude or e[1] in exclude)])
        for node in model['nodes']:
            if node['name'] in exclude:
                continue
            node['region'] = region
            nodes.append(node)
            
print('Total nodes: {}'.format(len(nodes)))

node_lookup = {node['name']: node for node in nodes}

for edge in edges:
    up_node = node_lookup.get(edge[0])
    down_node = node_lookup.get(edge[1])
    if up_node and down_node:
        up_nodes[down_node['name']] = up_nodes.get(down_node['name'], []) + [up_node]
        down_nodes[up_node['name']] = down_nodes.get(up_node['name'], []) + [down_node]


OUTPUT_FORMAT_LIST = ['png', 'pdf']
for OUTPUT_FORMAT in OUTPUT_FORMAT_LIST:
    asd = create_digraph(nodes, edges, node_lookup, up_nodes, down_nodes,
        'system', '../figures/OWF_flowchart/OWF_model', output_format=OUTPUT_FORMAT)
    zxc = asd.unflatten(stagger=3)
    zxc.view()
    