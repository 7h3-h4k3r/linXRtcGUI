"""
Secure Chat Client - Frontend GUI
==================================

A professional, modern desktop GUI for a secure chat client, built with
CustomTkinter (falls back to Tkinter/ttk automatically if CustomTkinter
is not installed).

IMPORTANT — SCOPE OF THIS FILE
-------------------------------
This module implements ONLY the presentation layer (widgets, layout,
navigation, and visual state). It intentionally contains:

    - NO networking / socket code
    - NO authentication logic
    - NO encryption / cryptography
    - NO server communication of any kind

Every user action (login, sending a message, changing settings, etc.)
calls a small set of placeholder "callback" functions/methods that
currently do nothing but print a debug line. Wire your own backend
(custom protocol, auth, encryption, etc.) into those callbacks — search
this file for "PLACEHOLDER CALLBACK" to find every hook point.

Author: (your name)
"""

import sys
import time
import random
import string
from datetime import datetime


try:
    import customtkinter as ctk
    USING_CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk
    USING_CTK = False

import tkinter as tk
from tkinter import ttk


from src.main import MainApplication


def main():
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
