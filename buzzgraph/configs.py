import configparser

class Configs:
    input_file = "data/pollution.xlsx"
    input_sheet = "Data"
    input_column = 1
    input_ignore_header = True
    nodes_file = "data/output/nodes.csv"
    edges_file = "data/output/edges.csv"

def initialize():
    print("Loading configuration")
    config = configparser.RawConfigParser()
    config.read('resources/config.cfg')

    Configs.input_file = config.get('DEFAULT', 'input_file', 
        fallback=Configs.input_file)
    Configs.input_sheet = config.get('DEFAULT', 'input_sheet', 
        fallback=Configs.input_sheet)
    Configs.input_column = config.getint('DEFAULT', 'input_column', 
        fallback=Configs.input_column)
    Configs.input_ignore_header = config.getboolean('DEFAULT', 
        'input_ignore_header', fallback=Configs.input_sheet)

    Configs.nodes_file = config.get('DEFAULT', 'nodes_file', 
        fallback=Configs.nodes_file)

    Configs.edges_file = config.get('DEFAULT', 'edges_file', 
        fallback=Configs.edges_file)

    print("All configs loaded")


initialize()
