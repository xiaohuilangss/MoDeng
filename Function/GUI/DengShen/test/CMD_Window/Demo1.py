from cmd import Cmd
from sys import exit


class MyCmd(Cmd):
    def __init__(self):
        super(MyCmd, self).__init__()
        self.prompt = "->"

    def do_hello(self, args):
        print("Hello.")

    def help_hello(self, args):
        print("hello - print hello and do nothing more.")

    def do_exit(self, args):
        exit(0)


def main():
    mycmd = MyCmd()
    mycmd.cmdloop(intro="My Cmd Demo.")


if __name__ == "__main__":
  main()