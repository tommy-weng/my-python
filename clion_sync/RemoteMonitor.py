import paramiko
import sys
import os
import threading
import select
from Json2CMake import Json2CMake
import json
import tarfile
import zipfile
import stat

target_mapping = {
    "L2PS" : {
        "json_path" : "l2_ps/build",
        "source" : ["uplane/L2-PS"]
    },
    "L2PS_UT" : {
        "json_path" : "l2_ps/ut_build",
        "source" : ["uplane/L2-PS"]
    },
    "L2PS_SCT" : {
        "json_path" : "tickler",
        "source" : ["uplane/sct"]
    },
    "L2LO" : {
        "json_path" : "l2_lo/rel_bbp/build_dir",
        "source" : ["uplane/L2-LO"]
    },
    "L2LO_UT" : {
        "json_path" : "l2_lo/ut/build_dir",
        "source" : ["uplane/L2-LO"]
    },
}

class RemoteMonitor:
    def __init__(self, host, key_file, remote_project_path, message_queue, target, postfix, logging, rsync):
        self.postfix = postfix.split(';')
        self.target = target
        self.host = host
        self.commands_file = 'uplane/build/%s/compile_commands.json' % (target_mapping[self.target]["json_path"])
        self.dependency_file_name = self.target + "_dependency.txt"
        self.logger = logging.getLogger('Remote')
        self.key = paramiko.RSAKey.from_private_key_file(key_file)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.load_system_host_keys()
        self.client.connect(self.host, port=22, pkey=self.key, timeout=1)
        self.sftp = self.client.open_sftp()
        self.home = self._check_output("echo $HOME") + "/.clion_remote_sync" # /home/qrb378/.clion_remote_sync
        self._exec_cmd("mkdir -p " + self.home)
        self.sftp.chdir(self.home)
        self.remote_project_path = remote_project_path
        self.message_queue = message_queue
        self.rsync = rsync

    def setup_remote_env(self):
        self.logger.info("Upload remote script...")
        base_path = os.path.dirname(os.path.abspath(__file__)) + '/remote'
        for f in os.listdir(base_path):
            if f.endswith('.py'):
                self.sftp.put(base_path + '/' + f, f)

        if self._exec_cmd('/usr/bin/python3 -c "import watchdog"') != 0:
            if self._exec_cmd("/usr/bin/python3 -m pip --proxy http://10.144.1.10:8080 install --user watchdog") != 0:
                raise Exception("Can't install watchdog on the LinSEE!")

    def _exec_cmd(self, cmd):
        channel = self.client.get_transport().open_session()
        channel.exec_command(cmd)
        f = channel.makefile_stderr()
        for chunk in f:
            self.logger.error('... ' + chunk.strip('\n'))
        return channel.recv_exit_status()

    def _check_output(self, cmd):
        stdout = self.client.exec_command(cmd)[1]
        return stdout.read().decode('utf-8').strip()

    def load_compile_command(self):
        self.json2cmake = Json2CMake(self.target, self.remote_project_path)
        local_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "compile_commands.json")
        try:
            self.sftp.get(self.remote_project_path + self.commands_file, local_path)
            fp = open(local_path)
            self.compile_commands = json.load(fp)
            self.json2cmake.load_commands_json(self.compile_commands)
            self.logger.info("Load " + self.commands_file + " successfully.")
        except FileNotFoundError:
            raise Exception("Can't find %s, please build the target at first." % (self.commands_file))

        fp = self.sftp.open(self.home + '/clion_sync_list.txt', 'w')
        fp.write("\n".join(target_mapping[self.target]["source"]) + '\n')
        fp.close()

    def generate_external_dependency(self, full_path):
        source_paths = "" if self.target == 'L2PS_SCT' else ",".join(target_mapping[self.target]["source"])
        cmd = "cd %s;/usr/bin/python3 generate_dependency.py %s %s %s %s 2>&1" % (
            self.home, 
            self.remote_project_path, 
            self.commands_file,
            self.dependency_file_name,
            source_paths)
        self._exec_cmd_with_ouput(cmd)
        self.download(self.home + "/" + self.dependency_file_name, full_path)

    def _exec_cmd_with_ouput(self, cmd):
        transport = self.client.get_transport()
        channel = transport.open_session()
        channel.get_pty()
        f = channel.makefile()
        channel.exec_command(cmd)
        while f:
            chunk = f.read(1024).decode('utf-8')
            if chunk == '':
                break
            sys.stdout.write(chunk)
            sys.stdout.flush()

    def get_monitor_list(self):
        return target_mapping[self.target]["source"]

    def is_dependency_existed(self):
        try:
            self.sftp.stat(self.dependency_file_name)
            return True
        except FileNotFoundError:
            return False

    def download_git(self, target_path):
        self.rsync.download_by_folder(".git", "--exclude=modules/*")

    def download_full_code(self, target_path):
        if self.target != 'L2PS_SCT':
            self._generate_source_code_list("clion_sync_file_list.txt")
            self._package_download_extact(self._package_list_file, "clion_sync_file_list.txt", target_path)

    def _generate_source_code_list(self, list_name):
        self.logger.info("Generate full source code tgz package...")
        files_filter = " -or ".join(["-name '*%s'" % (a) for a in self.postfix])
        self._exec_cmd("cd %s; while IFS= read -r line; do find -L $line %s; done < ~/.clion_remote_sync/clion_sync_list.txt > ~/.clion_remote_sync/%s" % (self.remote_project_path, files_filter, list_name))


    def download_dependency(self, target_path):
        self._package_download_extact(self._package_list_file, self.dependency_file_name, target_path)
        if self.target == "L2PS_SCT":
            self._fix_absolute_including(target_path)
    
    def _package_download_extact(self, package_method, param, target_path):
        package_name = package_method(param)
        self._download_package(target_path, package_name)
        self._extact_package(package_name)

    def _fix_absolute_including(self, target_path):
        case_folder = target_path + '/uplane/build/tickler/cpp_testsuites'
        unix_path_style = target_path.replace('\\', '/')
        for root, dirs, files in os.walk(case_folder, topdown=False):
            for name in files:
                if name.endswith(".hxx") or name.endswith(".hpp") or name.endswith(".cxx") or name.endswith(".cpp"):
                    fullpath = os.path.join(root, name)
                    new_lines = []
                    has_change = False
                    for l in open(fullpath):
                        if self.remote_project_path in l:
                            l = l.replace(self.remote_project_path, unix_path_style)
                            has_change = True
                        new_lines.append(l)
                    if has_change:
                        f = open(fullpath, "w")
                        f.writelines(new_lines)

    def _package_list_file(self, list_name):
        self.logger.info("Package remote %s ..." % (list_name))
        #self._exec_cmd("cd %s; tar -chzf tmp.tar.gz -T %s/%s" % (self.remote_project_path, self.home, list_name))
        self._exec_cmd("cd %s; cat %s/%s | zip -@ tmp" % (self.remote_project_path, self.home, list_name))
        return "tmp.zip"

    def _download_package(self, target_path, package_name):
        self.logger.info("Downloading the package file...")
        os.chdir(target_path)
        def progress(recv, total):
            percent = int(recv * 100 / total)
            sys.stdout.write("[%s>%s] %s%%\r" % ("="*percent, " "*(100-percent), percent))
        self.sftp.get(self.remote_project_path + package_name, package_name, progress)
        sys.stdout.write("\n")

    def _extact_package(self, package_name):
        self.logger.info("Extract %s locally..." % (package_name))
        with zipfile.ZipFile(package_name) as f:
            f.extractall()
            f.close()
        os.remove(package_name)
        self._exec_cmd("cd %s; rm -f %s" % (self.remote_project_path, package_name))

    def all_valid_files(self):
        monitor_list = self.get_monitor_list()
        for f in monitor_list:
            yield from self._recursive_list_files(self.remote_project_path + f)
    
    def _recursive_list_files(self, basefolder):
        n_strip = len(self.remote_project_path)
        try:
            result = {"base":basefolder[n_strip:], "files":[]}
            for f in self.sftp.listdir_attr(basefolder):
                fullpath = basefolder + '/' + f.filename
                if stat.S_ISDIR(f.st_mode):
                    result['files'].append({'name':f.filename, 'size':-1, 'mtime':f.st_mtime})
                    yield from self._recursive_list_files(fullpath)
                elif stat.S_ISLNK(f.st_mode) and stat.S_ISDIR(self.sftp.stat(fullpath).st_mode):
                    result['files'].append({'name':f.filename, 'size':-1, 'mtime':f.st_mtime})
                    yield from self._recursive_list_files(fullpath)
                else:
                    for postfix in self.postfix:
                        if f.filename.endswith(postfix):
                            result['files'].append({'name':f.filename, 'size':f.st_size, 'mtime':f.st_mtime})
                            break
            yield result
        except FileNotFoundError:
            pass

    def monitor(self):
        self.running = True
        self.ready_event = threading.Event()
        threading.Thread(target=self._worker, daemon=True).start()
        self.ready_event.wait()

    def stop(self):
        self.running = False

    def _worker(self):
        transport = self.client.get_transport()
        channel = transport.open_session()
        channel.exec_command('/usr/bin/python3 %s/monitor.py %s %s/clion_sync_list.txt "%s" 2>&1' % (self.home, self.remote_project_path, self.home, ";".join(self.postfix)))
        output = ""
        while self.running:
            rl, wl, xl = select.select([channel],[],[],2.0)
            if len(rl) > 0:
                try:
                    output += channel.recv(1024).decode('utf-8')
                    while True:
                        pos = output.find('\n')
                        if pos < 0:
                            break
                        line = output[0:pos]
                        if line.startswith('>'):
                            self.logger.debug(line)
                            self.message_queue.put("remote:" + line[1:])
                        else:
                            self.logger.info(line)
                            if line == 'observer is ready':
                                self.ready_event.set()
                        output = output[pos+1:]
                except UnicodeDecodeError as err:
                    pass
                if rl[0].closed:
                    break
        channel.close()
        if self.running: # abnormal exit
            # reconnect
            self.logger.warn("SSH disconnected abnormal. Try to reconnect it...")
            self.client.connect(self.host, port=22, pkey=self.key, timeout=1)
            self.sftp = self.client.open_sftp()
            self.sftp.chdir(self.home)
            self.monitor()
            self.logger.info("Reconnect succeed.")

    def covert(self, fname):
        return self.remote_project_path + fname.replace('\\', '/')

    def remove(self, fname):
        self.logger.info("remove " + fname)
        try:
            self.sftp.remove(fname)
        except FileNotFoundError as err:
            self.logger.info("remove failed : %s" % (err))
            pass

    def upload(self, src_name, dst_name):
        self.logger.info("upload %s -> %s" % (src_name, dst_name))
        self._exec_cmd('mkdir -p "%s"' % (os.path.dirname(dst_name)))
        self.sftp.put(src_name, dst_name)
        s = os.stat(src_name)
        self.sftp.utime(dst_name, (s.st_atime, s.st_mtime))

    def download(self, src_name, dst_name):
        self.logger.info("download %s -> %s" % (src_name, dst_name))
        try:
            os.makedirs(os.path.dirname(dst_name), exist_ok=True)
            self.sftp.get(src_name, dst_name)
            s = self.sftp.stat(src_name)
            os.utime(dst_name, times=(s.st_atime, s.st_mtime))
        except FileNotFoundError as err:
            pass
    
    def stat(self, fname):
        try:
            return self.sftp.stat(fname)
        except IOError:
            return None

    def rmdir(self, src_path):
        self.logger.info("rmdir %s" % (src_path))
        try:
            self._exec_cmd('rm -rf "%s"' %(src_path))
        except IOError:
            pass

    def move(self, src_path, dst_path):
        self.logger.info("move %s -> %s" % (src_path, dst_path))
        ret = self._exec_cmd('mv "%s" "%s"' %(src_path, dst_path))
        if ret != 0:
            self.logger.error('mv "%s" failed.' % (src_path))

    def is_old(self, fattr):
        target_fname = self.covert(fattr['name'])
        s = self.sftp.stat(target_fname)
        return s.st_mtime < fattr['mtime']

    def is_same(self, fname, fsize):
        try:
            s = self.sftp.stat(fname)
            return s.st_size == fsize
        except IOError:
            return None

    def is_alive(self):
        transport = self.client.get_transport() if self.client else None
        return transport and transport.is_active() 
