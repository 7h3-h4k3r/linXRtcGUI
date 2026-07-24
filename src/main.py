try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

from .themeClass import Theme
from .loginFrame import LoginFrame
from .chatFrame import ChatFrame    
from .settingsWindow import SettingsWindow
from .toastClass import Toast
from libs.network import Network
from libs.RtClient import RtClient
  
               
def apply_ctk_defaults():

    if USING_CTK:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

class MainApplication(ctk.CTk if USING_CTK else tk.Tk):
    """
    Root application window. Owns navigation between LoginFrame and
    ChatFrame, and exposes all placeholder callback methods that a
    backend implementer should override / connect to real logic.
    """

    def __init__(self):
        super().__init__()
        apply_ctk_defaults()

        self.rtc = None
        self.connection =None
    
        self.title("Secure Chat Client")
        self.geometry(Theme.WINDOW_SIZE)
        self.minsize(*Theme.MIN_SIZE)
        if USING_CTK:
            self.configure(fg_color=Theme.BG)
        else:
            self.configure(bg=Theme.BG)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        # Simple in-memory GUI state (NOT backend state / no persistence).
        self.current_auth_method = "Password"
        self._settings_window = None

        self.login_frame = LoginFrame(self, self)
        self.chat_frame = None  # built lazily after login

        self.login_frame.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------
    def show_login_screen(self):
        if self.chat_frame is not None:
            self.chat_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.login_frame.set_status("Disconnected", "muted")

    def show_chat_screen(self, username: str = "User"):
        self.login_frame.pack_forget()
        if self.chat_frame is None:
            self.chat_frame = ChatFrame(self, self)
            self.rtc.setRecv(self,self.chat_frame)
        self.chat_frame.pack(fill="both", expand=True)
        self.chat_frame.sidebar.set_profile(username)

        # Populate with sample/demo GUI data only — replace with real data
        # from your backend once connected.
        self._load_demo_state()

    def _load_demo_state(self):
        """Fills the UI with placeholder demo data purely for visual preview."""
        demo_users = [
            {"name": "Alice", "status": "online", "last_message": "See you at 5?"},
            {"name": "Bob", "status": "away", "last_message": "Thanks!"},
            {"name": "Charlie", "status": "offline", "last_message": ""},
            {"name" : "dharani","status":"offline","last_message":"now harivasan at room"},
            {"name": "Alice", "status": "online", "last_message": "See you at 5?"},
            {"name": "Bob", "status": "away", "last_message": "Thanks!"},
            {"name": "Charlie", "status": "offline", "last_message": ""},
        ]
        self.chat_frame.sidebar.user_list.populate(demo_users)
        self.chat_frame.sidebar.recent_chats.populate([])  # shows empty state

        self.chat_frame.right_panel.update_info(
            room_name="general", connected_users=len(demo_users),
            latency="-- ms", encryption_mode="Pending backend",
            auth_type=self.current_auth_method, connection_quality="Unknown",
        )
        self.chat_frame.status_bar.update_status(
            connection_state="offline", connection_text="Disconnected",
            socket_state="idle", ping="--", packet_count=0, protocol_version="v1.0",
        )

    # ==================================================================
    # PLACEHOLDER CALLBACKS
    # ------------------------------------------------------------------
    # Everything below is intentionally empty of real logic. Replace the
    # body of each method (or attach your own handlers) to wire up your
    # custom socket protocol, authentication, and encryption.
    # ==================================================================

    def on_login(self, username, password):
        """PLACEHOLDER CALLBACK — connect your authentication logic here."""
        print(f"[CALLBACK] on_login(username={username!r}, password=<hidden>)")
        try:
            self.connection = self.rtc.start(username,password)
            if self.connection:
                Toast(self,"cOzy Place for Hacker's")
                self.login_frame.set_status("Authenticating...", "info")
                self.after(700, lambda: self._simulate_login_result(username))
        except Exception as e:
            self.rtc.sock.close()
            Toast(self,str(e),"error")


    def _simulate_login_result(self, username):
        """Visual-only simulation so the GUI is demonstrable stand-alone."""
        if username:
            self.login_frame.set_status("Connected", "success")
            self.after(400, lambda: self.show_chat_screen(username))
        else:
            self.login_frame.set_status("Authentication Failed", "error")

    def on_logout(self):
        """PLACEHOLDER CALLBACK — connect your disconnect/session-teardown logic here."""
        print("[CALLBACK] on_logout()")
        self.show_login_screen()

    def on_send_message(self, message):
        """PLACEHOLDER CALLBACK — connect your message-send/encryption logic here."""
        print(f"[CALLBACK] on_send_message(message={message!r})")
        self.rtc.on_send_message_sock(message)


    def on_attach(self):
        """PLACEHOLDER CALLBACK — connect your file-attachment logic here."""
        print("[CALLBACK] on_attach()")

    def on_open_settings(self):
        """PLACEHOLDER CALLBACK — opens the settings window (GUI-only)."""
        print("[CALLBACK] on_open_settings()")
        if self._settings_window is None or not self._settings_window.winfo_exists():
            self._settings_window = SettingsWindow(self, self)
            
        else:
            self._settings_window.focus()

    def on_user_selected(self, user):
        """PLACEHOLDER CALLBACK — connect your conversation-loading logic here."""
        print(f"[CALLBACK] on_user_selected(user={user})")
        if self.chat_frame is not None:
            self.chat_frame.load_conversation(user)

    def on_change_auth(self, method):
        """PLACEHOLDER CALLBACK — connect your auth-method-switch logic here."""
        print(f"[CALLBACK] on_change_auth(method={method!r})")
        self.current_auth_method = method

    def on_save_settings(self):
        """PLACEHOLDER CALLBACK — connect your settings-persistence logic here."""
        if getattr(self, "_settings_window", None) is None:
            Toast(self, "Connection details not yet configured", "error")
            return False
        host = port =  remember = timeout = None
        try:
            host = self._settings_window.host_entry.get().strip()
            port  = int(self._settings_window.port_entry.get().strip())
            remember = self._settings_window.reconnect_var.get()
            timeout = self._settings_window.timeout_entry.get().strip()
            self.connection = Network.validate(host,port,timeout,remember)
            if self.connection and not self.rtc:
                self.rtc = RtClient(host,port)
        
        except Exception as e:
            print(e)
            Toast(self, str(e),"error", duration_ms=3000)
        

        #     "info": Theme.INFO,
        #     "success": Theme.SUCCESS,
        #     "warning": Theme.WARNING,
        #     "error": Theme.ERROR,
        # }

           
        print("[CALLBACK] on_save_settings()")

    def on_exit(self):
        """PLACEHOLDER CALLBACK — connect your graceful-disconnect logic here."""
        print("[CALLBACK] on_exit()")
        self.rtc.sock.close()
        self.destroy()
