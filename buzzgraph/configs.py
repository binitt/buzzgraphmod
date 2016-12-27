import configparser

class Configs:
    input_csv = "data/pollution.csv"
    nodes_file = "data/output/nodes.csv"
    edges_file = "data/output/edges.csv"

def initialize():
    print("Loading configuration")
    config = configparser.RawConfigParser()
    config.read('resources/config.cfg')
    Configs.input_csv = config.get('DEFAULT', 'input_csv', 
        fallback=Configs.input_csv)
    Configs.nodes_file = config.get('DEFAULT', 'nodes_file', 
        fallback=Configs.nodes_file)
    Configs.edges_file = config.get('DEFAULT', 'edges_file', 
        fallback=Configs.edges_file)
    print("All configs loaded")


initialize()
