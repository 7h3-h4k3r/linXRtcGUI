
try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from .connInte import ConnectionIndicator
class StatusBar(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Bottom bar: connection status, socket state, ping, packet count, protocol version."""

    def __init__(self, master, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.CARD, height=28, corner_radius=0, **kwargs)
        else:
            super().__init__(master, bg=Theme.CARD, height=28, **kwargs)
        self.pack_propagate(False)
        self._build_ui()

    def _field(self, text):
        if USING_CTK:
            lbl = ctk.CTkLabel(self, text=text, font=Theme.FONT_SMALL, text_color=Theme.TEXT_SECONDARY)
        else:
            lbl = tk.Label(self, text=text, bg=Theme.CARD, fg=Theme.TEXT_SECONDARY)
        lbl.pack(side="left", padx=14)
        return lbl

    def _build_ui(self):
        self.connection_indicator = ConnectionIndicator(self, text="Disconnected", state="offline")
        self.connection_indicator.pack(side="left", padx=14)

        self.socket_state_label = self._field("Socket: idle")
        self.ping_label = self._field("Ping: -- ms")
        self.packet_count_label = self._field("Packets: 0")
        self.protocol_version_label = self._field("Protocol: v1.0")

    def update_status(self, connection_state=None, connection_text=None, socket_state=None,
                       ping=None, packet_count=None, protocol_version=None):
        if connection_state is not None:
            self.connection_indicator.set_state(connection_state, connection_text)
        if socket_state is not None:
            self.socket_state_label.configure(text=f"Socket: {socket_state}")
        if ping is not None:
            self.ping_label.configure(text=f"Ping: {ping} ms")
        if packet_count is not None:
            self.packet_count_label.configure(text=f"Packets: {packet_count}")
        if protocol_version is not None:
            self.protocol_version_label.configure(text=f"Protocol: {protocol_version}")
