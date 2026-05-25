import networkx as nx

def build_concept_graph() -> nx.DiGraph:
    """
    Builds a directed graph representing the prerequisite relationship between concepts.
    
    Returns:
        nx.DiGraph: Directed graph of concept prerequisites.
    """
    graph = nx.DiGraph()
    
    # Add prerequisite edges (u -> v means u is a prerequisite for v)
    edges = [
        ("Basic Arithmetic", "Pre-Algebra"),
        ("Pre-Algebra", "Basic Algebra"),
        ("Basic Algebra", "Factoring Polynomials"),
        ("Factoring Polynomials", "Solving Quadratic Equations"),
        ("Basic Algebra", "Graphing Linear Equations"),
    ]
    graph.add_edges_from(edges)
    return graph

def check_prerequisites(graph: nx.DiGraph, target_concept: str, mastered_concepts: list) -> list:
    """
    Finds all immediate prerequisites of target_concept that are missing from mastered_concepts.
    
    Args:
        graph (nx.DiGraph): The concept graph.
        target_concept (str): The concept the student wants to learn.
        mastered_concepts (list): The list of concepts the student has already mastered.
        
    Returns:
        list: Required concepts that are missing from the student's mastery.
    """
    if not graph.has_node(target_concept):
        return []
    
    prereqs = list(graph.predecessors(target_concept))
    missing = [concept for concept in prereqs if concept not in mastered_concepts]
    return missing

def get_next_steps(graph: nx.DiGraph, current_concept: str, top_n: int = 2) -> list:
    """
    Returns the immediate successors of current_concept to recommend what to study next.
    
    Args:
        graph (nx.DiGraph): The concept graph.
        current_concept (str): The concept currently being studied.
        top_n (int): The maximum number of recommendations to return.
        
    Returns:
        list: Recommended next concepts to study.
    """
    if not graph.has_node(current_concept):
        return []
    
    successors = list(graph.successors(current_concept))
    return successors[:top_n]

if __name__ == "__main__":
    # Initialize the graph
    concept_graph = build_concept_graph()
    
    # Test 1: Check prerequisites for "Solving Quadratic Equations"
    target = "Solving Quadratic Equations"
    mastered = ["Basic Arithmetic", "Pre-Algebra", "Basic Algebra"]
    missing = check_prerequisites(concept_graph, target, mastered)
    
    print(f"Target Concept: {target}")
    print(f"Mastered Concepts: {mastered}")
    print(f"Missing Prerequisites: {missing}")
    
    # Test 2: Get next steps for "Basic Algebra"
    current = "Basic Algebra"
    next_steps = get_next_steps(concept_graph, current)
    print(f"\nCurrent Concept: {current}")
    print(f"Recommended Next Steps: {next_steps}")
