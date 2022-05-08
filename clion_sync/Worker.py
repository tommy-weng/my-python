import threading, queue
import stat
from datetime import datetime, timedelta
import os

class Worker:
    def __init__(self, message_queue, local, remote, logging):
        self.logger = logging.getLogger('Worker')
        self.message_queue = message_queue
        self.local = local
        self.remote = remote
        self.event_queue = {}
        self.pre_action = {'deleted':{}, 'modified':{}, 'moved':{}}

    def monitor(self):
        self.running = True
        threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False

    def _worker(self):
        while self.running:
            try:
                msg = self.message_queue.get(timeout=1)
                self.event_queue[msg] = datetime.now()
                self.message_queue.task_done()
            except queue.Empty:
                pass
            self._loop_event_queue()

    def _loop_event_queue(self):
        all_messages = list(self.event_queue.keys())
        for msg in all_messages:
            if datetime.now() - self.event_queue[msg] >= timedelta(seconds=1):
                self._handle_msg(msg)
                del self.event_queue[msg]

    def _handle_msg(self, msg):
        self.logger.debug(msg)

        words = msg.split(':')
        if words[0] == 'local':
            source_agent = self.local
            work_agent = self.remote
        else:
            source_agent = self.remote
            work_agent = self.local
        source_path = source_agent.covert(words[3])
        work_path = work_agent.covert(words[3])

        if words[1] == 'created':
            # don't need to consider the empty folder create
            if words[2] == 'F':
                self._modified_file(source_agent, work_agent, source_path, work_path)
        elif words[1] == 'moved':
            new_work_path = work_agent.covert(words[4])
            if work_agent.stat(work_path) != None:
                self._moved(work_agent, source_path, work_path, new_work_path)
            else:
                # can't rename it, then download it directly.
                self._modified_file(source_agent, work_agent, source_agent.covert(words[4]), new_work_path)

        elif words[1] == 'deleted':
            self._delete(work_agent, source_path, work_path)
        elif words[1] == 'modified':
            if words[2] == 'F': # file
                self._modified_file(source_agent, work_agent, source_path, work_path)
            else:
                # folder
                if words[0] == 'remote' and words[3] == ".git" and os.path.isdir(work_path):
                    self.remote.download_git(words[3])

    def _moved(self, work_agent, source_path, work_path, new_work_path):
        s_pos = max(work_path.rfind(i) for i in "\\/")
        t_pos = max(new_work_path.rfind(i) for i in "\\/")
        if work_path[s_pos+1:] == new_work_path[t_pos+1:]:
            # it's just caused by the parent folder rename action
            return
        if not self._is_pre_action_result("moved", source_path, work_path):
            work_agent.move(work_path, new_work_path)
    
    def _delete(self, agent, src_path, dst_path):
        if not self._is_pre_action_result("deleted", src_path, dst_path):
            s = agent.stat(dst_path)
            if s:
                if stat.S_ISDIR(s.st_mode):
                    agent.rmdir(dst_path)
                else:
                    agent.remove(dst_path) 

    def _modified_file(self, source_agent, work_agent, source_path, work_path):
        if not self._is_pre_action_result("modified", source_path, work_path):
            if work_agent == self.local:
                self.remote.download(source_path, work_path)
            else:
                self.remote.upload(source_path, work_path)

    def _is_pre_action_result(self, action, src_path, dst_path):
        if src_path in self.pre_action[action]:
            self.pre_action[action][src_path] -= 1
            if self.pre_action[action][src_path] == 0:
                del self.pre_action[action][src_path]
            return True
        else:
            if dst_path in self.pre_action[action]:
                self.pre_action[action][dst_path] += 1
            else:
                self.pre_action[action][dst_path] = 1
            return False
