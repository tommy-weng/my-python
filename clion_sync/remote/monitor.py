#!/usr/bin/python3

#!/opt/python/x86_64/3.7.1-1/bin/python
import os
import sys
import time
import subprocess
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from inspect import currentframe, getframeinfo

def remove_remained_listener():
    print("Remove the remained monitor process ...")
    sys.stdout.flush()
    output = subprocess.check_output("find /proc/*/fd -lname anon_inode:inotify 2>/dev/null |  cut -d/ -f3 | xargs -I '{}' -- ps --no-headers -o '%p %U %c' -p '{}' | uniq -c | sort -nr", shell=True).decode("utf-8")
    for line in output.split("\n"):
        words = re.split('\s+', line.strip())
        if len(words) == 4 and words[3] == "python3" and int(words[1]) != os.getpid():
            print("Kill process %s" % (words[1]))
            sys.stdout.flush()
            subprocess.call("kill -9 " + words[1], shell=True)

def log_print(s):
    cf = currentframe()
    frameinfo = getframeinfo(cf)
    print("%s:%s -- %s" % (frameinfo.filename, cf.f_back.f_lineno, s))

class Monitor(FileSystemEventHandler):
    def __init__(self, target_path, monitor_files, postfix):
        super().__init__()
        self.postfix = postfix.split(';')
        self.target_path = target_path
        self.trim_count = len(self.target_path)
        self.monitor_files = monitor_files
        self.running = True

    def on_any_event(self, event):
        # if event.event_type == "moved":
        #     log_print("event_type=%s, src_path=%s, is_directory=%s, dest_path=%s" % (event.event_type, event.src_path, event.is_directory, event.dest_path))
        # else:
        #     log_print("event_type=%s, src_path=%s, is_directory=%s" % (event.event_type, event.src_path, event.is_directory))

        if event.is_directory and event.event_type == "modified":
            if event.src_path.endswith(".git"):
                msg = self.build_msg(event)
                self._new_message(msg)
        elif self._is_cared(event.src_path, event.is_directory, event.event_type == "deleted"):
            msg = self.build_msg(event)
            self._new_message(msg)
        elif event.event_type == "moved" and self._is_cared(event.dest_path, event.is_directory, False):
            msg = self.build_msg(event)
            self._new_message(msg)

    def _is_cared(self, src_path, is_directory, is_deleted):
        if len(src_path) <= self.trim_count:
            return False
        
        relative_path = src_path[self.trim_count:]
        dir_name = relative_path.replace('\\', '/')

        for p in self.monitor_files:
            if dir_name.startswith(p):
                if is_directory:
                    return True

                fname, ext = os.path.splitext(relative_path)
                if ext in self.postfix:
                    return True
                elif ext == '' and is_deleted:
                    return True
                    
        return False

    def build_msg(self, event):
        if event.event_type == 'deleted':
            t = "X"
        else: 
            t = "D" if event.is_directory else "F"
        if event.event_type == "moved":
            return event.event_type + ":" + t + ":" + event.src_path[self.trim_count:] + ":" +  event.dest_path[self.trim_count:]
        else:
            return event.event_type + ":" + t + ":" + event.src_path[self.trim_count:]

    def _new_message(self, msg):
        sys.stdout.write('>' + msg + '\n')
        sys.stdout.flush()

    def start(self):
        self._log("start event observer on %s ..." % (self.target_path))
        observer = Observer()
        observer.schedule(self, self.target_path, recursive=True)
        observer.start()
        self._log("observer is ready")
        sys.stdout.flush()
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.stop()
    
    def _log(self, msg):
        print(msg)
        sys.stdout.flush()

if __name__ == "__main__":
    remove_remained_listener()
    if len(sys.argv) < 4:
        path = '/var/fpwork/qrb378/gnb/'
        sync_file = '/home/qrb378/.clion_remote_sync/clion_sync_list.txt'
        postfix = '.h;.hpp;.hxx;.c;.cpp;.cxx;.cc;.md;.adoc;.pu;.png;.txt'
    else:
        path = sys.argv[1]
        sync_file =sys.argv[2]
        postfix = sys.argv[3]
    with open(sync_file) as fp:
        monitor_files = [line.strip() for line in fp.readlines()]
        monitor = Monitor(path, monitor_files, postfix)
        monitor.start()
