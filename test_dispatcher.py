import sys
import inspect


class CMD(object):
    cmd = None

    def __call__(self, *args):
        raise RuntimeError("Abstract command can not be called")


class CMDl(CMD):
    cmd = 'l'
    description = 'list something'

    def __call__(self, *args):
        print('list', ', '.join([str(arg) for arg in args]))


class CMDd(CMD):
    cmd = 'd'
    description = 'delete something'

    def __call__(self, *args):
        print('delete', ', '.join([str(arg) for arg in args]))


class Other(object):
    pass


class Dispatcher(object):
    class Command(object):
        def __init__(self, description, command):
            self.description = description
            self.command = command

    def __init__(self, base_class):
        self.commands = {}
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj) and issubclass(obj, base_class) and obj is not CMD:
                self.commands[obj.cmd] = Dispatcher.Command(obj.description, obj())

    def help(self):
        for cmd_name, cmd in self.commands.items():
            print(cmd_name, '---', cmd.description, cmd)

    def __call__(self, command_name, *args):
        cmd = self.commands[command_name]
        return cmd.command(*args)


if __name__ == '__main__':
    dispatcher = Dispatcher(CMD)
    dispatcher.help()
    dispatcher('l', 1, 2, 'a')
    dispatcher('d', 3, 4, 'b', 'c')
