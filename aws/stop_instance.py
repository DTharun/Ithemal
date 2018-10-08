#!/usr/bin/env python

import argparse
import subprocess

from instance_utils import format_instance, AwsInstance

# Ithemal runs on Python 2 mostly
try:
    input = raw_input
except NameError:
    pass

class InstanceKiller(AwsInstance):
    def __init__(self, identity, force):
        super(InstanceKiller, self).__init__(identity)
        self.force = force

    def kill_instances(self, instances_to_kill):
        if not instances_to_kill:
            return

        if not self.force:
            print('Will kill the following instance{}:'.format('s' if len(instances_to_kill) else ''))
            for instance in instances_to_kill:
                if isinstance(instance, str):
                    print(instance)
                else:
                    print(format_instance(instance))

            try:
                res = input('Proceed? (y/n) ')[0].lower()
            except KeyboardInterrupt:
                print('Not killing.')
                return

            if res != 'y':
                print('Not killing.')
                return False

        instance_ids = [instance if isinstance(instance, str) else instance['InstanceId'] for instance in instances_to_kill]
        args = ['aws', 'ec2', 'stop-instances', '--instance-ids'] + instance_ids
        subprocess.check_call(args)


def interactively_kill_instances(instance_killer):
    while True:
        instances = instance_killer.get_running_instances()
        if not instances:
            print('No instances to kill!')
            return

        print('Active instances:')
        for i, instance in enumerate(instances):
            print('{}) {}'.format(i + 1, format_instance(instance)))

        try:
            res = input('Enter a number to kill that instance, "a" to kill all, or "q" to exit: ')
        except KeyboardInterrupt:
            return
        except EOFError:
            return

        if res[0].lower() == 'q':
            return
        elif res[0].lower() == 'a':
            instance_killer.kill_instances(instances)
        else:
            try:
                index_to_kill = int(res)
            except ValueError:
                print('"{}" is not an integer.'.format(res))
                continue

            if index_to_kill < 1 or index_to_kill > len(instances):
                print('{} is not between 1 and {}.'.format(index_to_kill, len(instances) + 1))
                continue

            instance_to_kill = instances[index_to_kill - 1]

            instance_killer.kill_instances([instance_to_kill])


def kill_all_instances(instance_killer):
    instances = instance_killer.get_running_instances()
    if not instances:
        print('No instances to kill!')
        return

    instance_killer.kill_instances(instances)

def main():
    parser = argparse.ArgumentParser(description='Kill running AWS EC2 instances')
    parser.add_argument('-a', '--all', help='Kill all running instances by default', default=False, action='store_true')
    parser.add_argument('-f', '--force', help="Don't ask for confirmation", default=False, action='store_true')
    parser.add_argument('-i', '--identity', help='Key identity to filter by', default=None)
    parser.add_argument('instance_id', help='Instance IDs to manually kill', nargs='*', default=[])
    args = parser.parse_args()

    instance_killer = InstanceKiller(args.identity, args.force)

    if args.instance_id:
        instance_killer.kill_instances(args.instance_id)
    elif args.all:
        kill_all_instances(instance_killer)
    else:
        interactively_kill_instances(instance_killer)


if __name__ == '__main__':
    main()