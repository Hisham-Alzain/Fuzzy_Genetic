"""Reusable flat pygame widgets (drawn in code, no image assets)."""

import pygame

from delivery_ga.ui.theme import ACCENT, BORDER, CARD, MUT, TXT


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Button:
    """Flat button. style 'primary' (accent fill) or 'secondary' (outline).

    Legacy style names 'green'/'red' map to primary/secondary.
    """

    def __init__(self, x, y, w, h, text, style="primary"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.style = {"green": "primary", "red": "secondary"}.get(style, style)
        self.hovered = False

    def set_rect(self, x, y, w=None, h=None):
        self.rect.x = int(x)
        self.rect.y = int(y)
        if w is not None:
            self.rect.w = int(w)
        if h is not None:
            self.rect.h = int(h)

    def draw(self, screen, font):
        radius = 10
        if self.style == "primary":
            fill = _lerp(ACCENT, (0, 0, 0), 0.12) if self.hovered else ACCENT
            pygame.draw.rect(screen, fill, self.rect, border_radius=radius)
            text_col = (255, 255, 255)
        else:
            fill = (245, 247, 250) if self.hovered else CARD
            pygame.draw.rect(screen, fill, self.rect, border_radius=radius)
            pygame.draw.rect(screen, BORDER, self.rect, width=1, border_radius=radius)
            text_col = TXT
        label = font.render(self.text, True, text_col)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False


class Slider:
    """Flat slider: light track, accent fill, white knob with accent ring."""

    def __init__(self, x, y, w, h, min_val, max_val, val, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = val
        self.label = label
        self.dragging = False

    def set_rect(self, x, y, w=None, h=None):
        self.rect.x = int(x)
        self.rect.y = int(y)
        if w is not None:
            self.rect.w = int(w)
        if h is not None:
            self.rect.h = int(h)

    def handle_event(self, event):
        hit = self.rect.inflate(0, 22)  # generous vertical grab zone
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and hit.collidepoint(event.pos):
                self.dragging = True
                self._update_val(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_val(event.pos[0])
            return True
        return False

    def _update_val(self, mouse_x):
        fraction = max(0.0, min(1.0, (mouse_x - self.rect.x) / self.rect.width))
        self.val = self.min_val + fraction * (self.max_val - self.min_val)

    def draw(self, screen, font, label_font=None, value_text=None, show_bounds=True):
        label_font = label_font or font
        if value_text is None:
            value_text = (
                f"{self.val:.3f}" if self.max_val <= 1.0 else str(int(self.val))
            )

        # Label (upper-left) and value (upper-right) sit clearly above the track.
        label = label_font.render(self.label.upper(), True, MUT)
        value = font.render(value_text, True, TXT)
        screen.blit(label, (self.rect.x, self.rect.y - 26))
        screen.blit(value, value.get_rect(topright=(self.rect.right, self.rect.y - 27)))

        track_h = max(6, self.rect.height)
        track = pygame.Rect(self.rect.x, self.rect.centery - track_h // 2, self.rect.width, track_h)
        pygame.draw.rect(screen, BORDER, track, border_radius=track_h // 2)

        fraction = (self.val - self.min_val) / max(1e-9, (self.max_val - self.min_val))
        fill_w = max(track_h, int(self.rect.width * fraction))
        fill = pygame.Rect(track.x, track.y, fill_w, track_h)
        pygame.draw.rect(screen, ACCENT, fill, border_radius=track_h // 2)

        knob_x = self.rect.x + int(self.rect.width * fraction)
        knob_r = track_h + 4
        pygame.draw.circle(screen, CARD, (knob_x, self.rect.centery), knob_r)
        pygame.draw.circle(screen, ACCENT, (knob_x, self.rect.centery), knob_r, width=3)
