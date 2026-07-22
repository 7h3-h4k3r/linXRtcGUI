try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from .userClass import UserList
class ConnectionIndicator(ctk.CTkFrame if USING_CTK else tk.Frame):
    """A small colored dot + label showing connection state (green/red/amber)."""

    def __init__(self, master, text="Disconnected", state="offline", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._state_colors = {
            "online": Theme.SUCCESS,
            "offline": Theme.ERROR,
            "connecting": Theme.WARNING,
        }

        if USING_CTK:
            self.dot = ctk.CTkLabel(self, text="●", text_color=self._state_colors.get(state, Theme.ERROR),
                                     font=(Theme.FONT_FAMILY, 14))
            self.dot.pack(side="left", padx=(0, 4))
            self.label = ctk.CTkLabel(self, text=text, text_color=Theme.TEXT_SECONDARY, font=Theme.FONT_SMALL)
            self.label.pack(side="left")
        else:
            self.dot = tk.Label(self, text="●", fg=self._state_colors.get(state, Theme.ERROR), bg=Theme.BG)
            self.dot.pack(side="left", padx=(0, 4))
            self.label = tk.Label(self, text=text, fg=Theme.TEXT_SECONDARY, bg=Theme.BG)
            self.label.pack(side="left")

    def set_state(self, state: str, text: str = None):
        """state: 'online' | 'offline' | 'connecting'"""
        color = self._state_colors.get(state, Theme.ERROR)
        if USING_CTK:
            self.dot.configure(text_color=color)
            if text is not None:
                self.label.configure(text=text)
        else:
            self.dot.configure(fg=color)
            if text is not None:
                self.label.configure(text=text)