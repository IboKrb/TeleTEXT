# systems/assets.py
import os
import pygame
from typing import Dict, Tuple, Optional, List

from systems import config

def scale_to_fit(surface: pygame.Surface, target: Tuple[int, int]) -> pygame.Surface:
    tw, th = target
    sw, sh = surface.get_width(), surface.get_height()
    if sw == 0 or sh == 0:
        return pygame.transform.smoothscale(surface, target)
    scale = min(tw / sw, th / sh)
    return pygame.transform.smoothscale(surface, (max(1, int(sw*scale)), max(1, int(sh*scale))))

def scale_surface_to_height(img: pygame.Surface, target_h: int) -> pygame.Surface:
    w, h = img.get_width(), img.get_height()
    if h <= 0:
        return img
    s = target_h / h
    return pygame.transform.smoothscale(img, (max(1, int(w*s)), target_h))

def find_happy_portrait_paths() -> List[str]:
    exts = (".png", ".jpg", ".jpeg", ".webp")
    paths = []
    people_dir = config.PEOPLE_DIR
    if not os.path.isdir(people_dir):
        return []
    for dirpath, _, filenames in os.walk(people_dir):
        for fn in filenames:
            lo = fn.lower()
            if "happy" in lo and lo.endswith(exts):
                paths.append(os.path.join(dirpath, fn))
    # je Personenordner nur eines
    first_by_person = {}
    for p in paths:
        person_folder = os.path.basename(os.path.dirname(p))
        first_by_person.setdefault(person_folder, p)
    return list(first_by_person.values())

class Assets:
    def __init__(self, logger=None):
        self.logger = logger or (lambda *_: None)
        self.room_bg_cache: Dict[str, pygame.Surface] = {}
        self.happy_images: List[pygame.Surface] = []

    def preload_rooms(self, raeume: Dict[str, object], size: Tuple[int, int], fallback_color=(25,35,60), fallback_title_surf=None):
        """Lädt alle Raumhintergründe vor und cached sie nach 'Raum.name'."""
        self.room_bg_cache.clear()
        for raum in raeume.values():
            filename = f"{raum.name.lower().replace(' ', '_')}.png"
            path = os.path.join(config.ROOMS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    img = pygame.transform.smoothscale(img, size)
                    self.room_bg_cache[raum.name] = img
                    continue
                except Exception as e:
                    self.logger(f"[Assets] Defektes Room-Image {filename}: {e}")
            # Fallback
            surf = pygame.Surface(size)
            surf.fill(fallback_color)
            if fallback_title_surf:
                title = fallback_title_surf
                rect = title.get_rect(center=(size[0]//2, 30))
                surf.blit(title, rect)
            self.room_bg_cache[raum.name] = surf

    def get_room_bg(self, raum_name: str) -> Optional[pygame.Surface]:
        return self.room_bg_cache.get(raum_name)

    def load_happy_images(self, max_height: int):
        imgs = []
        for path in find_happy_portrait_paths():
            try:
                img = pygame.image.load(path).convert_alpha()
                imgs.append(scale_surface_to_height(img, max_height))
            except Exception as e:
                self.logger(f"[Assets] Happy load fail {os.path.basename(path)}: {e}")
        self.happy_images = imgs

    def load_person_portrait(self, person_name: str, target_size: Tuple[int, int]) -> Optional[pygame.Surface]:
        basefile = person_name[:1].lower() + person_name[1:] + "Neutral"
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            path = os.path.join(config.PEOPLE_DIR, person_name, basefile + ext)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    return scale_to_fit(img, target_size)
                except Exception as e:
                    self.logger(f"[Assets] Portrait fail {os.path.basename(path)}: {e}")
        return None
