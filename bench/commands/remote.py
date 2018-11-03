

# imports - system imports
import os
import sys
import json

from distutils.spawn import find_executable
from distutils.util import strtobool

# imports - third-party imports
import ast
import click
import subprocess

# imports - app imports
import bench



@click.command('remote')
@click.argument('command', nargs=-1, required=True)
@click.option('--server', required=True, help='IP address/Domain name of the server which hosts your bench instance')
@click.option('--site', help='The site for which you want the command to be executed')
@click.option('--port', default=22, help='The SSH port of the server. Default: 22')
@click.option('--user', default='frappe', help='The user under which frappe is installed. Default: frappe')
@click.option('--path-to-bench', default='frappe-bench', help='The path to the frappe-bench instance as is from the home folder of the user. Default: frappe-bench')
@click.option('--sudo', default=False, is_flag=True, help='Execute the command as sudo')
def remote(command, server, site=None, port=22, user='frappe', path_to_bench='frappe-bench', sudo=False):
	"""
	Execute bench commands on a remote instance 

	CLI command: bench remote COMMAND [OPTION]

	Parameters:

		command (str): The command to be executed on the remote instance

	Returns:

		Prints the ansible output

	Examples:

		bench remote update --server 'frappe.erpnext.com'

		bench remote setup requirements --server 'frappe.erpnext.com'

		bench remote build --server 'frappe.erpnext.com'

		bench remote migrate --site 'frappe.io' --server 'frappe.erpnext.com'

	"""
	# Format the command
	command = ' '.join(command)
	command = '{sudo}bench {site}{command}'.format(
		sudo = 'sudo ' if sudo else '',
		site = '--site {} '.format(site) if site else '',
		command = command
	)
	print ('\nServer: ', server)
	print ('Command: ', command)

	try:
		proceed = strtobool(input('\nProceed? [Y/n]: '))
	except:
		proceed = True

	if not proceed: sys.exit()

	extra_vars = {
		'server': server,
		'command': command,
		'port': port,
		'user': user,
		'path_to_bench': path_to_bench
	}
	run_playbook('remote.yml', extra_vars=extra_vars)


def run_playbook(remote_playbook_name, extra_vars=None):
	if not find_executable('ansible'):
		print ("Installing ansible ...")
		from subprocess import check_output
		env_path = os.path.join(sys.prefix, 'bin', 'pip')
		check_output('{} install ansible'.format(env_path), shell=True)
		print ("Installed ansible!")

	import ansible

	args = ['ansible-playbook', remote_playbook_name, '-i', "{}:{},".format(extra_vars['server'], extra_vars['port'])]

	if extra_vars:
		args.extend(['-e', json.dumps(extra_vars)])

	print (args)

	subprocess.check_call(args, cwd=os.path.join(os.path.dirname(bench.__path__[0]), 'bench', 'commands'))
