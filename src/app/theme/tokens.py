"""Design tokens for Smart Vacuum desktop UI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeTokens:
    name: str
    bg: str
    surface: str
    surface_alt: str
    border: str
    text: str
    text_muted: str
    primary: str
    primary_hover: str
    primary_pressed: str
    on_primary: str
    success: str
    warning: str
    danger: str
    info: str
    focus_ring: str
    sidebar_bg: str
    sidebar_text: str
    sidebar_active: str


LIGHT = ThemeTokens(
    name="light",
    bg="#F4F6FA",
    surface="#FFFFFF",
    surface_alt="#EEF2F7",
    border="#CBD5E1",
    text="#0F172A",
    text_muted="#475569",
    primary="#0E7490",
    primary_hover="#155E75",
    primary_pressed="#164E63",
    on_primary="#FFFFFF",
    success="#15803D",
    warning="#B45309",
    danger="#B91C1C",
    info="#1D4ED8",
    focus_ring="#0E7490",
    sidebar_bg="#0F172A",
    sidebar_text="#E2E8F0",
    sidebar_active="#1E3A5F",
)

DARK = ThemeTokens(
    name="dark",
    bg="#0B1220",
    surface="#111A2E",
    surface_alt="#16213A",
    border="#2B3A55",
    text="#E6EBF5",
    text_muted="#9FB0CB",
    primary="#38BDF8",
    primary_hover="#7DD3FC",
    primary_pressed="#0EA5E9",
    on_primary="#06202E",
    success="#3DDC84",
    warning="#F59E0B",
    danger="#F87171",
    info="#60A5FA",
    focus_ring="#7DD3FC",
    sidebar_bg="#070D18",
    sidebar_text="#E2E8F0",
    sidebar_active="#12304F",
)

TOKENS = {
    "light": LIGHT,
    "dark": DARK,
}

FONT_FAMILY = '"DejaVu Sans", "Segoe UI Variable", "Segoe UI", sans-serif'
TYPE_SCALE = {
    "caption": 12,
    "body": 14,
    "label_strong": 16,
    "section_title": 20,
    "page_title": 28,
}
SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "xxl": 32}
RADII = {"sm": 6, "md": 10, "lg": 14}
ICON_SIZES = {"sm": 16, "md": 20, "lg": 24}
ANIMATION_MS = 150
