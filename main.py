import tkinter as tk
from Window import TkinterApp

def main():
    root = tk.Tk()
    app = TkinterApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()

if __name__ == "__main__":
    main()