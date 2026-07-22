
try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme

class EmptyState(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Placeholder shown when a list/panel has no content yet (e.g. no chats)."""

    def __init__(self, master, icon="💬", title="No conversations yet",
                 subtitle="Start a new chat to see it here.", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        if USING_CTK:
            ctk.CTkLabel(self, text=icon, font=(Theme.FONT_FAMILY, 36)).pack(pady=(30, 6))
            ctk.CTkLabel(self, text=title, font=Theme.FONT_BOLD,
                         text_color=Theme.TEXT_PRIMARY).pack()
            ctk.CTkLabel(self, text=subtitle, font=Theme.FONT_SMALL,
                         text_color=Theme.TEXT_MUTED, wraplength=200,
                         justify="center").pack(pady=(4, 30))
        else:
            tk.Label(self, text=icon, font=(Theme.FONT_FAMILY, 36), bg=Theme.BG).pack(pady=(30, 6))
            tk.Label(self, text=title, fg=Theme.TEXT_PRIMARY, bg=Theme.BG).pack()
            tk.Label(self, text=subtitle, fg=Theme.TEXT_MUTED, bg=Theme.BG,
                     wraplength=200, justify="center").pack(pady=(4, 30))