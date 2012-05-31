__version__ = "0.0.1"
__all__ = []

from tkinter import *
from tkinter import filedialog
from threading import Thread
import subprocess

class PyLaunchValidator():
    def __init__(self, **kwargs):
        pass
        
class PyLaunchThread(Thread):
    def __init__(self, caller):
        Thread.__init__(self)
        self.caller = caller
        
    def run(self):
        
        self.caller._on_button_clear()
        self.caller._result_widget.insert(END, "Please wait...")
        params = self.caller._generate_command_line()
        
        self.caller._on_button_clear()
        
        try:
            cmd = [sys.executable]
            cmd.extend(params)
            self._threading_state(thread_state = "start")
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout:
                self.caller._result_widget.insert(END, "{}".format(line.decode("utf-8")))
                self.caller._result_widget.see(END)
            self._threading_state(thread_state = "finish")
        except OSError as err:
            self.caller._result_widget.insert(END, "{}\n".format(err))
            self.caller._result_widget.see(END)

        
    def _threading_state(self, thread_state):
        if thread_state == "start":
            self.caller._launch_button.config(state=DISABLED)

        if thread_state == "finish":
            self.caller._launch_button.config(state=NORMAL)


class PyLaunch(Thread):
    def __init__(self, title="PyLaunch"):
        self._fields = []
        self._title = title
        self._window_height = 500
        self._window_width = 700
        Thread.__init__(self)
        
    def field(self, field_type, field_id, field_title, field_validator=None):
        self._fields.append({"type": field_type, "id": field_id, "title": field_title, "validator": field_validator})

    def launch(self, callback):
        self._callback = callback
        self._root = Tk()
        self._root.title(self._title)
        self._main_frame = Frame()
        self._main_frame.pack(expand=YES, fill=BOTH, padx=10, pady=10)
        self._create_window()
        
        self._fields_frame = Frame(self._main_frame)
        self._fields_frame.pack(expand=NO, fill=X)
        
        for field in self._fields:
            self.create_field_widget(field)
        
        self._create_result_widget()
        self._create_buttons()
        self._root.mainloop()
        print("PyLaunch terminated.")
        
    def create_field_widget(self, field):
        frame = Frame(self._fields_frame)
        
        if field["type"] == "text":
            input_widget = Text(frame, height=1, width=70, relief=SUNKEN, bd=1)
            element = input_widget
        elif field["type"] == "file" or field["type"] == "folder":
            element = Frame(frame)
            input_widget = Text(element, height=1, width=70, relief=SUNKEN, bd=1)
            Button(element, text="Browse " + field["type"] + "s", command=lambda: self._on_button_select_file(input_widget, field["type"])).pack(side=RIGHT)
            input_widget.pack(side=BOTTOM, expand=YES, fill=X)
            element.pack(side=BOTTOM)
        
        input_widget.bind("<Tab>", lambda e, input_widget=input_widget:self._on_field_tab(input_widget))
        input_widget.bind("<Return>", self._on_field_enter)
        field["widget"] = input_widget
        Label(frame, text=field["title"], justify=LEFT, anchor=W, fg="#2D5986").pack(expand=YES, fill=X)
        element.pack(side=BOTTOM, expand=YES, fill=X)
        frame.pack(side=TOP, expand=YES, fill=X)

    def _create_buttons(self):
        frame = Frame(self._main_frame)
        self._launch_button = Button(frame, text="Launch", command=self._on_button_launch)
        self._launch_button.pack(side=LEFT)
        Button(frame, text="Clear", command=self._on_button_clear).pack(side=LEFT)
        Button(frame, text="Exit", command=self._on_button_exit).pack(side=LEFT)
        frame.pack(side=BOTTOM)
        
    def _create_result_widget(self):
        frame = Frame(self._main_frame)
        Label(frame, text="Results", justify=LEFT, anchor=W).pack()
        self._result_widget = Text(frame, height=10, width=70, relief=SUNKEN, bd=1)
        self._result_widget.pack(expand=YES, fill=BOTH)
        frame.pack(side=BOTTOM, expand=YES, fill=BOTH)

    def _create_window(self):
        left = (self._root.winfo_screenwidth() / 2) - (self._window_width / 2)
        top = (self._root.winfo_screenheight() / 2) - (self._window_height / 2)
        self._root.geometry('{}x{}+{}+{}'.format(self._window_width, self._window_height, int(left), int(top)))
    
    def _generate_command_line(self):
        params = []
        
        for field in self._fields:
            params.append([field["id"], field["widget"].get(1.0, END)])
        
        return self._callback(params)
    
    def _on_button_launch(self):
        PyLaunchThread(self).start()
        
    def _on_button_clear(self):
        self._result_widget.delete(1.0, END)
        
    def _on_button_exit(self):
        self._root.destroy()

    def _on_button_select_file(self, text_field, dialog_type):
        if dialog_type == "file":
            filename = filedialog.askopenfilename().strip()
        else:
            filename = filedialog.askdirectory().strip()
        
        if filename == "":
            return
        text_field.delete(1.0, END)
        text_field.insert(1.0, filename)
        
    def _on_field_tab(self, element):
        element.tk_focusNext().focus()
        return "break"

    def _on_field_enter(self, element):
        self._on_button_launch()
        return "break"
        
### Now starts the demo ###

def pylaunch_callback(params):
    """
    Callback function for generating the command line parameters
    """
    return [__file__] + ([p[1].strip() for p in params])

def main():

    if len(sys.argv) > 1:
        if sys.argv[1] == "pylaunch":
            pl = PyLaunch(title="PyLaunch Demo")
            pl.field(field_type="text", field_id="firstname", field_title="Your first name", field_validator=PyLaunchValidator(required=True))
            pl.field(field_type="text", field_id="lastname", field_title="Your last name", field_validator=PyLaunchValidator(required=True))
            pl.field(field_type="file", field_id="inputfile1", field_title="Some file to select")
            pl.field(field_type="folder", field_id="folder1", field_title="Some folder to select")
            print("Starting PyLaunch...")
            pl.launch(pylaunch_callback)
        else:
            print("Calling the main script. You are '{} {}' and you have selected the file '{}' and the folder '{}'".format(*sys.argv[1:len(sys.argv)]))
    else:
        print("Params are missing. Usage: pylaunch.py pylaunch")
    
if __name__ == "__main__": main()