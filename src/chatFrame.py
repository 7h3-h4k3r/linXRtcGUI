try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False


from .themeClass import Theme
from .lbarPanel import Sidebar
from .connInte import ConnectionIndicator
from .chatClass import ChatArea
from .rbarPanel import RightPanel
from .statusBar import StatusBar
class ChatFrame(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Main chat interface: sidebar + center chat + right panel + status bar."""

    def __init__(self, master, app, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.BG, **kwargs)
        else:
            super().__init__(master, bg=Theme.BG, **kwargs)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        body = ctk.CTkFrame(self, fg_color="transparent") if USING_CTK else tk.Frame(self, bg=Theme.BG)
        body.pack(fill="both", expand=True)

        # # left sidebar
        # self.sidebar = Sidebar(body, self.app) 
        # self.sidebar.pack(side="left", fill="y")

        # center column (top bar + chat area)
        center = ctk.CTkFrame(body, fg_color=Theme.BG) if USING_CTK else tk.Frame(body, bg=Theme.BG)
        center.pack(side="left", fill="both", expand=True)

        self._build_center_top_bar(center)

        self.chat_area = ChatArea(center, on_send_message=self.app.on_send_message,
                                   on_attach=self.app.on_attach)
        self.chat_area.pack(fill="both", expand=True)

        # right panel
        self.right_panel = RightPanel(body)
        self.right_panel.pack(side="right", fill="y")

        # bottom status bar (spans full width)
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x", side="bottom")

    def _build_center_top_bar(self, center):
        if USING_CTK:
            top_bar = ctk.CTkFrame(center, fg_color=Theme.CARD, height=54, corner_radius=0)
            top_bar.pack(fill="x")
            top_bar.pack_propagate(False)

            self.room_label = ctk.CTkLabel(top_bar, text="# general", font=Theme.FONT_BOLD,
                                            text_color=Theme.TEXT_PRIMARY)
            self.room_label.pack(side="left", padx=16)

            right_group = ctk.CTkFrame(top_bar, fg_color="transparent")
            right_group.pack(side="right", padx=16)

            self.encryption_status = ctk.CTkLabel(right_group, text="🔒 Encrypted", font=Theme.FONT_SMALL,
                                                    text_color=Theme.SUCCESS)
            self.encryption_status.pack(side="right", padx=(10, 0))

            self.connection_status = ConnectionIndicator(right_group, text="Connected", state="online")
            self.connection_status.pack(side="right", padx=(10, 0))
        else:
            top_bar = tk.Frame(center, bg=Theme.CARD, height=54)
            top_bar.pack(fill="x")
            self.room_label = tk.Label(top_bar, text="# general", bg=Theme.CARD, fg=Theme.TEXT_PRIMARY)
            self.room_label.pack(side="left", padx=16)

    def load_conversation(self, user: dict):
        """Reset the chat area to reflect a newly-selected conversation."""
        self.chat_area.clear()
        if USING_CTK:
            self.room_label.configure(text=f"# {user.get('name', 'chat')}")
        else:
            self.room_label.configure(text=f"# {user.get('name', 'chat')}")