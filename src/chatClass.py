
try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .connInte import ConnectionIndicator
from .themeClass import Theme
from .emptyClass import EmptyState
from .statusBar import StatusBar
from .mbubbleClass import MessageBubble
class ChatArea(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Scrollable chat history plus the message input row."""

    def __init__(self, master, on_send_message=None, on_attach=None, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.BG, **kwargs)
        else:
            super().__init__(master, bg=Theme.BG, **kwargs)

        self.on_send_message = on_send_message or (lambda msg: None)
        self.on_attach = on_attach or (lambda: None)

        # --- scrollable message history -------------------------------
        if USING_CTK:
            self.history = ctk.CTkScrollableFrame(self, fg_color=Theme.BG)
        else:
            self.history = tk.Frame(self, bg=Theme.BG)
        self.history.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        self.typing_label = (ctk.CTkLabel(self, text="", font=Theme.FONT_SMALL,
                                           text_color=Theme.TEXT_MUTED) if USING_CTK
                              else tk.Label(self, text="", fg=Theme.TEXT_MUTED, bg=Theme.BG))
        self.typing_label.pack(anchor="w", padx=14)

        self._build_input_row()
        self._empty_state = None
        self.show_empty_state()

    def _build_input_row(self):
        if USING_CTK:
            input_row = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=Theme.CORNER_RADIUS)
            input_row.pack(fill="x", padx=10, pady=10)

            self.attach_btn = ctk.CTkButton(input_row, text="📎", width=36, fg_color="transparent",
                                             hover_color=Theme.CARD_LIGHT, command=self._handle_attach)
            self.attach_btn.pack(side="left", padx=(6, 0), pady=6)

            self.emoji_btn = ctk.CTkButton(input_row, text="😊", width=36, fg_color="transparent",
                                            hover_color=Theme.CARD_LIGHT, command=self._handle_emoji)
            self.emoji_btn.pack(side="left", padx=(2, 6), pady=6)

            self.message_entry = ctk.CTkEntry(input_row, placeholder_text="Type a message...",
                                               fg_color=Theme.CARD_LIGHT, border_width=0,
                                               font=Theme.FONT_BODY)
            self.message_entry.pack(side="left", fill="x", expand=True, pady=8)
            self.message_entry.bind("<Return>", lambda e: self._handle_send())

            self.send_btn = ctk.CTkButton(input_row, text="Send ➤", width=90, fg_color=Theme.ACCENT,
                                           hover_color=Theme.ACCENT_HOVER, command=self._handle_send)
            self.send_btn.pack(side="right", padx=6, pady=6)
        else:
            input_row = tk.Frame(self, bg=Theme.CARD)
            input_row.pack(fill="x", padx=10, pady=10)
            self.attach_btn = tk.Button(input_row, text="📎", command=self._handle_attach)
            self.attach_btn.pack(side="left", padx=4)
            self.emoji_btn = tk.Button(input_row, text="😊", command=self._handle_emoji)
            self.emoji_btn.pack(side="left", padx=4)
            self.message_entry = tk.Entry(input_row, bg=Theme.CARD_LIGHT, fg=Theme.TEXT_PRIMARY,
                                           insertbackground=Theme.TEXT_PRIMARY)
            self.message_entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
            self.message_entry.bind("<Return>", lambda e: self._handle_send())
            self.send_btn = tk.Button(input_row, text="Send", command=self._handle_send)
            self.send_btn.pack(side="right", padx=6)

    # -- placeholder-callback wrappers ----------------------------------
    def _handle_send(self):
        text = self.message_entry.get().strip()
        if not text:
            return
        self.message_entry.delete(0, "end")
        self.add_message(sender="You", text=text, kind="self")
        self.on_send_message(text)  # PLACEHOLDER CALLBACK

    def _handle_attach(self):
        self.on_attach()  # PLACEHOLDER CALLBACK

    def _handle_emoji(self):
        # Purely cosmetic placeholder; wire up a real emoji picker later.
        self.message_entry.insert("end", "🙂")

    # -- public helpers ---------------------------------------------------
    def show_empty_state(self):
        if self._empty_state is None:
            self._empty_state = EmptyState(self.history, icon="🔒",
                                            title="No messages yet",
                                            subtitle="Messages you send will appear here, end-to-end secured by your backend.")
            self._empty_state.pack(fill="both", expand=True, pady=40)

    def hide_empty_state(self):
        if self._empty_state is not None:
            self._empty_state.destroy()
            self._empty_state = None

    def add_message(self, sender, text, kind="other", timestamp=None):
        self.hide_empty_state()
        bubble = MessageBubble(self.history, sender=sender, text=text,
                                timestamp=timestamp, kind=kind)
        bubble.pack(fill="x")
        self.after(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        try:
            if USING_CTK:
                self.history._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def set_typing(self, who: str = None):
        text = f"{who} is typing..." if who else ""
        self.typing_label.configure(text=text)

    def clear(self):
        for child in self.history.winfo_children():
            child.destroy()
        self._empty_state = None
        self.show_empty_state()
