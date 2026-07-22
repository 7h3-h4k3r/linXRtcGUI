
try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from datetime import datetime
class MessageBubble(ctk.CTkFrame if USING_CTK else tk.Frame):
    """
    A single chat message bubble.

    kind: 'self' | 'other' | 'system' | 'warning' | 'error' | 'success'
    """

    KIND_COLORS = {
        "self": Theme.BUBBLE_SELF,
        "other": Theme.BUBBLE_OTHER,
        "system": Theme.BUBBLE_SYSTEM,
        "warning": Theme.WARNING,
        "error": Theme.ERROR,
        "success": Theme.SUCCESS,
    }

    def __init__(self, master, sender: str, text: str, timestamp: str = None,
                 kind: str = "other", **kwargs):
        color = self.KIND_COLORS.get(kind, Theme.BUBBLE_OTHER)
        timestamp = timestamp or datetime.now().strftime("%H:%M")
        text_color = "#FFFFFF" if kind in ("self", "warning", "error", "success") else Theme.TEXT_PRIMARY

        super().__init__(master, fg_color="transparent", **kwargs)

        anchor_side = "e" if kind == "self" else "w"
        inner_anchor = "e" if kind == "self" else "w"

        # CTkLabel renders at its wraplength width even for short text (it
        # isn't a "max width", it's closer to a fixed box width), so a flat
        # wraplength=340 made every bubble balloon out to ~340px wide even
        # for a one-word message. Instead, size the wrap width to the actual
        # message length (roughly 7px/char + padding), capped at a sensible
        # max/min so long messages still wrap and short ones stay compact.
        MAX_WRAP = 320
        MIN_WRAP = 50
        est_width = len(text) * 7 + 20
        wrap_len = max(MIN_WRAP, min(MAX_WRAP, est_width))

        # Own messages don't need a repeated "You" label above every bubble.
        show_header = kind not in ("system", "self")

        if USING_CTK:
            bubble = ctk.CTkFrame(self, fg_color=color, corner_radius=Theme.CORNER_RADIUS_SM)
            bubble.pack(anchor=inner_anchor, padx=10, pady=3)

            if show_header:
                header = ctk.CTkLabel(bubble, text=sender, font=Theme.FONT_SMALL,
                                       text_color=Theme.ACCENT)
                header.pack(anchor="w", padx=10, pady=(5, 0))

            body = ctk.CTkLabel(bubble, text=text, font=Theme.FONT_BODY, text_color=text_color,
                                 wraplength=wrap_len, justify="left")
            body.pack(anchor="w", padx=10, pady=(5 if not show_header else 0, 1))

            time_lbl = ctk.CTkLabel(bubble, text=timestamp, font=(Theme.FONT_FAMILY, 9),
                                     text_color="#DDDDDD" if kind == "self" else Theme.TEXT_MUTED)
            time_lbl.pack(anchor="e", padx=10, pady=(0, 5))
        else:
            bubble = tk.Frame(self, bg=color)
            bubble.pack(anchor=inner_anchor, padx=10, pady=3)
            if show_header:
                tk.Label(bubble, text=sender, fg=Theme.ACCENT, bg=color,
                         font=Theme.FONT_SMALL).pack(anchor="w", padx=10, pady=(5, 0))
            tk.Label(bubble, text=text, fg=text_color, bg=color, wraplength=wrap_len,
                     justify="left").pack(anchor="w", padx=10, pady=(5 if not show_header else 0, 1))
            tk.Label(bubble, text=timestamp, fg=Theme.TEXT_MUTED, bg=color,
                     font=(Theme.FONT_FAMILY, 9)).pack(anchor="e", padx=10, pady=(0, 6))