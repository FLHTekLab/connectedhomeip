#
#    Copyright (c) 2021 Project CHIP Authors
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from chip.server import (
    GetLibraryHandle,
    NativeLibraryHandleMethodArguments,
    PostAttributeChangeCallback,
)

from chip.exceptions import ChipStackError

from ctypes import CFUNCTYPE, c_char_p, c_int32, c_uint8

import sys
import os

import textwrap
import string

from cmd import Cmd

import asyncio
import threading

app_loop = None
dev = None


async def power_on(is_on: bool):
    global app_loop

    if (is_on):
        print("Power On")
    else:
        print("Power Off")


async def adjust_level(level: int):
    global app_loop

    print(f"Adjust level to {level}")


def appworker(_loop):
    asyncio.set_event_loop(_loop)
    _loop.run_forever()

    print("RUNNING LOOP:::")
    print(asyncio.get_running_loop())
    print("RUNNING LOOP::: END")

    # Create device instance here and add into main loop
    # dev = tridonic("/dev/dali/daliusb-*", glob=True)
    # _loop.run_in_executor(None, dev.connect())


class AppMgrCmd(Cmd):
    def __init__(self, rendezvousAddr=None, controllerNodeId=0, bluetoothAdapter=None):
        self.lastNetworkId = None

        Cmd.__init__(self)

        Cmd.identchars = string.ascii_letters + string.digits + "-"

        if sys.stdin.isatty():
            self.prompt = "chip-flh-thermostat > "
        else:
            self.use_rawinput = 0
            self.prompt = ""

        AppMgrCmd.command_names.sort()

        self.historyFileName = os.path.expanduser("~/.chip-lighting-history")

        try:
            import readline

            if "libedit" in readline.__doc__:
                readline.parse_and_bind("bind ^I rl_complete")
            readline.set_completer_delims(" ")
            try:
                readline.read_history_file(self.historyFileName)
            except IOError:
                pass
        except ImportError:
            pass

    command_names = [
        "help"
    ]

    def parseline(self, line):
        cmd, arg, line = Cmd.parseline(self, line)
        if cmd:
            cmd = self.shortCommandName(cmd)
            line = cmd + " " + arg
        return cmd, arg, line

    def completenames(self, text, *ignored):
        return [
            name + " "
            for name in AppMgrCmd.command_names
            if name.startswith(text) or self.shortCommandName(name).startswith(text)
        ]

    def shortCommandName(self, cmd):
        return cmd.replace("-", "")

    def precmd(self, line):
        if not self.use_rawinput and line != "EOF" and line != "":
            print(">>> " + line)
        return line

    def postcmd(self, stop, line):
        if not stop and self.use_rawinput:
            self.prompt = "chip-flh-thermostat > "
        return stop

    def postloop(self):
        try:
            import readline

            try:
                readline.write_history_file(self.historyFileName)
            except IOError:
                pass
        except ImportError:
            pass

    def do_help(self, line):
        """
        help

        Print the help
        """
        if line:
            cmd, arg, unused = self.parseline(line)
            try:
                doc = getattr(self, "do_" + cmd).__doc__
            except AttributeError:
                doc = None
            if doc:
                self.stdout.write("%s\n" % textwrap.dedent(doc))
            else:
                self.stdout.write("No help on %s\n" % (line))
        else:
            self.print_topics(
                "\nAvailable commands (type help <name> for more information):",
                AppMgrCmd.command_names,
                15,
                80,
            )


@PostAttributeChangeCallback
def attributeChangeCallback(
    endpoint: int,
    clusterId: int,
    attributeId: int,
    xx_type: int,
    size: int,
    value: bytes,
):
    print("attributeChangeCallback params")
    print("endpoint :", endpoint)
    print("-"*100)
    print("clusterId :", clusterId)
    print("attributeId :", attributeId)
    print("xx_type :", xx_type)
    print("size :", size)
    print("value (raw):", value)
    print("value (list):", list(value))
    print("-"*100)
    print("")
    global app_loop
    if endpoint == 1:
        if clusterId == 6 and attributeId == 0:
            if len(value) == 1 and value[0] == 1:
                print("[PY] Power on")
                # future = asyncio.run_coroutine_threadsafe(
                #     power_on(True), app_loop)
                # future.result()
            else:
                print("[PY] Power off")
                future = asyncio.run_coroutine_threadsafe(
                    power_on(False), app_loop)
                future.result()
        elif clusterId == 8 and attributeId == 0:
            if len(value):
                print("[PY] level {}".format(value[0]))
                # future = asyncio.run_coroutine_threadsafe(
                #     adjust_level(value[0]), app_loop)
                # future.result()
            else:
                print("[PY] no level")
        else:
            print("="*100)
            print("[PY] [ERR] unhandled cluster {} or attribute {}".format(
                clusterId, attributeId))
            print("="*100)
            pass
    else:
        print("[PY] [ERR] unhandled endpoint {} ".format(endpoint))


class FlhApp:
    def __init__(self):
        self.chipLib = GetLibraryHandle(attributeChangeCallback)


if __name__ == "__main__":
    l = FlhApp()

    AMgrCmd = AppMgrCmd()
    print("Chip Device Shell")
    print()

    print("Starting async")
    threads = []
    app_loop = asyncio.new_event_loop()
    
    print("app_loop is :::")
    print(app_loop)
    print("app_loop is ::: END")

    t = threading.Thread(target=appworker, args=(app_loop,))
    threads.append(t)
    t.start()

    print("app_loop is now:::")
    print(app_loop)
    print("app_loop is now::: END")

    try:
        AMgrCmd.cmdloop()
    except KeyboardInterrupt:
        print("\nQuitting")

    sys.exit(0)
