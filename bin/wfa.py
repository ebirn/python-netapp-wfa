#!/usr/bin/env python3

import cmd, sys

# or maybe use drop-in replacement cmd2:
# https://pypi.python.org/pypi/cmd2

# to make tab completion platform independent... meh.
import readline
if 'libedit' in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

class WFAShell(cmd.Cmd):
    intro = 'Welcome to the NetApp OnCommand Workflow Automation (WFA) shell.\n  Type help or ? to list commands.\n'
    prompt = 'wfa> '

    def __init__(self):
        super(WFAShell, self).__init__()
        self.WORKFLOW_ACTIONS = ['list', 'execute', 'status', 'end', 'show']

    def do_workflow(self, arg):
        'workflow subcommand help text'
        self.prompt = 'wfa: workflow> '
        print('arg: %s' % arg)

    def do_top(self, arg):
        ' go to the toplevel command prompt'
        self.prompt = 'wfa> '

    def complete_workflow(self, text, line, begidx, endidx):
        if not text:
            completions = self.WORKFLOW_ACTIONS[:]
        else:
            completions = [ f for f in self.WORKFLOW_ACTIONS if f.startswith(text) ]
        return completions

    def quit(self):
        print('\nthank you for using WFA cmdline client')
        return True

    def do_exit(self, arg):
        'end the session'
        return self.quit()

    def do_quit(self, arg):
        'end the session'
        return self.quit()

    def do_bye(self, arg):
        'end the session'
        return self.quit()

    def do_EOF(self, line):
        ''
        return self.quit()


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    shell = WFAShell()

    # single line command
    if len(sys.argv) > 1:
        shell.onecmd(' '.join(sys.argv[1:]))
    # interactive mode
    else:
        shell.cmdloop()