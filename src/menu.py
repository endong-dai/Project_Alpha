"""
menu.py
Simple right-side menu UI.
"""

import pygame


class MenuButton:
    def __init__(self, key, label, rect, enabled=True):
        self.key = key
        self.label = label
        self.rect = pygame.Rect(rect)
        self.enabled = enabled

    def draw(self, screen, font, colors):
        fill = colors["button"] if self.enabled else colors["button_disabled"]
        text_color = colors["text"] if self.enabled else colors["text_disabled"]
        pygame.draw.rect(screen, fill, self.rect, border_radius=6)
        pygame.draw.rect(screen, colors["border"], self.rect, 2, border_radius=6)
        label = font.render(self.label, True, text_color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def contains(self, position):
        return self.enabled and self.rect.collidepoint(position)


class VerticalMenu:
    def __init__(self, x, y, width, button_height=42, gap=10):
        self.x = x
        self.y = y
        self.width = width
        self.button_height = button_height
        self.gap = gap
        self.buttons = []

    def set_options(self, options):
        self.buttons = []
        top = self.y
        for option in options:
            rect = pygame.Rect(self.x, top, self.width, self.button_height)
            self.buttons.append(
                MenuButton(
                    option["key"],
                    option["label"],
                    rect,
                    option.get("enabled", True),
                )
            )
            top += self.button_height + self.gap

    def draw(self, screen, font, colors):
        for button in self.buttons:
            button.draw(screen, font, colors)

    def get_clicked(self, position):
        for button in self.buttons:
            if button.contains(position):
                return button.key
        return None
