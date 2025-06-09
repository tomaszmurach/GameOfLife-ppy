#!/usr/bin/env python3
"""
game.py

Conway's Game of Life implementation with Pygame GUI.
"""

import os
import sys
from typing import Callable, List, Set
import numpy as np
import pygame


# -----------------------------------------------------------------------------
# Parameters and constants
# -----------------------------------------------------------------------------
CELL_SIZE = 15
GRID_W, GRID_H = 100, 80
WINDOW_W = GRID_W * CELL_SIZE + 220
WINDOW_H = GRID_H * CELL_SIZE + 40
FPS_LIMIT = 60

# Default rule‐presets shown w panelu
RULE_PRESETS = ["23/3", "234/34", "1357/1357", "245/368"]

# Kolory
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER = (150, 150, 150)
BUTTON_SELECTED = (0, 255, 0)
PANEL_BG = (40, 40, 40)


# -----------------------------------------------------------------------------
# GUI Button
# -----------------------------------------------------------------------------
class Button:
    """Simple clickable button in Pygame.

    Args:
        rect (pygame.Rect): rectangle definiujący pozycję i rozmiar.
        text (str): tekst wyświetlany na przycisku.
        callback (Callable[[], None]): funkcja wywoływana po kliknięciu.
    """

    def __init__(
            self,
            rect: pygame.Rect,
            text: str,
            callback: Callable[[], None],
            bg_color: tuple[int, int, int] = BUTTON_COLOR,
            hover_color: tuple[int, int, int] = BUTTON_HOVER,
    ) -> None:
        self.rect = rect
        self.text = text
        self.callback = callback
        self.hover = False
        self.selected = False
        self.bg_color = bg_color
        self.hover_color = hover_color


    def draw(self, surface: pygame.Surface) -> None:
        """Narysuj przycisk na podanej powierzchni."""
        # jeśli przycisk jest wybrany, używamy BUTTON_SELECTED
        if getattr(self, "selected", False):
             bg = BUTTON_SELECTED
        else:
             bg = self.hover_color if self.hover else self.bg_color
        pygame.draw.rect(surface, bg, self.rect)
        font = pygame.font.SysFont(None, 24)
        lbl = font.render(self.text, True, (255, 255, 255))
        pos = lbl.get_rect(center=self.rect.center)
        surface.blit(lbl, pos)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Obsługa zdarzeń myszy (hover + click).

        Args:
            event (pygame.event.Event): zdarzenie Pygame.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


# -----------------------------------------------------------------------------
# Model symulacji
# -----------------------------------------------------------------------------
class GameOfLifeModel:
    """Model symulacji Conway’s Game of Life.

    Args:
        w (int): szerokość siatki (liczba kolumn).
        h (int): wysokość siatki (liczba wierszy).
    """

    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h
        self.grid = np.zeros((h, w), dtype=np.uint8)
        self.survive: Set[int] = {2, 3}
        self.born: Set[int] = {3}
        self.generation = 0

    def tick(self) -> None:
        """Przejdź do następnej generacji wg aktualnych reguł."""
        # zlicz sąsiadów z owinięciem krawędzi (toroidalnie)
        ncount = sum(
            np.roll(np.roll(self.grid, dy, axis=0), dx, axis=1)
            for dy in (-1, 0, 1) for dx in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
        )
        # reguły przeżycia i narodzin
        surv = (self.grid == 1) & np.isin(ncount, list(self.survive))
        born = (self.grid == 0) & np.isin(ncount, list(self.born))

        self.grid[:] = 0
        self.grid[surv | born] = 1
        self.generation += 1

    def toggle_cell(self, x: int, y: int) -> None:
        """Przełącz stan pojedynczej komórki.

        Args:
            x (int): indeks kolumny.
            y (int): indeks wiersza.
        """
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y, x] ^= 1

    def reset(self) -> None:
        """Wyczyść siatkę i zresetuj licznik generacji."""
        self.grid.fill(0)
        self.generation = 0

    def set_rules(self, rule_str: str) -> None:
        """Ustaw nowe reguły \"survive/born\" i zresetuj symulację.

        Args:
            rule_str (str): ciąg w formacie 'S/B', np. '23/3'.
        """
        s, b = rule_str.split('/')
        self.survive = {int(c) for c in s}
        self.born = {int(c) for c in b}
        self.reset()


