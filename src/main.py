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
from .loginFrame import LoginFrame
from .signupClass import RegFrame
from libs.network import Network
from libs.RtClient import RtClient
from dotenv import load_dotenv ,set_key
import time
from . import ENV_PATH
import os
load_dotenv(ENV_PATH)
  
               
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
        
        self.host  = None
        self.port = None
        self.connection = self.on_config()
        self.remember =  None
        self.title("Real Time E2E chat Application")
        self.geometry(Theme.WINDOW_SIZE)
        self.minsize(*Theme.MIN_SIZE)
        if USING_CTK:
            self.configure(fg_color=Theme.BG)
        else:
            self.configure(bg=Theme.BG)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.current_auth_method = "Password"
        self._settings_window = None

        
        self.chat_frame = None  
        self.frames = {}
        for F in (LoginFrame, RegFrame):
            frame = F(master=self, app=self)
            self.frames[F] = frame
           
       
        self.show_frame(LoginFrame)

    
    def show_frame(self, frame_class):
        for f in self.frames.values():
            f.pack_forget()
        frame = self.frames[frame_class]
        frame.pack(fill="both", expand=True)  
    

        
    def show_chat_screen(self, username: str = "User"):
        self.frames[LoginFrame].pack_forget()
        if self.chat_frame is None:
            self.chat_frame = ChatFrame(self, self)
            self.rtc.setRecv(self,self.chat_frame,username)
        self.chat_frame.pack(fill="both", expand=True)
        
    def on_login(self, username, password):
        print(self.host ,self.port)
        """PLACEHOLDER CALLBACK — connect your authentication logic here."""
        print(f"[CALLBACK] on_login(username={username!r}, password=<hidden>)")
        if self.rtc is None:
            self.rtc = RtClient(self.host,self.port)
        try:
            self.connection = self.rtc.start(username,password)
            print(self.host,self.port)
    
            if self.connection:
                Toast(self,"cOzy Place for Hacker's")
                self.frames[LoginFrame].set_status("Authenticating...", "info")
                self.after(700, lambda: self._simulate_login_result(username))
            else:
                Toast(self,'Auth Failed Credentials is invalid',"error")
            
        except Exception as e:
            self.rtc.sock.close()
            self.rtc = None
            print(str(e))
            Toast(self,'SERVER ERR:'+str(e),"error")


    def on_signup(self, username, password, email):
        """PLACEHOLDER CALLBACK — connect your authentication logic here."""
        print(f"[CALLBACK] on_signup(username={username!r}, password=<hidden> ,email={email}")
        if self.rtc is None:
            self.rtc = RtClient(self.host,self.port)
        try:
            self.connection = self.rtc.signup(username,password,email)
            if self.connection:
                Toast(self,"Signup Success",duration_ms=7000)
                self.show_frame(LoginFrame)
        except Exception as e:
            self.rtc.sock.close()
            self.rtc = None
            Toast(self,'SERVER ERR: Host is not Alive',"error")

    def _simulate_login_result(self, username):
        """Visual-only simulation so the GUI is demonstrable stand-alone."""
        if username:
            self.frames[LoginFrame].set_status("Connected", "success")
            self.after(400, lambda: self.show_chat_screen(username))
        else:
            self.frames[LoginFrame].set_status("Authentication Failed", "error")

    def on_send_message(self, message):
        """PLACEHOLDER CALLBACK — connect your message-send/encryption logic here."""
        print(f"[CALLBACK] on_send_message(message={message!r})")
        self.rtc.on_send_message_sock(message)


    def on_attach(self):
        """PLACEHOLDER CALLBACK — connect your file-attachment logic here."""
        print("[CALLBACK] on_attach()")
        Toast(self,"not updated","info")

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
    def on_config(self):
        remember = os.getenv('REM','')
        if not remember:
            Toast(self,"Connection details not yet configured","error")
            return False
        host = os.getenv('HOST','')
        port = os.getenv('PORT','')
        if not host or not port:
            Toast(self,'Please Configure the host and port',"warning")
            return False
        port = int(port)
        try:
            self.connection = Network.validate(host,port,remember)
            self.host = host
            self.port = int(port)
            
            return self.connection
        except ConnectionResetError:
            Toast(self,"Host is not a Alive",'info')
    def on_save_settings(self):
        """PLACEHOLDER CALLBACK — connect your settings-persistence logic here."""
        if getattr(self, "_settings_window", None) is None:
            Toast(self, "_settings_error", "error")
            return False
        host = port =  remember = None
        try:
            host = self._settings_window.host_entry.get().strip()
            port  = self._settings_window.port_entry.get().strip()
            remember = self._settings_window.reconnect_var.get()

            if not host or not port:
                Toast(self,'Fill Host configuration Details',"warning",duration_ms=3000)
                return
            print(remember)
            if remember:
                set_key(ENV_PATH, "HOST", host)
                os.environ["HOST"] = host 
                set_key(ENV_PATH, "PORT",port)
                os.environ["PORT"] = port
                set_key(ENV_PATH,"REM",'True')
                os.environ["REM"] = 'True'
            else:
                set_key(ENV_PATH, "HOST", '')
                os.environ["HOST"] =""
                set_key(ENV_PATH, "PORT",'')
                os.environ["PORT"] = ""
                set_key(ENV_PATH,"REM",'')
                os.environ["PORT"] = ""
            port = int(port)
            
            self.connection = Network.validate(host,port,remember)
            if self.connection:
                self.host = host 
                self.port = int(port)
                self.remember = remember
        except Exception as e:
            
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
        if self.rtc is not None and getattr(self.rtc, "sock", None) is not None:
            try:
                self.rtc.exit()
                self.rtc.sock.close()
            except Exception as e:
                print(f"Error closing socket: {e}")
                
        self.rtc = None
        self.destroy()