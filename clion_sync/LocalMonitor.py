import threading
from remote.monitor import Monitor
import os
import shutil

class LocalMonitor(Monitor):
    def __init__(self, target_path, monitor_files, message_queue, postfix, logging):
        super().__init__(target_path, monitor_files, postfix)
        self.logger = logging.getLogger('Local')
        self.message_queue = message_queue

    def _log(self, msg):
        self.logger.info(msg)
        if msg == 'observer is ready':
            self.ready_event.set()

    def _new_message(self, msg):
        msg = "local:" + msg
        self.logger.debug(msg)
        self.message_queue.put(msg)
    
    def monitor(self):
        self.running = True
        self.ready_event = threading.Event()
        threading.Thread(target=self.start, daemon=True).start()
        self.ready_event.wait()

    def stop(self):
        self.running = False

    def covert(self, fname):
        return os.path.join(self.target_path, fname.replace('/', '\\'))
    
    def remove(self, fname):
        self.logger.info("remove: " + fname)
        if os.path.exists(fname):
            os.remove(fname)

    def rmdir(self, src_path):
        self.logger.info("rmdir %s" % (src_path))
        try:
            if os.path.isdir(src_path):
                shutil.rmtree(src_path)
            return True
        except IOError as err:
            self.logger.warn("Can't remove this folder: %s" % (err))
            return False

    def move(self, src_path, dst_path):
        self.logger.info("move %s -> %s" % (src_path, dst_path))
        try:
            shutil.move(src_path, dst_path)
        except IOError:
            self.logger.error("can't find %s." % (src_path))

    def stat(self, fname):
        try:
            return os.stat(fname)
        except IOError:
            return None

    def is_old(self, fattr):
        target_fname = self.covert(fattr['name'])
        if os.path.exists(target_fname):
            s = os.stat(target_fname)
            return s.st_mtime < fattr['mtime']
        else:
            return True

    def all_valid_files(self, parent_path):
        n_strip = len(self.target_path)
        for root, dirs, files in os.walk(parent_path, topdown=False):
            for name in files:
                for postfix in self.postfix:
                    if name.endswith(postfix):
                        fullpath = os.path.join(root, name)
                        s = os.stat(fullpath)
                        yield {'name':fullpath[n_strip:], 'size':s.st_size, 'mtime':s.st_mtime}
