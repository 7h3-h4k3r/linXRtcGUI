try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False
from .themeClass import Theme
from .toastClass import Toast
class LoginFrame(ctk.CTkFrame if USING_CTK else tk.Frame):
    """Centered login card shown before the user authenticates."""

    def __init__(self, master, app, **kwargs):
        if USING_CTK:
            super().__init__(master, fg_color=Theme.BG, **kwargs)
        else:
            super().__init__(master, bg=Theme.BG, **kwargs)

        self.app = app
        self._password_visible = False
        self._build_ui()

    def _build_ui(self):
        # Centering wrapper
        if USING_CTK:
            card = ctk.CTkFrame(self, fg_color=Theme.CARD, corner_radius=Theme.CORNER_RADIUS,
                                 width=380, height=480)
        else:
            card = tk.Frame(self, bg=Theme.CARD, width=380, height=480)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        if USING_CTK:
            ctk.CTkLabel(card, text="🔒 Secure Chat", font=Theme.FONT_TITLE,
                         text_color=Theme.TEXT_PRIMARY).pack(pady=(34, 4))
            ctk.CTkLabel(card, text="Sign in to continue", font=Theme.FONT_SUBTITLE,
                         text_color=Theme.TEXT_SECONDARY).pack(pady=(0, 24))

            self.username_entry = ctk.CTkEntry(card, placeholder_text="Username", width=280,
                                                fg_color=Theme.CARD_LIGHT, border_width=0)
            self.username_entry.pack(pady=6)

            pw_row = ctk.CTkFrame(card, fg_color="transparent")
            pw_row.pack(pady=6)
            self.password_entry = ctk.CTkEntry(pw_row, placeholder_text="Password", show="•",
                                                width=240, fg_color=Theme.CARD_LIGHT, border_width=0)
            self.password_entry.pack(side="left")
            self.toggle_pw_btn = ctk.CTkButton(pw_row, text="👁", width=34, fg_color=Theme.CARD_LIGHT,
                                                hover_color=Theme.ACCENT, command=self._toggle_password)
            self.toggle_pw_btn.pack(side="left", padx=(6, 0))

            self.remember_var = ctk.BooleanVar(value=False)
            ctk.CTkCheckBox(card, text="Remember Me", variable=self.remember_var,
                             text_color=Theme.TEXT_SECONDARY, font=Theme.FONT_SMALL,
                             fg_color=Theme.ACCENT).pack(pady=(14, 4), anchor="w", padx=50)

            self.login_btn = ctk.CTkButton(card, text="Login", width=280, fg_color=Theme.ACCENT,
                                            hover_color=Theme.ACCENT_HOVER, font=Theme.FONT_BOLD,
                                            command=self._handle_login)
            self.login_btn.pack(pady=(16, 8))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(pady=4)
            ctk.CTkButton(btn_row, text="Settings", width=132, fg_color=Theme.CARD_LIGHT,
                          hover_color=Theme.CARD, command=self._handle_settings).pack(side="left", padx=4)
            ctk.CTkButton(btn_row, text="Exit", width=132, fg_color=Theme.CARD_LIGHT,
                          hover_color=Theme.ERROR, command=self._handle_exit).pack(side="left", padx=4)

            forgot = ctk.CTkLabel(card, text="Forgot Password?", font=Theme.FONT_SMALL,
                                   text_color=Theme.ACCENT, cursor="hand2")
            forgot.pack(pady=(14, 0))
            forgot.bind("<Button-1>", lambda e: self._handle_forgot_password())

            self.status_label = ctk.CTkLabel(card, text="Disconnected", font=Theme.FONT_SMALL,
                                              text_color=Theme.TEXT_MUTED)
            self.status_label.pack(side="bottom", pady=16)
        else:
            tk.Label(card, text="Secure Chat", fg=Theme.TEXT_PRIMARY, bg=Theme.CARD,
                     font=Theme.FONT_TITLE).pack(pady=(34, 4))
            self.username_entry = tk.Entry(card)
            self.username_entry.pack(pady=6)
            self.password_entry = tk.Entry(card, show="*")
            self.password_entry.pack(pady=6)
            self.remember_var = tk.BooleanVar(value=False)
            tk.Checkbutton(card, text="Remember Me", variable=self.remember_var,
                           bg=Theme.CARD, fg=Theme.TEXT_SECONDARY).pack(pady=4)
            self.login_btn = tk.Button(card, text="Login", command=self._handle_login)
            self.login_btn.pack(pady=8)
            tk.Button(card, text="Settings", command=self._handle_settings).pack(pady=2)
            tk.Button(card, text="Exit", command=self._handle_exit).pack(pady=2)
            self.status_label = tk.Label(card, text="Disconnected", fg=Theme.TEXT_MUTED, bg=Theme.CARD)
            self.status_label.pack(side="bottom", pady=16)

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        self.password_entry.configure(show="" if self._password_visible else "•")
        self.toggle_pw_btn.configure(text="🙈" if self._password_visible else "👁")

    def set_status(self, text: str, kind: str = "muted"):
        """kind: 'muted' | 'success' | 'error' | 'info'"""
        color_map = {
            "muted": Theme.TEXT_MUTED, "success": Theme.SUCCESS,
            "error": Theme.ERROR, "info": Theme.ACCENT,
        }
        self.status_label.configure(text=text, text_color=color_map.get(kind, Theme.TEXT_MUTED)) \
            if USING_CTK else self.status_label.configure(text=text, fg=color_map.get(kind, Theme.TEXT_MUTED))

    # -- placeholder-callback wrappers ----------------------------------
    def _handle_login(self):
        
        if self.app.connection:
            username = self.username_entry.get().strip()
            password = self.password_entry.get()
            self.set_status("Connecting...", "info")

            if username == 'admin' and password == 'pass@123':
                self.app.on_login(username, password)
        
            else:
                Toast(self, "invalid credentials","warning", duration_ms=3000)
        else:
            Toast(self, "Host configuration error","warning", duration_ms=3000)   

    def _handle_settings(self):
        self.app.on_open_settings()  # PLACEHOLDER CALLBACK

    def _handle_exit(self):
        self.app.on_exit()  # PLACEHOLDER CALLBACK

    def _handle_forgot_password(self):
        # Placeholder only — no recovery logic implemented here.
        print("[GUI] Forgot password clicked (placeholder, no backend logic).")
