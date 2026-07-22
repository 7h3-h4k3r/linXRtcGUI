
class ProgressDialog(ctk.CTkToplevel if USING_CTK else tk.Toplevel):
    """A small modal-style dialog with an indeterminate progress bar."""

    def __init__(self, master, title="Please wait", message="Working..."):
        super().__init__(master)
        self.title(title)
        self.geometry("340x140")
        self.resizable(False, False)
        self.configure(fg_color=Theme.CARD) if USING_CTK else self.configure(bg=Theme.CARD)
        self.transient(master)
        self.grab_set()

        if USING_CTK:
            ctk.CTkLabel(self, text=message, font=Theme.FONT_BODY,
                         text_color=Theme.TEXT_PRIMARY).pack(pady=(24, 12))
            self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=260,
                                                progress_color=Theme.ACCENT)
            self.progress.pack(pady=10)
            self.progress.start()
            ctk.CTkButton(self, text="Cancel", fg_color=Theme.CARD_LIGHT, hover_color=Theme.ERROR,
                          command=self.destroy, width=100).pack(pady=8)
        else:
            tk.Label(self, text=message, fg=Theme.TEXT_PRIMARY, bg=Theme.CARD).pack(pady=(24, 12))
            self.progress = ttk.Progressbar(self, mode="indeterminate", length=260)
            self.progress.pack(pady=10)
            self.progress.start(12)
            tk.Button(self, text="Cancel", command=self.destroy).pack(pady=8)

    def close(self):
        try:
            self.progress.stop()
        except Exception:
            pass
        self.destroy()