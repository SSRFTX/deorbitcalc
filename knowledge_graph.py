import networkx as nx

def build_graph():
    G = nx.DiGraph()
    orbits = {"LEO": {"type": "orbit", "alt_min_km": 160, "alt_max_km": 2000}, "MEO": {"type": "orbit", "alt_min_km": 2000, "alt_max_km": 35786}, "GEO": {"type": "orbit", "alt_min_km": 35786, "alt_max_km": 35786 }}
    for name, attrs in orbits.items():
        G.add_node(name, **attrs)
        regulators = { "FCC": {"type": "regulator", "country": "USA","disposal_rule_years": 5},"ITU": {"type": "regulator", "country": "International",    "disposal_rule_years": 25}, "ESA": {"type": "regulator", "country": "Europe", "disposal_rule_years": 25},}
        for name, attrs in regulators.items():
            G.add_node(name, **attrs)
        G.add_edge("FCC", "LEO", relation="regulates", rule="5-year post-mission disposal")
        G.add_edge("ITU", "LEO", relation="regulates", rule="25-year guidelines")
        G.add_edge("ESA", "LEO", relation="regulates", rule="25-year clean space initiative")
        operators = {
        "SpaceX": {"type": "operator", "constellation": "Starlink",
                   "country": "USA"},
        "OneWeb": {"type": "operator", "constellation": "OneWeb",
                   "country": "UK"},
        "Planet": {"type": "operator", "constellation": "Flock",
                   "country": "USA"},
    }
        for name, attrs in operators.items():
            G.add_node(name, **attrs)
        G.add_edge("SpaceX", "FCC", relation="licensed_by")
        G.add_edge("OneWeb", "ITU", relation="licensed_by")
        G.add_edge("Planet", "FCC", relation="licensed_by")
        satellites = {
        "Starlink-1000": {"type": "satellite", "altitude_km": 550,
                          "mass_kg": 260, "has_drag_sail": False},
        "OneWeb-100": {"type": "satellite", "altitude_km": 1200,
                       "mass_kg": 150, "has_drag_sail": False},
        "Dove-50": {"type": "satellite", "altitude_km": 475,
                    "mass_kg": 5, "has_drag_sail": False},
        "DragSail-Demo": {"type": "satellite", "altitude_km": 500,
                          "mass_kg": 150, "has_drag_sail": True,
                          "sail_area_m2": 10.0},
    }
        for name, attrs in satellites.items():
            G.add_node(name, **attrs)
        G.add_edge("Starlink-1000", "SpaceX", relation="operated_by")
        G.add_edge("OneWeb-100", "OneWeb", relation="operated_by")
        G.add_edge("Dove-50", "Planet", relation="operated_by")
        G.add_edge("DragSail-Demo", "SpaceX", relation="operated_by")
        G.add_edge("Starlink-1000", "LEO", relation="orbits_in")
        G.add_edge("OneWeb-100", "LEO", relation="orbits_in")
        G.add_edge("Dove-50", "LEO", relation="orbits_in")
        G.add_edge("DragSail-Demo", "LEO", relation="orbits_in")
        return G

def query_by_regulator(G, regulator):
    regulated_orbits = [
        target for _, target, data in G.edges(regulator, data=True)
        if data.get("relation") == "regulates"
    ]
    licensed_operators = [
        source for source, target, data in G.edges(data=True)
        if target == regulator and data.get("relation") == "licensed_by"
    ]
    satellites = []
    for node, attrs in G.nodes(data=True):
        if attrs.get("type") != "satellite":
            continue
        op_edges = [
            t for _, t, d in G.edges(node, data=True)
            if d.get("relation") == "operated_by"
        ]
        orbit_edges = [
            t for _, t, d in G.edges(node, data=True)
            if d.get("relation") == "orbits_in"
        ]
        in_regulated_orbit = any(o in regulated_orbits for o in orbit_edges)
        by_licensed_op = any(o in licensed_operators for o in op_edges)
        if in_regulated_orbit and by_licensed_op:
            satellites.append(node)
    return satellites

def print_graph_summary(G):
    print("\n" + "=" * 55)
    print("  DEORBIT COMPLIANCE KNOWLEDGE GRAPH")
    print("=" * 55)
    node_types = {}
    for node, attrs in G.nodes(data=True):
        t = attrs.get("type", "unknown")
        node_types.setdefault(t, []).append(node)
    print(f"\n  Nodes: {G.number_of_nodes()}    "f"Edges:  {G.number_of_edges()}")
    for t, nodes in sorted(node_types.items()):
        print(f"    {t}:  {', '.join(nodes)}")
    print("\n  Relationships:")
    for src, tgt, data in G.edges(data=True):
        rel = data.get("relation", "?")
        print(f"    {src} --[{rel}]--> {tgt}")

if __name__ == "__main__":
    G = build_graph()
    print_graph_summary(G)
    fcc_sats = query_by_regulator(G, "FCC")
    print("\n  FCC 5-year rule applies to:")
    for sat in fcc_sats:
        attrs = G.nodes[sat]
        sail = "with drag sail" if attrs.get("has_drag_sail") else "no drag sail"
        print(f"    {sat} ({attrs['altitude_km']} km, {sail})")
    print("\n" + "=" * 55)