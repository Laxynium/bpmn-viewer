import os

import numpy as np
import pandas as pd
from itertools import product
import copy

from opyenxes.data_in.XUniversalParser import XUniversalParser


class DataColumns:
    def __init__(self, id_col, activity_col, datetime_col):
        self.id = id_col
        self.activity = activity_col
        self.datetime = datetime_col


class DataLoading:
    def get_traces_csv(file_name, sep, columns: DataColumns):
        df = pd.read_csv(file_name, sep=sep)
        dfs = df[[columns.id, columns.activity, columns.datetime]]
        dfs = (
            dfs.sort_values(by=[columns.id, columns.datetime])
            .groupby([columns.id])
            .agg({columns.activity: ";".join})
        )
        dfs["trace"] = [trace.split(";") for trace in dfs[columns.activity]]
        values = np.array(dfs[["trace"]].values, dtype=object)
        values = np.unique(values)
        return list(values)

    def get_traces_xes(file_path):
        traces = []
        with open(file_path) as log_file:
            # parse the log
            logs = XUniversalParser().parse(log_file)[0]
            for log in logs:
                new_list = []
                traces.append(new_list)
                id = log.get_attributes()["concept:name"]
                for event in log:
                    attrs = event.get_attributes()
                    activity = attrs["Activity"]
                    timestamp = attrs["time:timestamp"]
                    new_list.append(activity.get_value())
                    # print(id,',',activity,",", timestamp)
        return traces

    def get_traces_from_file(file_path, dataColumns: DataColumns, separator = ","):
        filename, extension = os.path.splitext(file_path)
        if extension == ".csv":
            return DataLoading.get_traces_csv(file_path, separator, dataColumns)
        if extension == ".xes":
            return DataLoading.get_traces_xes(file_path)


def get_start_events(traces):
    starts = set()
    for trace in traces:
        first = trace[0]
        starts.add(first)
    return starts


def get_end_events(traces):
    ends = set()
    for trace in traces:
        last = trace[-1]
        ends.add(last)
    return ends


def get_aba_pattern(traces):
    result = dict()
    for trace in traces:
        tripled = list(zip(trace, trace[1:] + [None], trace[2:] + [None, None]))
        for [first, second, third] in tripled:
            if first == third and second != first:
                x = result.get(first, set())
                x.add(second)
                result.setdefault(first, x)
    return result


def get_aba_and_bab_pattern(traces):
    patterns = get_aba_pattern(traces)
    result = dict()
    for (first, seconds) in patterns.items():
        for second in seconds:
            sec_patt = patterns.get(second, set())
            if first in sec_patt:
                x = result.get(first, set())
                x.add(second)
                result.setdefault(first, x)
    return result


def get_direct_succession(traces):
    direct_succession = dict()
    for trace in traces:
        paired = list(zip(trace, trace[1:] + [None]))
        for [first, second] in paired:
            x = direct_succession.get(first, set())
            x.add(second)
            direct_succession.setdefault(first, x)
    return direct_succession


def get_causality(traces):
    # a, b | a->c,d ^ b->e,f
    # node1 = a set1 = c,d | node2 = b set2 = e,f
    # a->b & (b!->a | a<>b)
    # if node2 in set1 and ( node1 not in set2 or node2 in patterns.get(node1,set())):
    direct_succession = get_direct_succession(traces)
    patterns = get_aba_and_bab_pattern(traces)
    causality = dict()
    nodes = direct_succession.keys()
    for aNode, bNode in product(nodes, nodes):
        if aNode != bNode:
            a_set = direct_succession.get(aNode, set())
            b_set = direct_succession.get(bNode, set())
            if bNode in a_set and (
                (aNode not in b_set) or (bNode in patterns.get(aNode, set()))
            ):
                causality.setdefault(aNode, set()).add(bNode)
    return causality


def get_inv_causality(causality):
    inv_causality = dict()
    causality_val_len_1 = {
        key: next(iter(value)) for key, value in causality.items() if len(value) == 1
    }
    for k, v in causality_val_len_1.items():
        inv_causality.setdefault(v[0], set()).add(k)
    return inv_causality


