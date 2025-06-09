#!/usr/bin/env python3
"""
menu.py

Main menu for Conway's Game of Life application.
"""

import sys
import pygame

from game import GameApp
import presets


# -----------------------------------------------------------------------------
# GUI Button (analogiczny do tego w game.py)
# -----------------------------------------------------------------------------
class MenuButton:
    """Przycisk w menu głównym."""

    def __init__(self, rect, text, callback):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, surf):
        color = (200, 200, 200) if self.hover else (100, 100, 100)
        pygame.draw.rect(surf, color, self.rect)
        font = pygame.font.SysFont(None, 30)
        lbl = font.render(self.text, True, (0,0,0))
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()


# -----------------------------------------------------------------------------
# Funkcje wywoływane przez menu
# -----------------------------------------------------------------------------
def run_clean_game():
    """Start gry bez żadnego presetu."""
    pygame.quit()
    GameApp().run()


def run_preset(pattern_func):
    """Start gry z wybranym presetem."""
    pygame.quit()
    GameApp(initial_pattern=pattern_func).run()


def show_instructions():
    """Wyświetl zasady gry w nowym okienku."""

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Instructions")
    font = pygame.font.SysFont(None, 24)
    lines = [
        "Conway's Game of Life – Rules and Controls:",
        "",
        "23/3 Rules:",
        "1. Any live cell with two or three live neighbours survives.",
        "2. Any dead cell with three live neighbours becomes a live cell.",
        "3. All other live cells die in the next generation.",
        "4. All other dead cells stay dead.",
        "",
        "Controls:",
        "- Click on the grid to toggle cells (while paused).",
        "- Start/Pause: run or pause the simulation.",
        "- Reset: clear the grid.",
        "- + Speed / - Speed: adjust simulation speed.",
        "- Rule Presets: choose different survival/birth rules from the side panel.",
        "- Back to Menu: return to the main menu.",
        "",
        "Press any key or click to return."
    ]

    while True:
        for ev in pygame.event.get():
            if ev.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                # just restore caption and go back
                pygame.display.set_mode((400, 400))
                pygame.display.set_caption("Game of Life – Main Menu")
                return

        screen.fill((50, 50, 50))
        for i, line in enumerate(lines):
            txt = font.render(line, True, (230, 230, 230))
            screen.blit(txt, (20, 20 + i * 30))
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def presets_menu():
    """Wyswietl użytkownikowi presety do wyboru wraz z opcją cofnięcia się do menu."""
    screen = pygame.display.get_surface()
    pygame.display.set_caption("Select a Preset")
    clock = pygame.time.Clock()

    patterns = [
        ("Beacon", presets.beacon),
        ("Glider", presets.glider),
        ("Pulsar", presets.pulsar),
        ("Pentadecathlon", presets.pentadecathlon),
        ("Gosper Gun", presets.gosper_glider_gun),
        ("Back", None)
    ]

    btns = []
    for i, (name, func) in enumerate(patterns):
        rect = pygame.Rect(100, 30 + i*60, 200, 50)
        if func is None:
            callback = lambda: None
        else:
            callback = lambda f=func: run_preset(f)
        btns.append(MenuButton(rect, name, callback))

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for b in btns:
                b.handle(ev)

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if btns[-1].rect.collidepoint(ev.pos):
                    pygame.display.set_caption("Game of Life – Main Menu")
                    return

        screen.fill((20, 20, 60))
        for b in btns:
            b.draw(screen)
        pygame.display.flip()
        clock.tick(30)



def main():
    """Główna pętla menu"""
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Game of Life – Main Menu")
    clock = pygame.time.Clock()

    btns = [
        MenuButton(pygame.Rect(100,  60, 200, 50),  "Start",       run_clean_game),
        MenuButton(pygame.Rect(100, 130, 200, 50),  "Presets",     presets_menu),
        MenuButton(pygame.Rect(100, 200, 200, 50),  "Instructions", show_instructions),
        MenuButton(pygame.Rect(100, 270, 200, 50),  "Exit",        lambda: sys.exit())
    ]

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for b in btns:
                b.handle(ev)

        screen.fill((30, 30, 30))
        for b in btns:
            b.draw(screen)
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
