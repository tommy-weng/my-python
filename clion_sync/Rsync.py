import subprocess
import os

class Rsync:
    def __init__(self, server, rsa_key, remote, local):
        self.rsa_key = self._window_path_to_cygpath(rsa_key)
        self.rsync_tool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cwrsync", "bin")
        self._trans_remote_path = lambda sub_path : server + ":" + remote + sub_path
        self._trans_local_path = lambda sub_path : self._window_path_to_cygpath(local) + sub_path
        self.rsync_cmd_template = '%s/rsync -Pa {} -e "%s/ssh -o StrictHostKeyChecking=no -i %s"' % (
            self.rsync_tool_path, 
            self._window_path_to_cygpath(self.rsync_tool_path),
            self.rsa_key)
    
    def _window_path_to_cygpath(self, path):
        driver = path[0]
        return "/cygdrive/" + driver + path[2:].replace("\\", "/")

    def download_by_folder(self, folder, options=""):
        self._download(options, folder.replace("\\", "/") + "/*", folder)

    def upload_by_folder(self, folder, options=""):
        self._upload(options, folder + "/*", folder.replace("\\", "/"))

    def download_by_list(self, file_list):
        new_path = self._window_path_to_cygpath(file_list)
        self._download("--files-from=" + new_path, "", "")

    def upload_by_list(self, file_list):
        new_path = self._window_path_to_cygpath(file_list)
        self._upload("--files-from=" + new_path, "", "")

    def _download(self, options, remote, local):
        cmd = self.rsync_cmd_template.format(options) + " " + self._trans_remote_path(remote) + " " + self._trans_local_path(local)
        subprocess.check_call(cmd)
        print("download completed.")

    def _upload(self, options, local, remote):
        cmd = self.rsync_cmd_template.format(options) + " " + self._trans_local_path(local) + " " + self._trans_remote_path(remote)
        subprocess.check_call(cmd)
        print("upload completed.")

if __name__ == '__main__':
    rsync = Rsync("hzlinb32.china.nsn-net.net", r"C:\Users\qrb378\.ssh\id_rsa", "/var/fpwork/qrb378/gnb/", "d:\\l2ps\\", "")
    rsync.download_by_folder(".git", "--exclude=modules/*")
    rsync.download_by_list(r"D:\l2ps\L2PS_dependency.txt")
