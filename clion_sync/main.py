import tkinter as tk
from tkinter import ttk
from tkinter import messagebox 
import os
import json
import sys
import re
import daemon
from functools import partial
import getpass

VERSION = '0.8'

class InputWidget:
    def __init__(self, parent, label, layout, default, callback):
        self.callback = callback
        self.layout = layout
        self.label_w = tk.Label(parent, text=label, anchor='w')

        self.var = tk.StringVar()
        self.var.set(default)
        self.var.trace("w", lambda name, index, mode, sv=self.var:callback(sv.get()))
        self.input_w = tk.Entry(parent, textvariable=self.var)

    def hide(self):
        self.label_w.pack_forget()
        self.input_w.pack_forget()
        return self

    def show(self):
        self.label_w.pack(side=tk.LEFT)
        self.input_w.pack(**self.layout)
        return self

    def setState(self, state):
        self.input_w['state'] = state
        return self

    def get(self):
        return self.var.get()
    
    def set(self, input):
        self.var.set(input)
        return self

class ButtonWidget:
    def __init__(self, parent, text, callback, layout={'side':tk.LEFT}):
        self.layout = layout
        self.text = tk.StringVar()
        self.text.set(text)
        self.w = tk.Button(parent, textvariable=self.text, command=callback)
    def show(self):
        self.w.pack(**self.layout)
        return self
    def hide(self):
        self.w.pack_forget()
        return self
    def setState(self, state):
        self.w['state'] = state
        return self
    def changeText(self, new_text):
        self.text.set(new_text)

class ComboboxWidget:
    def __init__(self, parent, text, candidates, default, layout, callback=None):
        self.layout = layout
        self.callback = callback
        self.candidates = candidates

        self.label_w = tk.Label(parent, text=text, anchor='w')

        self.combobox_w = ttk.Combobox(parent, width=max([len(str(k)) for k in candidates]))
        self.combobox_w['values'] = candidates
        self.combobox_w.current(candidates.index(default))
        self.combobox_w['state'] = 'readonly'
        self.combobox_w.bind("<<ComboboxSelected>>", self._val_change, "+")

    def hide(self):
        self.label_w.pack_forget()
        self.combobox_w.pack_forget()
        return self

    def show(self):
        self.label_w.pack(side=tk.LEFT)
        self.combobox_w.pack(**self.layout)
        return self

    def setState(self, state):
        self.combobox_w['state'] = state
        return self

    def _val_change(self, event=None):
        if self.callback != None:
            self.callback(self.get())

    def get(self):
        return self.candidates[self.combobox_w.current()]

class Configuration:
    default_configuration = {
        'ver' : VERSION,
        'geometry' : '340x160+500+500',
        'server':'',
        'remote' : '',
        'local' : '',
        'rsa' : 'C:\\Users\\{}\\.ssh\\id_rsa'.format(getpass.getuser()),
        'target':'L2PS',
    }
    def __init__(self):
        script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.config_name = os.path.join(script_path, "configure.json")
        self._load()

    def _load(self):
        self.configuration = {'ver':VERSION}
        if os.path.isfile(self.config_name):
            try:
                with open(self.config_name,'r') as load_f:
                    configuration = json.load(load_f)
                    # if 'ver' in configuration and configuration['ver'] == VERSION:
                    self.configuration = configuration
            except Exception as err:
                sys.stdout.write("Load configuration error with " + str(err) + "\n")
   
    def _save(self):
        with open(self.config_name,"w") as f:
            json.dump(self.configuration, f, indent=4)

    def __getitem__(self, key):
        if key not in self.configuration:
            self.configuration[key] = self.default_configuration[key]
        return self.configuration[key]

    def __setitem__(self, key, value):
        self.configuration[key] = value
        self._save()

