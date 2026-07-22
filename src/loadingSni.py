
class LoadingSpinner(ctk.CTkLabel if USING_CTK else tk.Label):
    """A lightweight text-based 'spinner' animation (no external assets)."""

    FRAMES = ["◐", "◓", "◑", "◒"]

    def __init__(self, master, **kwargs):
        if USING_CTK:
            super().__init__(master, text=self.FRAMES[0], font=(Theme.FONT_FAMILY, 18),
                              text_color=Theme.ACCENT, **kwargs)
        else:
            super().__init__(master, text=self.FRAMES[0], fg=Theme.ACCENT, bg=Theme.CARD, **kwargs)
        self._running = False
        self._frame_index = 0

    def start(self):
        self._running = True
        self._animate()

    def stop(self):
        self._running = False

    def _animate(self):
        if not self._running:
            return
        self._frame_index = (self._frame_index + 1) % len(self.FRAMES)
        self.configure(text=self.FRAMES[self._frame_index])
        self.after(150, self._animate)