def get_parallel(traces):
    direct_succession = get_direct_succession(traces)
    patterns = get_aba_and_bab_pattern(traces)
    parallel = set()
    for aNode in direct_succession:
        a_set = direct_succession[aNode]
        for bNode in a_set:
            b_set = direct_succession.get(bNode, set())
            if (
                bNode in a_set
                and aNode in b_set
                and bNode not in patterns.get(aNode, set())
            ):
                parallel.add((aNode, bNode))
    return parallel


def get_looped_events(traces):
    result = set()
    for log in traces:
        for a, b in zip(log, log[1:]):
            if a is b:
                result.add(a)
    return result


def remove_one_loops(traces):
    result = copy.deepcopy(traces)
    for idx1, trace in enumerate(traces):
        paired = zip(trace, trace[1:] + [None])
        for idx2, [a, b] in enumerate(paired):
            if a is b:
                result[idx1].remove(a)
    return [list(y) for y in set([tuple(x) for x in result])]


class InMemoryGraph:
    def __init__(self, *args):
        self.events = set()
        self.end = None
        self.and_gateways = set()
        self.xor_gateways = set()
        self.edges = set()
        self.gatewaysEdges = set()

    def add_event(self, name):
        self.events.add(name)

    def add_end_event(self, name):
        self.end = name

    def add_and_gateway(self, name, type):
        self.and_gateways.add((name, type))

    def add_xor_gateway(self, name, type):
        self.xor_gateways.add((name, type))

    def add_edge(self, source, target):
        self.edges.add((source, target))

    def add_and_split_gateway(self, source, targets):
        gateway = "ANDs " + str(source) + "->" + str(targets)
        self.add_and_gateway(gateway, "SPLIT")
        self.add_edge(source, gateway)
        self.gatewaysEdges.add((source, gateway))
        for target in targets:
            self.add_edge(gateway, target)
            self.gatewaysEdges.add((gateway, target))

    def add_xor_split_gateway(self, source, targets, *args):
        gateway = "XORs " + str(source) + "->" + str(targets)
        self.add_xor_gateway(gateway, "SPLIT")
        self.add_edge(source, gateway)
        self.gatewaysEdges.add((source, gateway))
        for target in targets:
            self.add_edge(gateway, target)
            self.gatewaysEdges.add((gateway, target))

    def add_and_merge_gateway(self, sources, target):
        gateway = "ANDm " + str(sources) + "->" + str(target)
        self.add_and_gateway(gateway, "MERGE")
        self.add_edge(gateway, target)
        self.gatewaysEdges.add((gateway, target))
        for source in sources:
            self.add_edge(source, gateway)
            self.gatewaysEdges.add((source, gateway))

    def add_xor_merge_gateway(self, sources, target):
        gateway = "XORm " + str(sources) + "->" + str(target)
        self.add_xor_gateway(gateway, "MERGE")
        self.add_edge(gateway, target)
        self.gatewaysEdges.add((gateway, target))
        for source in sources:
            self.add_edge(source, gateway)
            self.gatewaysEdges.add((source, gateway))

    def add_looped_event(self, event):
        self.add_xor_split_gateway(event, {event})

def createGraph(traces):
    looped_events = get_looped_events(traces)
    traces = remove_one_loops(traces)
    start_set_events = get_start_events(traces)
    end_set_events = get_end_events(traces)
    direct_succession = get_direct_succession(traces)
    causality = get_causality(traces)
    parallel_events = get_parallel(traces)
    inv_causality = get_inv_causality(causality)

    graph = InMemoryGraph()
    # adding split gateways based on causality
    for event in causality:
        if len(causality[event]) > 1:
            if tuple(causality[event]) in parallel_events:
                graph.add_and_split_gateway(event, causality[event])
            else:
                graph.add_xor_split_gateway(event, causality[event])

    # adding merge gateways based on inverted causality
    for event in inv_causality:
        if len(inv_causality[event]) > 1:
            if tuple(inv_causality[event]) in parallel_events:
                graph.add_and_merge_gateway(inv_causality[event], event)
            else:
                graph.add_xor_merge_gateway(inv_causality[event], event)
        elif len(inv_causality[event]) == 1:
            source = list(inv_causality[event])[0]
            graph.add_edge(source, event)

    # # adding start event
    graph.add_event("start")
    if len(start_set_events) > 1:
        if tuple(start_set_events) in parallel_events:
            graph.add_and_split_gateway("start", start_set_events)
        else:
            graph.add_xor_split_gateway("start", start_set_events)
    else:
        graph.add_edge("start", list(start_set_events)[0])

    # # adding end event
    graph.add_end_event("end")
    if len(end_set_events) > 1:
        if tuple(end_set_events) in parallel_events:
            graph.add_and_merge_gateway(end_set_events, "end")
        else:
            graph.add_xor_merge_gateway(end_set_events, "end")
    else:
        graph.add_edge(list(end_set_events)[0], "end")

    for e in looped_events:
        graph.add_looped_event(e)
    return graph


