# -*- coding: utf-8 -*-
""" All the services supplied by tdd_common
:copyright: Nokia
:author: yao,yonna (NSN - CN/Hangzhou)
:contact: yonna.yao@nsn.com
"""
import binascii
import subprocess
import socket
import types
import os
import struct
import logging
import time
import sys


POWER_OFF_STATUS = '01020100A188'
POWER_ON_STATUS = '010201016048'
POWER_ON_CODE = {1: "01050000FF008C3A", 2: "01050001FF00DDFA",
                 3: "01050002FF002DFA", 4: "01050003FF007C3A",
                 5: "01050004FF00CDFB", 6: "01050005FF009C3B",
                 7: "01050006FF006C3B", 8: "01050007FF003DFB"}
POWER_OFF_CODE = {1: "010500000000CDCA", 2: "0105000100009C0A",
                  3: "0105000200006C0A", 4: "0105000300003DCA",
                  5: "0105000400008C0B", 6: "010500050000DDCB",
                  7: "0105000600002DCB", 8: "0105000700007C0B"}
CHECK_CODE = {1: "010200000001B9CA", 2: "010200010001E80A",
              3: "010200020001180A", 4: "01020003000149CA",
              5: "010200040001F80B", 6: "010200050001A9CB",
              7: "01020006000159CB", 8: "010200070001080B"}


class SocketClient(object):
    """Socket operation
    """

    def __init__(self, server_ip='127.0.0.1', server_port=4001):
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.DEBUG)
        self.is_conneted = False
        self.timeout = 5.0
        self.server_ip = server_ip
        self._log.info(self.server_ip)
        self.server_port = server_port
#         arglist = ["netstat", "-ano", "grep %s" % self.server_port]
#         sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         self._log.info(sp.stdout.readlines())

    def _is_server_port_free(self):
        port_info = str(self.server_ip) + ':' + str(self.server_port)
        self._log.info("Try to release port %s..." % (port_info))
        try:
            arglist = ["netstat", '-tulpn']
            sp = subprocess.Popen(args=arglist, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            netlist = sp.stdout.readlines()

            for netinfo in netlist:
                if port_info in netinfo:
                    pid = str(netinfo).split()[-1].split("/")[0]
            else:
                self._log.info("Port %s is free!" % port_info)
                return True

            if int(pid) == '-':
                self._log.info("Process pid is not valid,skip it.")
                return True
            if not str(pid).isdigit():
                self._log.warning("Port is obtained but decode PID info fail.")
                return False

            ret = os.system("ntsd -c q -p " + str(pid))
            if ret == 0:
                self._log.info("Kill PID %s and release %s successful!" % (pid, port_info))
                return True
            else:
                self._log.warning("Kill PID %s and release %s successful!" % (pid, port_info))
                return False
        except Exception, e:
            self._log.warning("Unknown error occur when check port %s,detail is %s!" % (port_info, str(e)))
            return False

    def open(self):
        """open socket connection
        """
        if self.is_conneted is True:
            self.close()
        try:
            self._is_server_port_free()
            self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.Socket.settimeout(self.timeout)
            self.Socket.connect((self.server_ip, self.server_port))
            self.is_conneted = True
            self._log.info("socket '%s:%s' is established!" % (self.server_ip, self.server_port))
            return True
        except Exception, e:
            self._log.warning("socket open fail, detail is %s" % e)
            return False

    def close(self):
        """Close socket connection
        """
        if self.is_conneted is True:
            self.Socket.close()
            self.is_conneted = False
        self._log.info("socket '%s:%s' is closed!" % (self.server_ip, self.server_port))

    def send(self, msg):
        """send socket command
        """
        marshalled = ""
        msg_all = binascii.a2b_hex(msg)
        if self.is_conneted is False:
            self._log.error("socket '%s:%s' is closed, send failure!" %
                            (self.server_ip, self.server_port))
            return False

        for msg in msg_all:
            if isinstance(msg, types.StringTypes) is False:
                marshalled += struct.pack("l", socket.htonl(msg))
            else:
                marshalled += msg
        try:
            self.Socket.send(marshalled)
            self._log.info("Socket send message %s success!" % msg)
            return True
        except Exception, e:
            self._log.warning("Socket send message fail, detail is %s!" % str(e))
            return False

    def receive(self, timeout=5, max_msg_size=4096):
        """receive socket return message
        """
        msg = ''
        try:
            self.Socket.settimeout(timeout)
            (msg, address) = self.Socket.recvfrom(max_msg_size)
        except Exception, e:
            self._log.warning("socket receive have error:%s" % str(e))
            msg = ''
        ret = binascii.b2a_hex(msg)
        self._log.info("Receive message-->%s" % ret)
        return ret


class FACOMCONTROL():
    """facom operation
    """

    def __init__(self, host, port):
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.DEBUG)
        self.host = host
        self.port = int(port)
        print "init..."
        if int(self.port) not in range(1, 9):
            raise Exception("Power Breaker Port %s is out of range[1~8]!" % self.port)

    def _send_command_to_powerbreak(self, set_cmd, check_cmd, status, interva):
        try:
            p_Socket = SocketClient(self.host)
            time.sleep(interva)
            if not p_Socket.open():
                return False
            if not p_Socket.send(set_cmd):
                return False
            p_Socket.receive()
            time.sleep(interva)
            if not p_Socket.send(check_cmd):
                return False
            ret_msg = p_Socket.receive()
            ret = True if str(status).upper() == str(ret_msg).upper() else False
            return ret
        except Exception, e:
            self._log.warning("exception error in process, detail is %s" % str(e))
        finally:
            if p_Socket:
                p_Socket.close()

    def _power_onoff(self, oper):
        """power off
        """
        check_cmd = CHECK_CODE[self.port]
        if oper == 'off':
            set_cmd = POWER_OFF_CODE[self.port]
            status = POWER_OFF_STATUS
        else:
            set_cmd = POWER_ON_CODE[self.port]
            status = POWER_ON_STATUS        
        cmd_interva = 1
        for try_time in ['1st', '2nd', '3rd']:
            self._log.info("%s(total 3) power %s" % (try_time, oper))
            self._log.info("set_cmd:%s, check_cmd:%s, status:%s" % (set_cmd, check_cmd, status))
            ret = self._send_command_to_powerbreak(set_cmd, check_cmd, status, cmd_interva)
            print "%s result: %s" % (oper, ret)
            if ret:
                return
            else:
                cmd_interva = 5
        else:
            raise Exception("Power %s fail" % oper)

    def power_on(self):
        """power on
        """
        self._power_onoff('on')

    def power_off(self):
        """power off
        """
        self._power_onoff('off')

if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print('usage: reboot_byfacom.py <facom ip> <port>')
        print('Example: reboot_byfacom.py 10.68.183.35 5')
        exit(1)
        
    host = sys.argv[1]
    port = sys.argv[2]
    print "trying to reboot %s:%s" % (host, port)
    pb=FACOMCONTROL(host,port)
    pb.power_off()
    time.sleep(5)
    pb.power_on()


