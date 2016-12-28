

class WordCloud:
    


def main():
    try:
        cloud = WordCloud()
        cloud.process_file(Configs.input_excel)
        pollution.write_node_csv(Configs.nodes_file)
        pollution.write_edge_csv(Configs.edges_file)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** Top Level Exception:", file=sys.stderr)
#        traceback.print_exc()
        print(traceback.format_exc(), file=sys.stderr)
