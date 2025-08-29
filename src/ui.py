# ui.py
import pygame
from typing import Optional, List, Tuple

# Achtung: stelle sicher, dass pygame.init() + pygame.font.init()
# im Hauptprogramm *vor* dem Import von ui.py aufgerufen werden.

# Standard-Farben
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
GRAY       = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
MAGENTA    = (225, 0, 117)
DARK_BLUE = (25, 35, 60)
ACCENT    = (240, 240, 120)

# Standard-Fonts
FONT       = pygame.font.SysFont("arial", 20)
FONT_SMALL = pygame.font.SysFont("arial", 16)
FONT_BIG   = pygame.font.SysFont("arial", 28)

class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback,
                 tooltip: Optional[str] = None,
                 font: Optional[pygame.font.Font] = None):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.tooltip = tooltip
        self.hover = False
        self.font = font or FONT

    def draw(self, surface: pygame.Surface):
        color = LIGHT_GRAY if self.hover else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        text_surf = self.font.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and callable(self.callback):
                self.callback()

class Panel:
    def __init__(self, rect: pygame.Rect, title: str = ""):
        self.rect = rect
        self.title = title

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (235, 235, 240), self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        if self.title:
            title_surf = FONT_BIG.render(self.title, True, BLACK)
            surface.blit(title_surf, (self.rect.x + 12, self.rect.y + 8))

    def content_rect(self, pad: int = 12) -> pygame.Rect:
        title_h = (FONT_BIG.get_height() + 12) if self.title else 0
        return pygame.Rect(
            self.rect.x + pad,
            self.rect.y + pad + title_h,
            self.rect.width - 2*pad,
            self.rect.height - 2*pad - title_h
        )

class Slider:
    def __init__(self, rect: pygame.Rect, min_val=0, max_val=10, value=5, on_change=None):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = int(value)
        self.on_change = on_change
        self.dragging = False
        self.pad = 12  # Innenabstand für die Schiene

    def _val_to_x(self):
        track_w = self.rect.width - 2 * self.pad
        ratio = (self.value - self.min_val) / max(1, (self.max_val - self.min_val))
        return int(self.rect.x + self.pad + ratio * track_w)

    def _x_to_val(self, x):
        track_w = self.rect.width - 2 * self.pad
        ratio = (x - (self.rect.x + self.pad)) / max(1, track_w)
        v = self.min_val + ratio * (self.max_val - self.min_val)
        return int(round(max(self.min_val, min(self.max_val, v))))

    def set_value(self, v):
        v = int(max(self.min_val, min(self.max_val, v)))
        if v != self.value:
            self.value = v
            if callable(self.on_change):
                self.on_change(self.value)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_value(self._x_to_val(event.pos[0]))
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_value(self._x_to_val(event.pos[0]))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (245, 245, 245), self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        y = self.rect.centery
        x1 = self.rect.x + self.pad
        x2 = self.rect.right - self.pad
        pygame.draw.line(surface, GRAY, (x1, y), (x2, y), 4)

        knob_x = self._val_to_x()
        knob_rect = pygame.Rect(0, 0, 18, 26)
        knob_rect.center = (knob_x, y)
        pygame.draw.rect(surface, LIGHT_GRAY, knob_rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, knob_rect, 2, border_radius=6)

        val_surf = FONT_SMALL.render(str(self.value), True, BLACK)
        surface.blit(val_surf, (self.rect.right + 8, self.rect.centery - val_surf.get_height() // 2))

class TextLog:
    def __init__(self, rect: pygame.Rect, max_lines: int = 10,
                 title: str = "Log",
                 bg_color: Tuple[int,int,int] = (245, 245, 250),
                 border_color: Tuple[int,int,int] = (0, 0, 0),
                 border_width: int = 2,
                 radius: int = 12,
                 text_color: Tuple[int,int,int] = (0, 0, 0),
                 pad: int = 10,
                 title_color: Tuple[int,int,int] = (0, 0, 0)):
        self.rect = rect
        self.lines: List[str] = []
        self.max_lines = max_lines
        self.scroll_offset = 0
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.radius = radius
        self.text_color = text_color
        self.pad = pad
        self.title_color = title_color

    def add(self, line: str):
        max_chars = 80
        while len(line) > max_chars:
            self.lines.append(line[:max_chars])
            line = line[max_chars:]
        self.lines.append(line)
        if len(self.lines) > 1000:
            self.lines = self.lines[-1000:]
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y
            self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.lines) - self.max_lines)))

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=self.radius)

        x = self.rect.x + self.pad
        y = self.rect.y + self.pad

        if self.title:
            title_surf = FONT_SMALL.render(self.title, True, self.title_color)
            surface.blit(title_surf, (x, y))
            y += title_surf.get_height() + 6

        start = max(0, len(self.lines) - self.max_lines - self.scroll_offset)
        end = start + self.max_lines
        visible = self.lines[start:end]

        for line in visible:
            ts = FONT_SMALL.render(line, True, self.text_color)
            surface.blit(ts, (x, y))
            y += ts.get_height() + 4
