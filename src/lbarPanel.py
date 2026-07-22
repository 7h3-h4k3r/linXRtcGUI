try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from .connInte import ConnectionIndicator
from .userClass import UserList
class Sidebar(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Left sidebar: profile, search, online users / recent chats, settings/logout."""

    def __init__(self, master, app, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.CARD, corner_radius=0, width=270, **kwargs)
        else:
            super().__init__(master, bg=Theme.CARD, width=270, **kwargs)
        self.pack_propagate(False)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        # --- profile header ---------------------------------------------
        if USING_CTK:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=16, pady=(20, 10))

            self.avatar = ctk.CTkLabel(header, text="U", width=48, height=48, fg_color=Theme.ACCENT,
                                        corner_radius=24, font=Theme.FONT_TITLE)
            self.avatar.pack(side="left")

            info = ctk.CTkFrame(header, fg_color="transparent")
            info.pack(side="left", padx=10)
            self.username_label = ctk.CTkLabel(info, text="Username", font=Theme.FONT_BOLD,
                                                text_color=Theme.TEXT_PRIMARY, anchor="w")
            self.username_label.pack(fill="x")
            self.status_indicator = ConnectionIndicator(info, text="Online", state="online")
            self.status_indicator.pack(anchor="w")

            # --- footer buttons ---------------------------------------------
            # NOTE: packed BEFORE the expanding lists below (with side="bottom")
            # so it reserves its space first. Tkinter's packer allocates space
            # in the order widgets are packed, not just by "side" — if this is
            # packed last, the expand=True list above would claim all the
            # remaining room and push these buttons out of view.
            footer = ctk.CTkFrame(self, fg_color="transparent")
            footer.pack(fill="x", padx=16, pady=14, side="bottom")
            ctk.CTkButton(footer, text="⚙ Settings", fg_color=Theme.CARD_LIGHT, hover_color=Theme.ACCENT,
                          command=self._handle_settings).pack(fill="x", pady=(0, 6))
            ctk.CTkButton(footer, text="⎋ Logout", fg_color=Theme.CARD_LIGHT, hover_color=Theme.ERROR,
                          command=self._handle_logout).pack(fill="x")

            # --- search ---------------------------------------------------
            self.search_entry = ctk.CTkEntry(self, placeholder_text="🔍 Search users...",
                                              fg_color=Theme.CARD_LIGHT, border_width=0)
            self.search_entry.pack(fill="x", padx=16, pady=(10, 10))
            self.search_entry.bind("<KeyRelease>", self._handle_search)

            ctk.CTkLabel(self, text="ONLINE USERS", font=(Theme.FONT_FAMILY, 10, "bold"),
                         text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=18, pady=(6, 2))
            self.user_list = UserList(self, on_user_selected=self._handle_user_selected, height=220)
            self.user_list.pack(fill="both", expand=False, padx=8)

            ctk.CTkLabel(self, text="RECENT CHATS", font=(Theme.FONT_FAMILY, 10, "bold"),
                         text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=18, pady=(10, 2))
            self.recent_chats = UserList(self, on_user_selected=self._handle_user_selected, height=180)
            self.recent_chats.pack(fill="both", expand=True, padx=8)
        else:
            tk.Label(self, text="Username", bg=Theme.CARD, fg=Theme.TEXT_PRIMARY).pack(pady=10)
            self.search_entry = tk.Entry(self)
            self.search_entry.pack(fill="x", padx=10, pady=6)
            self.user_list = UserList(self, on_user_selected=self._handle_user_selected)
            self.user_list.pack(fill="both", expand=True, padx=8)
            self.recent_chats = self.user_list
            tk.Button(self, text="Settings", command=self._handle_settings).pack(fill="x", padx=16, pady=2)
            tk.Button(self, text="Logout", command=self._handle_logout).pack(fill="x", padx=16, pady=2)

    def set_profile(self, username: str):
        self.username_label.configure(text=username) if USING_CTK else None
        if USING_CTK:
            self.avatar.configure(text=username[0].upper() if username else "U")

    # -- placeholder-callback wrappers ----------------------------------
    def _handle_search(self, event=None):
        # Purely visual filter placeholder — real search should call backend.
        query = self.search_entry.get().lower()
        print(f"[GUI] Search users: '{query}' (placeholder, no backend search).")

    def _handle_user_selected(self, user):
        self.app.on_user_selected(user)  # PLACEHOLDER CALLBACK

    def _handle_settings(self):
        self.app.on_open_settings()  # PLACEHOLDER CALLBACK

    def _handle_logout(self):
        self.app.on_logout()  # PLACEHOLDER CALLBACK
