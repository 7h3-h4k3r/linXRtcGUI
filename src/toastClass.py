
try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme

class Toast(ctk.CTkFrame if USING_CTK else tk.Frame):
   

    COLORS = {
        "info": Theme.INFO,
        "success": Theme.SUCCESS,
        "warning": Theme.WARNING,
        "error": Theme.ERROR,
    }

    def __init__(self, master, message: str, kind: str = "info", duration_ms: int = 3000):
        color = self.COLORS.get(kind, Theme.INFO)
        if USING_CTK:
            super().__init__(
                master,
                width=300,
                height=58,
                fg_color=Theme.CARD_LIGHT,
                corner_radius=10,
                border_width=0
            )

            self.pack_propagate(False)
            bar = ctk.CTkFrame(self, fg_color=color, width=6, corner_radius=0)
            bar.pack(side="left", fill="y")
            ctk.CTkLabel(self, text=message, text_color=Theme.TEXT_PRIMARY, font=Theme.FONT_SMALL,
                         wraplength=0, justify="left").pack(side="left", padx=10, pady=8)
        else:
            super().__init__(master, bg=Theme.CARD_LIGHT, highlightbackground=color, highlightthickness=1)
            tk.Label(self, text=message, fg=Theme.TEXT_PRIMARY, bg=Theme.CARD_LIGHT,
                     wraplength=0, justify="left").pack(padx=10, pady=8)

        self.place(
            relx=0.98,
            rely=0.96,
            anchor="se"
        )
        self.after(duration_ms, self._dismiss)

    def _dismiss(self):
        self.destroy()

