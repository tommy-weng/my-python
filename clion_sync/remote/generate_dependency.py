#!/usr/bin/env python3

import json
import subprocess
import sys
from datetime import datetime, timedelta
import threading, queue
import multiprocessing
import os
import getpass
import shlex 
import subprocess
import socket

class AllFiles:
    def __init__(self, base, ignore_path):
        self.files = {}
        self.base = base
        self.ignore_path = ignore_path
        if self.ignore_path:
            self.ignore_path = base + self.ignore_path
    def append(self, file):
        file = os.path.abspath(file)
        if self.ignore_path and file.startswith(self.ignore_path):
            return
        pos = file.rfind('/')
        fname = file[pos+1:]
        if fname in self.files:
            if file not in self.files[fname]:
                self.files[fname].append(file)
        else:
            self.files[fname] = [file]

    def get(self):
        items = []
        prefix_count = len(self.base)
        for files in self.files.values():
            items += [v[prefix_count:] for v in files]

        # Workaround the mess including in Fuse: 
        # They include the same file, one by symbol link, the other is by real file
        # In Linux, g++ can handle it, but on Windows, they are totally different file.
        if 'uplane/sct/tickler/cpp_testsuites/fuse/mcf/interface/Loadable.hpp' in items:
            items.append('uplane/sct/cpp_testsuites/fuse/mcf/interface/Loadable.hpp')

        return sorted(items)

class Parser:
    def __init__(self, base, ignore_path):
        self.q = queue.Queue()
        self.proc = None
        self.all_files = AllFiles(base, ignore_path)

    def parse_file_thread(self, directory, command):
        words = command.split()
        c = words.pop()
        assert words.pop() == "-c" # -c
        o = words.pop()
        assert words.pop() == "-o"
        words += ['-E', '-M', '-c', c]
        #t0 = datetime.now()
        output = subprocess.check_output(words, cwd=directory)
        # delta_t = (datetime.now() - t0) / timedelta(seconds=1)
        # sys.stdout.write("  %s\n" % (delta_t))
        content = output.decode("utf-8").replace('\\\n', '')
        pos = content.find(':')
        lines = content[pos+1:].split(' ')
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] != '/':
                line = directory + '/' + line
            self.q.put(line)

    def fetch_queue(self):
        while not self.q.empty() or threading.active_count() >= multiprocessing.cpu_count():
            try:
                item = self.q.get(timeout=1)
                self.all_files.append(item)
                self.q.task_done()
            except queue.Empty:
                pass

    def do(self, compile_commands):
        totals = len(compile_commands)
        count = 1
        for item in compile_commands:
            if item['file'].endswith(".S"):
                continue
            if item['file'].endswith('cmake_pch.hxx.cxx'):
                continue
            print("%s:(%s/%s) Parsing %s" % (threading.active_count(), count, totals, item['file']))
            threading.Thread(target=self.parse_file_thread, args=(item['directory'], item['command']), daemon=True).start()
            count += 1
            self.fetch_queue()
        self.fetch_queue()


def get_docker_instance():
    user = getpass.getuser()
    output = subprocess.check_output(['docker', 'ps']).decode("utf8")
    for line in output.split("\n"):
        if user in line:
            return line.split()[0]

def docker_run(argv):
    cmd_line = " ".join(argv)
    print(cmd_line)
    instance = get_docker_instance()
    if instance:
        print("Attached to existed instance " + instance)
        user = getpass.getuser()
        command = ['docker', 'exec', '-i', '-u', user, instance, '/bin/bash',  '-c', 'cd /workspace;' + cmd_line]
    else:
        print("New docker instance")
        command = ['/bin/bash', '-i', '-c', 'export HOSTNAME=%s; cd %s; docker-compose run --rm bash /bin/bash -i -c "%s"' % (socket.gethostname(), os.getcwd(), cmd_line)]
        
    p=subprocess.Popen(command, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    while p.poll() is None:
        c = p.stdout.read(1)
        sys.stdout.buffer.write(c)
        sys.stdout.flush()

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) < 4:
        base = "/var/fpwork/qrb378/gnb/"
        json_file = "uplane/build/l2_ps/build/compile_commands.json"
        dependency_filename = "dependency.txt"
        ignore_path = "uplane/L2-PS"
    else:
        base = sys.argv[1]
        json_file = sys.argv[2]
        dependency_filename = sys.argv[3]
        ignore_path = sys.argv[4] if len(sys.argv) >= 5 else None

    cur_name = os.path.abspath(__file__)
    os.chdir(base)
    fp = open(json_file)
    compile_commands = json.load(fp)
    if len(compile_commands) == 0:
        sys.exit(-1)

    directory = compile_commands[0]["directory"]
    result = subprocess.run(['uname', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    if directory.startswith('/workspace/') and result.split()[1] != 'l2l3image':
        # docker mode in linsee now, trigger docker command again
        docker_run([cur_name, "/workspace/", json_file, dependency_filename, ignore_path])
    else:
        # local mode
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), dependency_filename)
        parser = Parser(base, ignore_path)
        parser.do(compile_commands)
        result = open(output_file, "w+")
        result.write("\n".join(parser.all_files.get()) + "\n")
        result.close()
        print("All done.")
