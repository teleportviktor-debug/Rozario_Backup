"""
Registry for Genome Architecture (Phase 1).
Maintains registered mutations, component templates, and UI schemas.
"""
from typing import Dict, Any, Callable

COMPONENT_REGISTRY: Dict[str, Any] = {}
MUTATION_REGISTRY: Dict[str, Any] = {}

def register_component(name: str):
    def decorator(fn: Callable):
        COMPONENT_REGISTRY[name] = fn
        return fn
    return decorator

def register_mutation(name: str):
    def decorator(fn: Callable):
        MUTATION_REGISTRY[name] = fn
        return fn
    return decorator
