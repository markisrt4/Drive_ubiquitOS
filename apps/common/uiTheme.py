FONT_FAMILY = "DejaVu Sans"

COLORS = {
    "app_bg":         "#111418",
    "top_bar_bg":     "#dfe7eb",
    "top_bar_fg":     "#1d2429",
    "top_bar_active": "#cfd9de",
    "status_bg":      "#0b0d10",
    "status_fg":      "#b8c7d3",

    "status_label":           "#9aa4b2",
    "status_primary_value":   "#1f7cff",
    "status_telemetry_value": "#48d11f",

    "tile_bg":       "#20252b",
    "tile_border":   "#384653",
    "tile_accent":   "#0d6fd8",
    "tile_title":    "#ffffff",
    "tile_subtitle": "#b8c7d3",
    "tile_detail":   "#7f8d99",

    "volume_button_bg":          "#20252b",
    "volume_button_fg":          "#ffffff",
    "volume_indicator_active":   "#0d6fd8",
    "volume_indicator_inactive": "#6f7a86",

    "power_bg":     "#c62828",
    "power_active": "#a91f1f",
    "power_fg":     "#ffffff",
}

FONTS = {
    "title":         (FONT_FAMILY, 20, "bold"),
    "back":          (FONT_FAMILY, 16, "bold"),
    "power":         (FONT_FAMILY, 22, "bold"),
    "status":        (FONT_FAMILY, 12),
    "tile_title":    (FONT_FAMILY, 26, "bold"),
    "tile_subtitle": (FONT_FAMILY, 15),
    "tile_detail":   (FONT_FAMILY, 12),
    "volume_button": (FONT_FAMILY, 16, "bold"),
}

MENU_TILE_STYLE = {
    "compact": {
        "main_title_font": (FONT_FAMILY, 19, "bold"),
        "preset_title_font": (FONT_FAMILY, 18, "bold"),
        "default_title_font": (FONT_FAMILY, 17, "bold"),
        "subtitle_font": (FONT_FAMILY, 10),
        "detail_font": (FONT_FAMILY, 9),
        "body_padx": 12,
        "body_pady": 8,
        "accent_height": 4,
        "title_wrap": 180,
        "text_wrap": 220,
        "tile_padx": 6,
        "tile_pady": 6,
    },
    "normal": {
        "main_title_font": FONTS["tile_title"],
        "preset_title_font": FONTS["tile_title"],
        "default_title_font": FONTS["tile_title"],
        "subtitle_font": FONTS["tile_subtitle"],
        "detail_font": FONTS["tile_detail"],
        "body_padx": 22,
        "body_pady": 18,
        "accent_height": 5,
        "title_wrap": 260,
        "text_wrap": 300,
        "tile_padx": 10,
        "tile_pady": 10,
    },
}