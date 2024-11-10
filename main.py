from engine.MProjectorWindow import ProjectorWindow
import time

if __name__ == "__main__":
    # Create and run the app
    app = ProjectorWindow()
    
    while 1:
        app.mainloop()
        time.sleep(0.1)