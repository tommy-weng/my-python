import os
import re
import xml.etree.ElementTree as ET
import shutil

# /var/fpwork/qrb378/gnb/uplane/sdkuplane/prefix-root-list/asik-x86_64-ps_lfs-gcc9/toolchain/sysroots/x86_64-oesdk-linux/usr/bin/x86_64-pc-linux-gnu-g++ -dM -E -x c++ < /dev/null > x86_64-pc-linux-gnu-g++_macros.h
# /var/fpwork/qrb378/gnb/uplane/sdkuplane/prefix-root-list/asik-x86_64-ps_lfs-gcc9/toolchain/sysroots/x86_64-oesdk-linux/usr/bin/x86_64-pc-linux-gnu-gcc -dM -E -x < /dev/null > x86_64-pc-linux-gnu-gcc_macros.h
class Json2CMake:
    def __init__(self, target, remote_project_path):
        self.target = target
        self.remote_project_path= remote_project_path
        self.libs = {}
        self.extra_flags = ""
        self.extra_includes = [
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/{arch}/usr/include/c++/9.1.0",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/{arch}/usr/include/c++/9.1.0/x86_64-poky-linux",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/{arch}/usr/include",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/{arch}/usr/include/dpdk",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/x86_64-oesdk-linux/usr/lib/x86_64-poky-linux/gcc/x86_64-poky-linux/9.1.0/include",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/toolchain/sysroots/x86_64-oesdk-linux/usr/lib/x86_64-poky-linux/gcc/x86_64-poky-linux/9.1.0/include-fixed",
            "uplane/sdkuplane/prefix-root-list/{toolchain}/usr/include"
        ]

    def _process_params(self, is_cplusplus, directory, commandline_words):
        ret = "-nostdinc -nostdinc++ -undef -include ${CMAKE_CURRENT_SOURCE_DIR}/"
        ret += "x86_64-pc-linux-gnu-g++_macros.h" if is_cplusplus else "x86_64-pc-linux-gnu-gcc_macros.h"
        ret += " "
        include_method = None
        for w in commandline_words:
            if w[0:2] == '-I':
                include_path = w[2:]
                ret += self._handle_including(None, directory, include_path)
            elif w.startswith('--sysroot='):
                include_path = w[10:]
                ret += self._handle_including("--sysroot=", directory, include_path)
                if not self.extra_flags:
                    m = re.match(r'.*uplane/sdkuplane/prefix-root-list/(.*)/toolchain/sysroots/(.*)', w)
                    self.toolchain = m.group(1)
                    self.arch = m.group(2)
                    print("toolchain is " + self.toolchain)
                    print("arch is " + self.arch)
                    for include in self.extra_includes:
                        self.extra_flags += " -I${CMAKE_CURRENT_SOURCE_DIR}/" + include.format(toolchain=self.toolchain, arch=self.arch)
            elif w in ["-isystem", "-include"]:
                include_method = w + " "
            elif w == "-rdynamic":
                continue  # GCC 8.0 can't recongnize it.
            elif w.startswith('-march='):
                continue  #MINGW don't support it.
            elif w == 'rte_config.h':
                include_method = None
                continue # it's dpdk header file, ignore it
            else:
                if include_method:
                    ret += self._handle_including(include_method, directory, w)
                    include_method = None
                else:
                    ret += ' ' + w
        return ret

    def _handle_including(self, include_method, directory, include_path):
        if include_path == '.':
            include_path = directory
        elif include_path[0] != '/':
            include_path = directory + '/' + include_path
        
        if include_path.startswith(self.remote_project_path):
            include_path = include_path[len(self.remote_project_path):]

        if include_method:
            return ' %s${CMAKE_CURRENT_SOURCE_DIR}/%s' % (include_method, include_path)
        else:
            return ' -I${CMAKE_CURRENT_SOURCE_DIR}/' + include_path

    def load_commands_json(self, commands_json):
        for item in commands_json:
            if item['file'].endswith(".S"):
                continue
            if item['file'].endswith("cmake_pch.hxx.cxx"):
                continue
            if not item['file'].startswith(self.remote_project_path):
                # docker mode
                self.remote_project_path = "/workspace/"
            words = item['command'].split()
            tool = words.pop(0)
            c = words.pop()
            assert words.pop() == "-c" # -c
            o = words.pop()
            assert words.pop() == "-o"
            m = re.match(r'(.*)CMakeFiles/([^.]+)\.dir/(.+)\.o', o)
            if m:
                lib_name = m.group(1).replace('/', '_') + m.group(2)
                if lib_name not in self.libs:
                    is_cplusplus = item['file'].endswith('.cpp') or item['file'].endswith('.cxx') or item['file'].endswith('.cc')
                    self.libs[lib_name] = {'params':self._process_params(is_cplusplus, item['directory'], words), 'files':[]}
                # else:
                #     assert self.libs[lib_name]['params'] == self._process_params(item['directory'], words)
                source_file = self._handle_source(item['file'])
                if source_file not in self.libs[lib_name]['files']:
                    self.libs[lib_name]['files'].append(source_file)

    def _handle_source(self, source_file):
        source_file = source_file[len(self.remote_project_path):]
        return source_file
    
    def generate_cmake(self, path):
        src_path = os.path.dirname(os.path.abspath(__file__))
        for f in ["x86_64-pc-linux-gnu-g++_macros.h", "x86_64-pc-linux-gnu-gcc_macros.h"]:
            shutil.copyfile(os.path.join(src_path, f), os.path.join(path, f))
        fp = open(os.path.join(path, 'CMakeLists.txt'), "w")
        fp.write('''
cmake_minimum_required(VERSION 3.10)
set(CMAKE_C_COMPILER "gcc")
set(CMAKE_CXX_COMPILER "g++")
project(%s)

''' % (self.target))
        empty_libs = []
        for (name, info) in self.libs.items():
            valid_files = []
            for f in info['files']:
                if os.path.isfile(path + '/' + f):
                    valid_files.append("${CMAKE_CURRENT_SOURCE_DIR}/" + f)
                else:
                    print("Not find %s, skip it." % (f))
            if len(valid_files) > 0:
                fp.write("add_library(%s STATIC %s)\n" % (name, " ".join(valid_files)))
                fp.write('set_target_properties(%s PROPERTIES COMPILE_FLAGS "%s %s")\n' % (name, info['params'], self.extra_flags))
            else:
                empty_libs.append(name)
        fp.write("target_link_libraries(%s)\n" % (" ".join([k for k in self.libs.keys() if k not in empty_libs])))
        fp.close()
        print("CMakeLists.txt generated successfully for '%s'." % (self.target))
