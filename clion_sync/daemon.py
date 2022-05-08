import sys
import os
import logging
import queue
from Worker import Worker
from LocalMonitor import LocalMonitor
from RemoteMonitor import RemoteMonitor
from Rsync import Rsync

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class Daemon:
    def __init__(self, server, rsa_key, local, remote, target, postfix, message_box):
        if local[-1] != '\\':
            local += '\\'
        if remote[-1] != '/':
            remote += '/'

        self.dependency_file_name = target + "_dependency.txt"
        self.message_box = message_box
        self.message_queue = queue.Queue()
        self.rsync = Rsync(server, rsa_key, remote, local)
        self.remote = RemoteMonitor(server, rsa_key, remote, self.message_queue, target, postfix, logging, self.rsync)
        self.remote.setup_remote_env()
        self.remote.load_compile_command()
        self.local = LocalMonitor(local, self.remote.get_monitor_list(), self.message_queue, postfix, logging)
        self.worker = Worker(self.message_queue, self.local, self.remote, logging)
        
    def start_monitor(self):
        self.worker.monitor()
        self.remote.monitor()
        self.local.monitor()

    def stop_monitor(self):
        self.remote.stop()
        self.local.stop()
        self.worker.stop()

    def is_alive(self):
        return self.remote.is_alive()

    def generate_cmake(self):
        self.remote.json2cmake.generate_cmake(self.local.target_path)

    def update_dependency(self, fully = False):
        result = 'yes'
        full_path = self.local.target_path + self.dependency_file_name
        if os.path.isfile(full_path): #self.remote.is_dependency_existed():
            result = self.message_box("Dependency file is existed.\nWhat do you want to refresh it (Need much time)?", ['yes', 'no'])
        if result == "yes":
            self.remote.generate_external_dependency(full_path)
        if fully:
            self.remote.download_dependency(self.local.target_path)
        else:
            self.rsync.download_by_list(full_path)

    def show_message_box(self, fname):
        overwrite_mode = None
        skip_mode = None
        result = self.message_box(fname + " is existed.\nWhat do you want to do?", ['always overwrite', 'alway overwrite old', 'overwrite once', 'always skip', 'skip once'])
        if result == 'always overwrite':
            overwrite_mode = 'always'
        elif result == 'alway overwrite old':
            overwrite_mode = 'old'
        elif result == 'overwrite once':
            overwrite_mode = 'once'
        elif result == 'always skip':
            skip_mode = 'always'
        elif result == 'skip once':
            skip_mode = 'once'
        else:
            assert(False)
        return overwrite_mode, skip_mode

    def show_orphan_message_box(self, fname):
        mode = None
        result = self.message_box(fname + " is not existed on remote.\nDo you want to remove it?", ['always remove', 'remove this file', 'always keep', 'only keep this file'])
        if result == 'always remove':
            mode = 'always_remove'
        elif result == 'remove this file':
            mode = 'remove_once'
        elif result == 'always keep':
            mode = 'always_keep'
        elif result == 'only keep this file':
            mode = 'keep_once'
        else:
            assert(False)
        return mode


    def download_git(self):
        # if not self.local.rmdir(self.local.covert(".git")):
        #     raise Exception("Can't remove .git folder. Please remove it manually. Then download it again.")
        # self.remote.download_git(self.local.target_path)
        self.rsync.download_by_folder(".git", "--exclude=modules/*")

    def download(self):
        if not os.path.exists(self.local.target_path) or len(os.listdir(self.local.target_path)) == 0:
            os.makedirs(self.local.target_path, exist_ok=True)
            self.remote.download_full_code(self.local.target_path)
            self.update_dependency(True)
            self.remote.json2cmake.generate_cmake(self.local.target_path)
            return

        overwrite_mode  = None
        skip_mode  = None
        orphan_mode = None
        cover_str = ""
        for files in self.remote.all_valid_files():
            cur_path = self.local.covert(files['base'])
            local_files = os.listdir(cur_path) if os.path.isdir(cur_path) else []

            for f in files['files']:
                if f['name'] in local_files:
                    local_files.remove(f['name'])
                if f['size'] >= 0: # not a folder
                    rel_path = files['base'] + '/' + f['name']
                    sys.stdout.write(cover_str + '\rChecking ' + rel_path + '\r')
                    cover_str = ' '*(len(rel_path)+9)
                    local_path = self.local.covert(rel_path)
                    remote_path = self.remote.covert(rel_path)

                    overwrite_it = False
                    if os.path.exists(local_path):
                        s = os.stat(local_path)
                        if s.st_size != f['size']:
                            if overwrite_mode == None and skip_mode == None:
                                overwrite_mode, skip_mode = self.show_message_box(local_path)
                            if skip_mode:
                                # don't care about it.
                                if skip_mode == 'once':
                                    skip_mode = None
                            else:
                                if overwrite_mode == "always":
                                    overwrite_it = True
                                elif overwrite_mode == "old":
                                    overwrite_it = self.local.is_old(f)
                                elif overwrite_mode == "once":
                                    overwrite_it = True
                                    overwrite_mode = None
                    else:
                        overwrite_it = True

                    if overwrite_it:
                        self.remote.download(remote_path, local_path)
            # check the orphan
            for f in local_files:
                full_path = cur_path + '\\' + f
                if orphan_mode == None:
                    orphan_mode = self.show_orphan_message_box(full_path)
                remove_it = False
                if orphan_mode == "always_remove":
                    remove_it = True
                elif orphan_mode == "remove_once":
                    remove_it = True
                    orphan_mode = None
                elif orphan_mode == "keep_once":
                    orphan_mode = None
                
                if remove_it:
                    if os.path.isdir(full_path):
                        self.local.rmdir(full_path)
                    else:
                        self.local.remove(full_path)
                
        sys.stdout.write(cover_str + '\r')

    def upload(self):
        overwrite_mode  = None
        skip_mode  = None
        cover_str = ""
        for d in self.remote.get_monitor_list():
            for f in self.local.all_valid_files(self.local.covert(d)):
                sys.stdout.write(cover_str + '\rChecking ' + f['name'] + '\r')
                cover_str = ' '*(len(f['name'])+9)
                local_path = self.local.covert(f['name'])
                remote_path = self.remote.covert(f['name'])

                overwrite_it = False
                r = self.remote.is_same(remote_path, f['size'])
                if r == False:
                    if overwrite_mode == None and skip_mode == None:
                        overwrite_mode, skip_mode = self.show_message_box(remote_path)
                    if skip_mode:
                        # don't care about it.
                        if skip_mode == 'once':
                            skip_mode = None
                    else:
                        if overwrite_mode == "always":
                            overwrite_it = True
                        elif overwrite_mode == "old":
                            overwrite_it = self.remote.is_old(f)
                        elif overwrite_mode == "once":
                            overwrite_it = True
                            overwrite_mode = None
                elif r == None:
                    overwrite_it = True

                if overwrite_it:
                    self.remote.upload(local_path, remote_path)
        sys.stdout.write(cover_str + '\r')

if __name__ == "__main__":
    key_file = r'C:\Users\qrb378\.ssh\id_rsa'
    daemon = Daemon("hzlinb32.china.nsn-net.net", key_file, 'd:\\clion_sync\\gnb\\', "/var/fpwork/qrb378/gnb/", "L2PS", ".h;.hpp;.hxx;.c;.cpp;.cxx;.cc", None)
    # daemon.download()
    # daemon.start_monitor()
    # while True:
    #     time.sleep(10)
    # test_sftp()
