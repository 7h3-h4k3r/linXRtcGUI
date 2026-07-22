try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from .emptyClass import EmptyState

class UserList(ctk.CTkScrollableFrame if USING_CTK else tk.Frame):
    """Scrollable list of users (online users or recent chats)."""

    def __init__(self, master, on_user_selected=None, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color="transparent", **kwargs)
        else:
            super().__init__(master, bg=Theme.CARD, **kwargs)

        self.on_user_selected = on_user_selected or (lambda user: None)
        self._rows = []

    def clear(self):
        for row in self._rows:
            row.destroy()
        self._rows.clear()

    def populate(self, users):
        """users: list of dicts -> {"name": str, "status": "online"|"away"|"offline", "last_message": str}"""
        self.clear()
        if not users:
            empty = EmptyState(self, icon="👥", title="No users found",
                                subtitle="Try a different search term.")
            empty.pack(fill="both", expand=True)
            self._rows.append(empty)
            return

        for user in users:
            row = self._build_row(user)
            row.pack(fill="x", pady=2, padx=2)
            self._rows.append(row)

    def _build_row(self, user):
        status_color = {"online": Theme.ONLINE, "away": Theme.AWAY, "offline": Theme.OFFLINE}.get(
            user.get("status", "offline"), Theme.OFFLINE)

        if USING_CTK:
            row = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=Theme.CORNER_RADIUS_SM, height=52)
            row.pack_propagate(False)

            avatar = ctk.CTkLabel(row, text=user["name"][0].upper(), width=34, height=34,
                                   fg_color=Theme.ACCENT, corner_radius=17, font=Theme.FONT_BOLD)
            avatar.pack(side="left", padx=8, pady=8)

            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=6)
            ctk.CTkLabel(text_frame, text=user["name"], font=Theme.FONT_BOLD,
                         text_color=Theme.TEXT_PRIMARY, anchor="w").pack(fill="x")
            ctk.CTkLabel(text_frame, text=user.get("last_message", "No messages yet"),
                         font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED, anchor="w").pack(fill="x")

            dot = ctk.CTkLabel(row, text="●", text_color=status_color, font=(Theme.FONT_FAMILY, 12))
            dot.pack(side="right", padx=10)

            for widget in (row, avatar, text_frame, dot):
                widget.bind("<Double-Button-1>", lambda e, u=user: self.on_user_selected(u))
                widget.bind("<Enter>", lambda e, r=row: r.configure(fg_color=Theme.CARD_LIGHT))
                widget.bind("<Leave>", lambda e, r=row: r.configure(fg_color=Theme.CARD))
        else:
            row = tk.Frame(self, bg=Theme.CARD, height=52)
            row.pack_propagate(False)
            tk.Label(row, text=user["name"][0].upper(), bg=Theme.ACCENT, fg="white",
                     width=3).pack(side="left", padx=8, pady=8)
            text_frame = tk.Frame(row, bg=Theme.CARD)
            text_frame.pack(side="left", fill="both", expand=True)
            tk.Label(text_frame, text=user["name"], fg=Theme.TEXT_PRIMARY, bg=Theme.CARD,
                     anchor="w").pack(fill="x")
            tk.Label(text_frame, text=user.get("last_message", "No messages yet"),
                     fg=Theme.TEXT_MUTED, bg=Theme.CARD, anchor="w").pack(fill="x")
            tk.Label(row, text="●", fg=status_color, bg=Theme.CARD).pack(side="right", padx=10)
            row.bind("<Double-Button-1>", lambda e, u=user: self.on_user_selected(u))

        return row