import bpmn_python.bpmn_diagram_rep as diagram
import bpmn_python.bpmn_diagram_layouter as layouter
from typing import List, Set, Tuple, AnyStr


class BpmnGraphCreator:
    def __init__(self):
        self.bpmn = diagram.BpmnDiagramGraph()
        self.bpmn.create_new_diagram_graph("d1")
        self.pid = self.bpmn.add_process_to_diagram("p1")
        self.createdNodes = dict()

    def add_start(self, name):
        [self.start_id, _] = self.bpmn.add_start_event_to_diagram(self.pid, name)
        self.createdNodes.setdefault(name, self.start_id)

    def add_end_event(self, name):
        [end_id, _] = self.bpmn.add_end_event_to_diagram(self.pid, name)
        self.createdNodes.setdefault(name, end_id)

    def add_and_split_gateways(self, gateways: List[Tuple[AnyStr, Set[AnyStr]]]):
        for source, targets in gateways:

            source_id = None
            if source not in self.createdNodes:
                [source_id, _] = self.bpmn.add_task_to_diagram(self.pid, source)
                self.createdNodes.setdefault(source, source_id)
            else:
                source_id = self.createdNodes[source]

            target_ids = {}
            for target in targets:
                if target not in self.createdNodes:
                    [target_id, _] = self.bpmn.add_task_to_diagram(self.pid, target)
                    self.createdNodes.setdefault(target, target_id)
                target_ids.setdefault(self.createdNodes[target])

            gateway_name = "ANDs " + str(source) + "->" + str(targets)

            [gateway_id, _] = self.bpmn.add_parallel_gateway_to_diagram(
                self.pid, gateway_name
            )
            self.createdNodes.setdefault(gateway_name, gateway_id)

            self.bpmn.add_sequence_flow_to_diagram(self.pid, source_id, gateway_id)
            for t_id in target_ids:
                self.bpmn.add_sequence_flow_to_diagram(self.pid, gateway_id, t_id)

    def add_xor_split_gateways(self, gateways: List[Tuple[AnyStr, Set[AnyStr]]]):
        for source, targets in gateways:

            source_id = None
            if source not in self.createdNodes:
                [source_id, _] = self.bpmn.add_task_to_diagram(self.pid, source)
                self.createdNodes.setdefault(source, source_id)
            else:
                source_id = self.createdNodes[source]

            target_ids = {}
            for target in targets:
                if target not in self.createdNodes:
                    [target_id, _] = self.bpmn.add_task_to_diagram(self.pid, target)
                    self.createdNodes.setdefault(target, target_id)
                target_ids.setdefault(self.createdNodes[target])

            gateway_name = "XORs " + str(source) + "->" + str(targets)

            [gateway_id, _] = self.bpmn.add_exclusive_gateway_to_diagram(
                self.pid, gateway_name
            )
            self.createdNodes.setdefault(gateway_name, gateway_id)

            self.bpmn.add_sequence_flow_to_diagram(self.pid, source_id, gateway_id)
            for t_id in target_ids:
                self.bpmn.add_sequence_flow_to_diagram(self.pid, gateway_id, t_id)

    def add_and_merge_gateways(self, gateways: List[Tuple[Set[AnyStr], AnyStr]]):
        for sources, target in gateways:

            target_id = None
            if target not in self.createdNodes:
                [target_id, _] = self.bpmn.add_task_to_diagram(self.pid, target)
                self.createdNodes.setdefault(target, target_id)
            else:
                target_id = self.createdNodes[target]

            source_ids = {}
            for source in sources:
                if source not in self.createdNodes:
                    [source_id, _] = self.bpmn.add_task_to_diagram(self.pid, source)
                    self.createdNodes.setdefault(source, source_id)
                source_ids.setdefault(self.createdNodes[source])

            gateway_name = "XORm " + str(target) + "->" + str(sources)

            [gateway_id, _] = self.bpmn.add_parallel_gateway_to_diagram(
                self.pid, gateway_name
            )
            self.createdNodes.setdefault(gateway_name, gateway_id)

            self.bpmn.add_sequence_flow_to_diagram(self.pid, gateway_id, target_id)
            for s_id in source_ids:
                self.bpmn.add_sequence_flow_to_diagram(self.pid, s_id, gateway_id)

    def add_xor_merge_gateways(self, gateways: List[Tuple[Set[AnyStr], AnyStr]]):
        for sources, target in gateways:

            target_id = None
            if target not in self.createdNodes:
                [target_id, _] = self.bpmn.add_task_to_diagram(self.pid, target)
                self.createdNodes.setdefault(target, target_id)
            else:
                target_id = self.createdNodes[target]

            source_ids = {}
            for source in sources:
                if source not in self.createdNodes:
                    [source_id, _] = self.bpmn.add_task_to_diagram(self.pid, source)
                    self.createdNodes.setdefault(source, source_id)
                source_ids.setdefault(self.createdNodes[source])

            gateway_name = "XORm " + str(target) + "->" + str(sources)

            [gateway_id, _] = self.bpmn.add_exclusive_gateway_to_diagram(
                self.pid, gateway_name
            )
            self.createdNodes.setdefault(gateway_name, gateway_id)

            self.bpmn.add_sequence_flow_to_diagram(self.pid, gateway_id, target_id)
            for s_id in source_ids:
                self.bpmn.add_sequence_flow_to_diagram(self.pid, s_id, gateway_id)

    def add_edges(self, edges: List[Tuple[AnyStr, AnyStr]]):
        for source, target in edges:
            if target not in self.createdNodes:
                [target_id, _] = self.bpmn.add_task_to_diagram(self.pid, target)
                self.createdNodes.setdefault(target, target_id)
            if source not in self.createdNodes:
                [source_id, _] = self.bpmn.add_task_to_diagram(self.pid, source)
                self.createdNodes.setdefault(source, source_id)

            source_id = self.createdNodes[source]
            target_id = self.createdNodes[target]

            self.bpmn.add_sequence_flow_to_diagram(self.pid, source_id, target_id)


