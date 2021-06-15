import logic.bpmn_builder as bpmn_builder
import os


def get_xml_file(file_path, dataColumns):
    traces = bpmn_builder.DataLoading.get_traces_from_file(file_path, dataColumns)
    graph = bpmn_builder.createGraph(traces)
    basename = os.path.splitext(os.path.basename(file_path))[0]
    bpmn_builder.export_xml_file(graph, "generated_xmls", basename)
    with open(f"generated_xmls/{basename}.xml", "r") as file:
        content = file.read()
        return content
