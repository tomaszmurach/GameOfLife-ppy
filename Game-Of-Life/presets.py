"""
presets.py

Predefined patterns for Conway's Game of Life.
"""

from typing import List, Tuple
from game import GameOfLifeModel


def _apply_coords(
    model: GameOfLifeModel,
    coords: List[Tuple[int, int]],
    width: int,
    height: int
) -> None:
    """Helper: wyczyść siatkę i nanieś liste współrzędnych.

    Args:
        model (GameOfLifeModel): obiekt symulacji.
        coords (List[Tuple[int,int]]): punkty (x,y) żywych komórek.
        width (int): szerokość wzorca.
        height (int): wysokość wzorca.
    """
    model.reset()
    ox = (model.w - width) // 2
    oy = (model.h - height) // 2
    for x, y in coords:
        model.grid[oy + y, ox + x] = 1


def beacon(model: GameOfLifeModel) -> None:
    """Beacon (oscylator okresu 2)."""
    coords = [
        (0, 0), (1, 0), (0, 1), (1, 1),
        (2, 2), (3, 2), (2, 3), (3, 3)
    ]
    _apply_coords(model, coords, width=4, height=4)


def glider(model: GameOfLifeModel) -> None:
    """Glider – poruszający się wzorzec."""
    coords = [
        (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
    ]
    _apply_coords(model, coords, width=3, height=3)


def pulsar(model: GameOfLifeModel) -> None:
    """Pulsar – oscylator okresu 3."""
    coords = [
        # górna część
        (2,0),(3,0),(4,0),(8,0),(9,0),(10,0),
        (0,2),(5,2),(7,2),(12,2),
        (0,3),(5,3),(7,3),(12,3),
        (0,4),(5,4),(7,4),(12,4),
        (2,5),(3,5),(4,5),(8,5),(9,5),(10,5),
        # dolna część (lustrzane odbicie)
        (2,7),(3,7),(4,7),(8,7),(9,7),(10,7),
        (0,8),(5,8),(7,8),(12,8),
        (0,9),(5,9),(7,9),(12,9),
        (0,10),(5,10),(7,10),(12,10),
        (2,12),(3,12),(4,12),(8,12),(9,12),(10,12)
    ]
    _apply_coords(model, coords, width=13, height=13)


def pentadecathlon(model: GameOfLifeModel) -> None:
    """Pentadecathlon – oscylator okresu 15 (początkowo rząd 10)."""
    coords = [(i, 0) for i in range(10)]
    _apply_coords(model, coords, width=10, height=1)


def gosper_glider_gun(model: GameOfLifeModel) -> None:
    """Gosper Glider Gun."""
    coords = [
        (1,5),(1,6),(2,5),(2,6),
        (11,5),(11,6),(11,7),(12,4),(12,8),(13,3),(13,9),(14,3),(14,9),(15,6),(16,4),(16,8),(17,5),(17,6),(17,7),(18,6),
        (21,3),(21,4),(21,5),(22,3),(22,4),(22,5),(23,2),(23,6),(25,1),(25,2),(25,6),(25,7),
        (35,3),(35,4),(36,3),(36,4)
    ]
    _apply_coords(model, coords, width=37, height=10)
