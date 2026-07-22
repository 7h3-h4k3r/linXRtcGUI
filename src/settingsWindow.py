try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme

class SettingsWindow(ctk.CTkToplevel if USING_CTK else tk.Toplevel):
    """Tabbed settings window: General / Connection / Authentication / Appearance / About."""

    AUTH_METHODS = ["Password", "API Key", "Certificate", "Token", "QR", "Public Key"]

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.title("Settings")
        self.geometry("560x460")
        self.minsize(480, 400)
        self.host_entry = None
        self.port_entry = None
        self.reconnect_var = None
        self.timeout_entry = None
        if USING_CTK:
            self.configure(fg_color=Theme.BG)
        else:
            self.configure(bg=Theme.BG)
        self.transient(master)

        self._build_ui()

    def _build_ui(self):
        # --- action bar (Save / Cancel) -------------------------------
        # Packed BEFORE the tabview below (side="bottom") so it reserves
        # its space first — otherwise the expanding tabview would claim
        # the whole window and push these buttons out of view, same issue
        # as the sidebar footer.
        if USING_CTK:
            action_bar = ctk.CTkFrame(self, fg_color="transparent")
            action_bar.pack(fill="x", side="bottom", padx=14, pady=(0, 14))
            ctk.CTkButton(action_bar, text="Save", width=110, fg_color=Theme.ACCENT,
                          hover_color=Theme.ACCENT_HOVER, command=self._handle_save).pack(side="right")
            ctk.CTkButton(action_bar, text="Cancel", width=110, fg_color=Theme.CARD_LIGHT,
                          hover_color=Theme.CARD, command=self._handle_cancel).pack(side="right", padx=(0, 8))
        else:
            action_bar = tk.Frame(self, bg=Theme.BG)
            action_bar.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
            tk.Button(action_bar, text="Save", command=self._handle_save).pack(side="right")
            tk.Button(action_bar, text="Cancel", command=self._handle_cancel).pack(side="right", padx=(0, 8))

        if USING_CTK:
            self.tabview = ctk.CTkTabview(self, fg_color=Theme.CARD, segmented_button_selected_color=Theme.ACCENT)
            self.tabview.pack(fill="both", expand=True, padx=14, pady=14)
            for tab_name in ("General", "Connection", "Authentication", "Appearance", "About"):
                self.tabview.add(tab_name)

            self._build_general_tab(self.tabview.tab("General"))
            self._build_connection_tab(self.tabview.tab("Connection"))
            self._build_auth_tab(self.tabview.tab("Authentication"))
            self._build_appearance_tab(self.tabview.tab("Appearance"))
            self._build_about_tab(self.tabview.tab("About"))
        else:
            notebook = ttk.Notebook(self)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            for tab_name, builder in (
                ("General", self._build_general_tab),
                ("Connection", self._build_connection_tab),
                ("Authentication", self._build_auth_tab),
                ("Appearance", self._build_appearance_tab),
                ("About", self._build_about_tab),
            ):
                frame = tk.Frame(notebook, bg=Theme.BG)
                notebook.add(frame, text=tab_name)
                builder(frame)

    def _build_general_tab(self, tab):
        if USING_CTK:
            ctk.CTkLabel(tab, text="Display Name").pack(anchor="w", padx=16, pady=(16, 4))
            ctk.CTkEntry(tab, placeholder_text="Your display name", width=300).pack(anchor="w", padx=16)
            ctk.CTkLabel(tab, text="Status Message").pack(anchor="w", padx=16, pady=(16, 4))
            ctk.CTkEntry(tab, placeholder_text="What's on your mind?", width=300).pack(anchor="w", padx=16)
        else:
            tk.Label(tab, text="Display Name", bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=8)
            tk.Entry(tab).pack(anchor="w", padx=16)

    def _build_connection_tab(self, tab):
        if USING_CTK:
            ctk.CTkLabel(tab, text="Host").pack(anchor="w", padx=16, pady=(16, 4))

            self.host_entry = ctk.CTkEntry(
                tab,
                placeholder_text="e.g. chat.example.com",
                width=300
            )
            self.host_entry.pack(anchor="w", padx=16)

            ctk.CTkLabel(tab, text="Port").pack(anchor="w", padx=16, pady=(16, 4))

            self.port_entry = ctk.CTkEntry(
                tab,
                placeholder_text="e.g. 8443",
                width=140
            )
            self.port_entry.pack(anchor="w", padx=16)

            self.reconnect_var = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                tab,
                text="Reconnect Automatically",
                variable=self.reconnect_var,
                fg_color=Theme.ACCENT
            ).pack(anchor="w", padx=16, pady=16)

            ctk.CTkLabel(tab, text="Timeout (seconds)").pack(anchor="w", padx=16, pady=(4, 4))

            self.timeout_entry = ctk.CTkEntry(
                tab,
                placeholder_text="30",
                width=140
            )
            self.timeout_entry.pack(anchor="w", padx=16)
            

    def _build_auth_tab(self, tab):
        if USING_CTK:
            ctk.CTkLabel(tab, text="Authentication Method", font=Theme.FONT_BOLD).pack(anchor="w", padx=16, pady=(16, 6))
            self.auth_dropdown = ctk.CTkOptionMenu(tab, values=self.AUTH_METHODS, fg_color=Theme.CARD_LIGHT,
                                                     button_color=Theme.ACCENT, button_hover_color=Theme.ACCENT_HOVER,
                                                     command=self._handle_auth_change)
            self.auth_dropdown.pack(anchor="w", padx=16)

            self.auth_detail_label = ctk.CTkLabel(tab, text=self._auth_description("Password"),
                                                    font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED,
                                                    wraplength=460, justify="left")
            self.auth_detail_label.pack(anchor="w", padx=16, pady=16)
        else:
            tk.Label(tab, text="Authentication Method", bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=8)
            self.auth_var = tk.StringVar(value="Password")
            dropdown = ttk.Combobox(tab, textvariable=self.auth_var, values=self.AUTH_METHODS, state="readonly")
            dropdown.pack(anchor="w", padx=16)
            dropdown.bind("<<ComboboxSelected>>", lambda e: self._handle_auth_change(self.auth_var.get()))

    def _handle_save(self):
        # GUI-only: collect current field values are already reflected in
        # self.app.current_auth_method etc. via _handle_auth_change. Add
        # any other field collection here before calling your backend.
        self.app.on_save_settings()  # PLACEHOLDER CALLBACK
        self.destroy()

    def _handle_cancel(self):
        self.destroy()

    def _auth_description(self, method):
        descriptions = {
            "Password": "Standard username/password authentication.",
            "API Key": "Authenticate using a long-lived API key.",
            "Certificate": "Authenticate using a client TLS certificate.",
            "Token": "Authenticate using a one-time password / hardware token.",
            "QR": "Authenticate by scanning a QR code with a paired device.",
            "Public Key": "Authenticate using a public/private keypair (e.g. SSH-style).",
        }
        return descriptions.get(method, "")

    def _handle_auth_change(self, method):
        # GUI-only update — no real authentication logic here.
        if USING_CTK:
            self.auth_detail_label.configure(text=self._auth_description(method))
        self.app.on_change_auth(method)  # PLACEHOLDER CALLBACK

    def _build_appearance_tab(self, tab):
        if USING_CTK:
            ctk.CTkLabel(tab, text="Theme", font=Theme.FONT_BOLD).pack(anchor="w", padx=16, pady=(16, 6))
            self.theme_var = ctk.StringVar(value="Dark Theme")
            for option in ("Dark Theme", "Light Theme", "System Theme"):
                ctk.CTkRadioButton(tab, text=option, variable=self.theme_var, value=option,
                                   fg_color=Theme.ACCENT).pack(anchor="w", padx=24, pady=2)

            ctk.CTkLabel(tab, text="Font Size", font=Theme.FONT_BOLD).pack(anchor="w", padx=16, pady=(16, 6))
            self.font_size_slider = ctk.CTkSlider(tab, from_=10, to=20, number_of_steps=10,
                                                   progress_color=Theme.ACCENT, button_color=Theme.ACCENT)
            self.font_size_slider.pack(anchor="w", padx=16, fill="x", pady=(0, 16))
        else:
            tk.Label(tab, text="Theme", bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=8)

    def _build_about_tab(self, tab):
        if USING_CTK:
            ctk.CTkLabel(tab, text="🔒 Secure Chat Client", font=Theme.FONT_TITLE).pack(pady=(30, 8))
            ctk.CTkLabel(tab, text="Frontend GUI build — v0.1.0", font=Theme.FONT_SMALL,
                         text_color=Theme.TEXT_MUTED).pack()
            ctk.CTkLabel(tab, text="Backend (networking, auth, encryption) not included.",
                         font=Theme.FONT_SMALL, text_color=Theme.TEXT_MUTED,
                         wraplength=400, justify="center").pack(pady=(4, 0))
        else:
            tk.Label(tab, text="Secure Chat Client", bg=Theme.BG, fg=Theme.TEXT_PRIMARY).pack(pady=30)