def export_xml_file(inMemoryGraph: InMemoryGraph, dir, file_name):
    creator = BpmnGraphCreator()

    creator.add_end_event(inMemoryGraph.end)
    creator.add_start(list(inMemoryGraph.events)[0])

    and_split_gateways = [
        (
            [source for source, target in inMemoryGraph.edges if target == gateway[0]][
                0
            ],
            [target for source, target in inMemoryGraph.edges if source == gateway[0]],
        )
        for gateway in filter(lambda g: g[1] == "SPLIT", inMemoryGraph.and_gateways)
    ]
    creator.add_and_split_gateways(and_split_gateways)

    xor_split_gateways = [
        (
            [source for source, target in inMemoryGraph.edges if target == gateway[0]][
                0
            ],
            [target for source, target in inMemoryGraph.edges if source == gateway[0]],
        )
        for gateway in filter(lambda g: g[1] == "SPLIT", inMemoryGraph.xor_gateways)
    ]
    creator.add_xor_split_gateways(xor_split_gateways)

    and_merge_gateways = [
        (
            [source for source, target in inMemoryGraph.edges if target == gateway[0]],
            [target for source, target in inMemoryGraph.edges if source == gateway[0]][
                0
            ],
        )
        for gateway in filter(lambda g: g[1] == "MERGE", inMemoryGraph.and_gateways)
    ]
    creator.add_and_merge_gateways(and_merge_gateways)

    xor_merge_gateways = [
        (
            [source for source, target in inMemoryGraph.edges if target == gateway[0]],
            [target for source, target in inMemoryGraph.edges if source == gateway[0]][
                0
            ],
        )
        for gateway in filter(lambda g: g[1] == "MERGE", inMemoryGraph.xor_gateways)
    ]
    creator.add_xor_merge_gateways(xor_merge_gateways)

    edges = [
        (source, target)
        for source, target in inMemoryGraph.edges.difference(
            inMemoryGraph.gatewaysEdges
        )
    ]
    creator.add_edges(edges)

    # layouter.generate_layout(creator.bpmn)    
    creator.bpmn.export_xml_file(f"{dir}{os.path.sep}", f"{file_name}.xml")
