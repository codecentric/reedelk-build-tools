from subprocess import Popen, PIPE

class Maven:

	def maven_command(self, command, pom_file):
		cmd_maven = "mvn -f " + pom_file + ' ' + command
		success = False
		for line in self.run(cmd_maven):
			line_as_string = line.decode('utf-8').rstrip()
			print(line_as_string)
			if 'BUILD SUCCESS' in line_as_string:
				success = True
		return success
	
	def run_command(self, command):
		for line in self.run(command):
			line_as_string = line.decode('utf-8').rstrip()
			print(line_as_string)

	def run(self, command):
		process = Popen(command, stdout=PIPE, shell=True)
		while True:
			line = process.stdout.readline()
			if not line:
				break
			yield line