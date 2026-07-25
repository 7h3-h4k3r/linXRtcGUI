try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
class RightPanel(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Right-hand info panel: room info, connected users, server/connection info."""

    def __init__(self, master, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.CARD, corner_radius=0, width=260, **kwargs)
        else:
            super().__init__(master, bg=Theme.CARD, width=260, **kwargs)
        self.pack_propagate(False)
        self._build_ui()
      
        self.update_client_log('Your connection to the Lab now')
        

    def _section_title(self, text):
        if USING_CTK:
            ctk.CTkLabel(self, text=text, font=(Theme.FONT_FAMILY, 10, "bold"),
                         text_color=Theme.TEXT_MUTED).pack(anchor="w", padx=16, pady=(16, 4))
        else:
            tk.Label(self, text=text, bg=Theme.CARD, fg=Theme.TEXT_MUTED).pack(anchor="w", padx=16, pady=(16, 4))

    def _info_row(self, label, value_var_name):
        if USING_CTK:
            row = ctk.CTkFrame(self, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row, text=label, font=Theme.FONT_SMALL,
                         text_color=Theme.TEXT_SECONDARY).pack(side="left")
            value_label = ctk.CTkLabel(row, text="—", font=Theme.FONT_SMALL,
                                        text_color=Theme.TEXT_PRIMARY)
            value_label.pack(side="right")
        else:
            row = tk.Frame(self, bg=Theme.CARD)
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=label, bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(side="left")
            value_label = tk.Label(row, text="—", bg=Theme.CARD, fg=Theme.TEXT_PRIMARY)
            value_label.pack(side="right")
        setattr(self, value_var_name, value_label)
        return row

    def _build_ui(self):
        self._section_title("ROOM INFO")
        self._info_row("Room Name", "room_name_value")
        self._info_row("Connected Users", "connected_users_value")

        self._section_title("SERVER INFO")
        self._info_row("Latency", "latency_value")
        self._info_row("Encryption Mode", "encryption_mode_value")
        self._info_row("Authentication", "auth_type_value")
        self._info_row("Connection Quality", "connection_quality_value")

        self._section_title("Client Logs")
        if USING_CTK:
            self.client_logs = ctk.CTkScrollableFrame(self, fg_color="transparent")
        else:
            self.client_logs = tk.Frame(self, bg=Theme.CARD)
        self.client_logs.pack(fill="both", expand=True, padx=8, pady=(0, 10))

    def update_info(self, **kwargs):
        """Update any subset of: room_name, connected_users, latency,
        encryption_mode, auth_type, connection_quality."""
        mapping = {
            "room_name": "room_name_value",
            "connected_users": "connected_users_value",
            "latency": "latency_value",
            "encryption_mode": "encryption_mode_value",
            "auth_type": "auth_type_value",
            "connection_quality": "connection_quality_value",
        }
        for key, value in kwargs.items():
            widget_name = mapping.get(key)
            if widget_name and hasattr(self, widget_name):
                getattr(self, widget_name).configure(text=str(value))

    def update_client_log(self, msg, colour=None):
        if colour is None:
            colour = Theme.TEXT_PRIMARY

        if USING_CTK:
            ctk.CTkLabel(
                self.client_logs,
                text=msg,
                anchor="w",
                justify="left",
                font=Theme.FONT_SMALL,
                text_color=colour
            ).pack(fill="x", padx=8, pady=2)
        else:
            tk.Label(
                self.client_logs,
                text=msg,
                anchor="w",
                justify="left",
                bg=Theme.CARD,
                fg=colour
            ).pack(fill="x", padx=8, pady=2)
        