# -----------------------------------------------------------------------------
# Aplikacja Pygame
# -----------------------------------------------------------------------------
class GameApp:
    """Pygame GUI dla Conway’s Game of Life.

    Args:
        initial_pattern (Callable[[GameOfLifeModel], None], optional):
            funkcja nakładająca wstępny wzorzec na model.
        initial_rule_str (str, optional):
            reguły początkowe w formacie 'S/B'.
    """

    def __init__(
        self,
        initial_pattern: Callable[['GameOfLifeModel'], None] = None,
        initial_rule_str: str = None
    ) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Game of Life")
        self.clock = pygame.time.Clock()

        # model symulacji
        self.model = GameOfLifeModel(GRID_W, GRID_H)
        if initial_rule_str:
            self.model.set_rules(initial_rule_str)
        if initial_pattern:
            initial_pattern(self.model)

        # stan symulacji
        self.running = False
        self.speed = 10  # generacji na sekundę

        # przygotowanie GUI
        self.panel_rect = pygame.Rect(GRID_W * CELL_SIZE, 0,
                                      WINDOW_W - GRID_W * CELL_SIZE,
                                      WINDOW_H)
        self.buttons: List[Button] = []
        self.rule_buttons: List[Button] = []
        self._create_buttons()

    def _create_buttons(self) -> None:
        """Utwórz przyciski na panelu bocznym."""
        # Start / Pause
        self.buttons.append(Button(
            pygame.Rect(self.panel_rect.x + 10, 10, 180, 30),
            "PAUSE" if self.running else "START",
            self._toggle_run
        ))

        # Reset
        self.buttons.append(Button(
            pygame.Rect(self.panel_rect.x + 10, 50, 180, 30),
            "RESET",
            self.model.reset
        ))

        # + Speed / - Speed
        self.buttons.append(Button(
            pygame.Rect(self.panel_rect.x + 10, 90, 80, 30),
            "+ Speed",
            self._inc_speed
        ))
        self.buttons.append(Button(
            pygame.Rect(self.panel_rect.x + 110, 90, 80, 30),
            "- Speed",
            self._dec_speed
        ))

        # Rule presets
        y0 = 130
        for i, rule in enumerate(RULE_PRESETS):
            btn = Button(
                pygame.Rect(self.panel_rect.x + 10,
                            y0 + i * 40,
                            180, 30),
                rule,
                lambda r=rule: self._set_rule(r)
            )
            # zaznaczenie aktualnego
            if self.model.survive == set(map(int, rule.split('/')[0])):
                btn.selected = True
            self.buttons.append(btn)
            self.rule_buttons.append(btn)


        # Back to Menu
        back_rect = pygame.Rect(
            self.panel_rect.x + (self.panel_rect.w - 200),
            self.panel_rect.bottom - 100,
            180, 50
        )

        back_button = Button(
            back_rect,
            "Back to menu",
            self._back_to_menu,
            bg_color=(200, 0, 0),
            hover_color=(255, 50, 50)
        )
        self.buttons.append(back_button)

    def _toggle_run(self) -> None:
        """Start / pause symulacji."""
        self.running = not self.running
        # aktualizacja tekstu przycisku
        for btn in self.buttons:
            if btn.text in ("START", "PAUSE"):
                btn.text = "PAUSE" if self.running else "START"

    def _inc_speed(self) -> None:
        """Zwiększ prędkość (max 60)."""
        self.speed = min(60, self.speed + 1)

    def _dec_speed(self) -> None:
        """Zmniejsz prędkość (min 1)."""
        self.speed = max(1, self.speed - 1)

    def _set_rule(self, rule: str) -> None:
        """Zmień reguły symulacji.

        Args:
            rule (str): nowy ciąg 'S/B'.
        """
        self.model.set_rules(rule)
        for btn in self.rule_buttons:
            btn.selected = (btn.text == rule)

    def run(self) -> None:
        """Główna pętla aplikacji."""
        accumulator = 0.0
        while True:
            dt = self.clock.tick(FPS_LIMIT) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # klikanie w komórki (tylko gdy pauza)
                if (not self.running and
                    event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1 and
                    event.pos[0] < GRID_W * CELL_SIZE):
                    gx = event.pos[0] // CELL_SIZE
                    gy = event.pos[1] // CELL_SIZE
                    self.model.toggle_cell(gx, gy)
                for btn in self.buttons:
                    btn.handle_event(event)

            # update symulacji
            if self.running:
                accumulator += dt
                if accumulator >= 1.0 / self.speed:
                    self.model.tick()
                    accumulator = 0.0

            # rysowanie
            self._draw()

    def _draw(self) -> None:
        """Narysuj siatkę, przyciski i status."""
        self.screen.fill((0, 0, 0))
        # siatka
        for y in range(GRID_H):
            for x in range(GRID_W):
                r = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE - 1, CELL_SIZE - 1
                )
                if self.model.grid[y, x]:
                    pygame.draw.rect(self.screen, (200, 200, 200), r)
                else:
                    pygame.draw.rect(self.screen, (60, 60, 60), r, 1)

        # panel boczny
        pygame.draw.rect(self.screen, PANEL_BG, self.panel_rect)
        for btn in self.buttons:
            btn.draw(self.screen)

        # status
        font = pygame.font.SysFont(None, 24)
        st = f"Gen: {self.model.generation}   Spd: {self.speed}"
        txt = font.render(st, True, (200, 200, 200))
        self.screen.blit(txt, (self.panel_rect.x + 10,
                               self.panel_rect.bottom - 30))

        pygame.display.flip()

    def _back_to_menu(self) -> None:
        """Powrót do Main Menu. Odpalając skrypt od nowa."""
        pygame.quit()

        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import menu
        menu.main()
        sys.exit(0)


if __name__ == "__main__":
    app = GameApp()
    app.run()
    sys.exit()