class MainWindow:
    def __init__(self):
        self.configuration = Configuration()
        self.start_sync = False
        self.daemon = None

    def start_button_callback(self):
        if not self.start_sync:
            self._start_sync()
        else:
            self._stop_sync()

    def _stop_sync(self):
        self.start_sync = False
        self.remote_server.setState('normal')
        self.local_folder.setState('normal')
        self.remote_folder.setState('normal')
        self.rsa_key_file.setState('normal')
        self.target_combobox.setState('normal')
        self.start_button.changeText('Start Sync')
        self.daemon.stop_monitor()

    def _start_sync(self):
        self.start_sync = True
        self._create_daemon().start_monitor()
        self.remote_server.setState('disable')
        self.local_folder.setState('disable')
        self.remote_folder.setState('disable')
        self.rsa_key_file.setState('disable')
        self.target_combobox.setState('disable')
        self.start_button.changeText('Stop Sync')

    def _create_daemon(self):
        if not self.daemon:
            try:
                self.daemon = daemon.Daemon(self.remote_server.get(), self.rsa_key_file.get(), self.local_folder.get(), self.remote_folder.get(), self.target_combobox.get(), ".h;.hpp;.hxx;.c;.cpp;.cxx;.cc;.md;.adoc;.pu;.png;.txt", self.message_box)
                self.root.after(5000, self._check_daemon_alive) 
            except PermissionError as err:
                messagebox.showerror("can't find the valid compile_commands.json, please build it and try it again.")
                self.daemon = None
                raise Exception("create daemon failed.")
            except Exception as err:
                messagebox.showerror("Error", err)
                self.daemon = None
                raise Exception("create daemon failed.")
        return self.daemon

    def _check_daemon_alive(self):
        if self.daemon:
            if self.daemon.is_alive():
                self.root.after(5000, self._check_daemon_alive)
            else:
                messagebox.showerror("Error", "ssh was disconnected abnoramally.")
                if self.start_sync:
                    self._stop_sync()
                self.daemon = None

    def message_box(self, msg, buttons):
        win = tk.Toplevel(self.root)
        win.title('warning')
        tk.Label(win, text=msg).pack()
        row = tk.Frame(win)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        ret = None
        def call_back(b):
            nonlocal ret
            ret = b
            win.destroy()
        for b in buttons:
            tk.Button(row, text=b, command=partial(call_back, b)).pack(side=tk.LEFT)
        self.root.wait_window(win)
        return ret

    def _daemon_call(self, func):
        try:
            if self._create_daemon():
                getattr(self.daemon, func)()
                print("Execute %s successfully." % (func))
                messagebox.showinfo("Info", "Execute %s successfully." % (func))
        except OSError as err:
            messagebox.showerror("Error", err)
            self.daemon = None

    # def build_callback(self, target):
    #     self._create_daemon().build(target)

    def on_close(self):
        self.configuration['geometry'] = self.root.winfo_geometry()
        self.root.quit()

    def _restore(self, root):
        geometry = self.configuration['geometry']
        match = re.match(r'(\d+)x(\d+)\+(\d+)\+(\d+)', geometry)
        if match:
            [w, h, x, y] = [int(match.group(i+1)) for i in range(4)]
            if x + w > root.winfo_screenwidth() or y + h > root.winfo_screenheight():
                x = (root.winfo_screenwidth() - w) / 2
                y = (root.winfo_screenheight() - h) / 2
                geometry = "%dx%d+%d+%d" % (w, h, x, y)
            root.geometry(geometry)
        
        self.remote_folder.set(self.configuration['remote'])
        self.local_folder.set(self.configuration['local'])
        self.rsa_key_file.set(self.configuration['rsa'])

    def _target_change(self, target):
        self.configuration['target'] = target
        self.daemon = None

    def _param_change(self, key, value):
        self.configuration[key] = value
        self.daemon = None
        
    def run(self):
        self.root = root = tk.Tk()
        root.title("source sync by qrb378, v" + VERSION)
        # base = sys._MEIPASS if hasattr(sys, "frozen") else os.path.dirname(__file__)
        # datafile = os.path.join(base, "TtiTraceHelper.ico")
        # root.iconbitmap(datafile)
        # root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 1nd row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        self.remote_server = InputWidget(row, "LinSEE server:", {'side':tk.LEFT, 'expand':tk.YES, 'fill':tk.X}, self.configuration["server"], partial(self._param_change, 'server')).show()

        # 2nd row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        self.local_folder = InputWidget(row, "Local Folder:", {'side':tk.LEFT, 'expand':tk.YES, 'fill':tk.X}, self.configuration["local"], partial(self._param_change, 'local')).show()

        # 3rd row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        self.remote_folder = InputWidget(row, "Remote Folder:", {'side':tk.LEFT, 'expand':tk.YES, 'fill':tk.X}, self.configuration["remote"], partial(self._param_change, 'remote')).show()

        # 4th row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        self.rsa_key_file = InputWidget(row, "RSA Key File:", {'side':tk.LEFT, 'expand':tk.YES, 'fill':tk.X}, self.configuration["rsa"], partial(self._param_change, 'rsa')).show()

        # 5th row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        ButtonWidget(row, 'Download .git', partial(self._daemon_call, "download_git"), {'side':tk.RIGHT}).show()
        ButtonWidget(row, 'Download Code', partial(self._daemon_call, "download"), {'side':tk.RIGHT}).show()
        ButtonWidget(row, 'Upload All', partial(self._daemon_call, "upload"), {'side':tk.RIGHT}).show()
        self.target_combobox = ComboboxWidget(row, "", ["L2PS", "L2PS_UT", "L2PS_SCT", "L2LO", "L2LO_UT"], self.configuration['target'], {'side':tk.LEFT}, self._target_change).show()

        # 6th row
        row = tk.Frame(root)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        ButtonWidget(row, 'Quit', self.on_close, {'side':tk.RIGHT}).show()
        ButtonWidget(row, 'Generate CMakefile', partial(self._daemon_call, "generate_cmake"), {'side':tk.RIGHT}).show()
        ButtonWidget(row, 'Update Dependency', partial(self._daemon_call, "update_dependency"), {'side':tk.RIGHT}).show()
        self.start_button = ButtonWidget(row, 'Start Sync', self.start_button_callback, {'side':tk.RIGHT}).show()

        # 7th row
        # row = tk.Frame(root)
        # row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        # InputWidget(row, "UT Binary:", {'side':tk.LEFT, 'expand':tk.YES, 'fill':tk.X}, self.configuration, 'ut').show()
        # InputWidget(row, "Port:", {'side':tk.LEFT, 'expand':tk.YES, 'ipadx':1}, self.configuration, 'ut').show()
        # ButtonWidget(row, 'Debug', self.on_close, {'side':tk.RIGHT}).show()

        self._restore(root)
        root.mainloop()

if __name__ == '__main__':
    MainWindow().run()