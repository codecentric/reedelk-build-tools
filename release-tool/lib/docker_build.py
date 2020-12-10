import os
from lib.commons import Commons
from subprocess import Popen, PIPE

DOCKER_IMAGE = 'FROM adoptopenjdk/openjdk11:x86_64-alpine-jre-11.0.6_10\n\
RUN apk add --no-cache bash && apk add --no-cache wget && wget -P /opt "${MAVEN_REPOSITORY_URL}com/reedelk/${DISTRIBUTION_WITHOUT_VERSION}/${VERSION}/${ZIP_DISTRIBUTION_NAME}" && cd /opt && unzip /opt/${ZIP_DISTRIBUTION_NAME} && mv ${DISTRIBUTION_WITH_VERSION} reedelk-runtime && echo -e \'#!/bin/bash\\n/opt/reedelk-runtime/runtime-start.sh $*\' > /usr/bin/runtime-start &&  chmod +x /usr/bin/runtime-start && echo -e \'admin.console.address=0.0.0.0\' > /opt/reedelk-runtime/config/configuration.properties\n\
EXPOSE 9988/tcp'

DOCKER_FILE_NAME = 'Dockerfile'

class DockerBuild:


	def __init__(self, build_config):
		self.build_config = build_config
		self.commons = Commons(build_config)

	def run(self):
		maven_repository_url = self.build_config['mavenRepositoryUrl']

		# reedelk-runtime-ce
		distribution_without_version = self.commons.get_distribution_name_without_version()
		# 1.0.2
		version = self.commons.get_runtime_version_from_pom()
		# reedelk-runtime-ce-1.0.2.zip
		distribution_zip_name = self.commons.get_release_zip_distribution_name()
		# reedelk-runtime-ce-1.0.2
		distribution_with_version = self.commons.get_release_distribution_name()

		docker_image = DOCKER_IMAGE.replace('${MAVEN_REPOSITORY_URL}', maven_repository_url)
		docker_image = docker_image.replace('${DISTRIBUTION_WITHOUT_VERSION}', distribution_without_version)
		docker_image = docker_image.replace('${VERSION}', version)
		docker_image = docker_image.replace('${ZIP_DISTRIBUTION_NAME}', distribution_zip_name)
		docker_image = docker_image.replace('${DISTRIBUTION_WITH_VERSION}', distribution_with_version)

		with open(DOCKER_FILE_NAME, "w") as dockerfile:
			dockerfile.write(docker_image)

		print('Building Docker image (' + version + ')')
		docker_build = 'docker build -t reedelk/' + distribution_without_version + ':' + version + ' .'
		self.run_command(docker_build)

		docker_push = 'docker push reedelk/' + distribution_without_version + ':' + version 
		self.run_command(docker_push)

		print('Building latest Docker image (' + version + ')')
		docker_build = 'docker build -t reedelk/' + distribution_without_version + ':latest .'
		self.run_command(docker_build)

		docker_push = 'docker push reedelk/' + distribution_without_version + ':latest'
		self.run_command(docker_push)
		
		
	def run_command(self, command):
		for line in self.run_docker(command):
			line_as_string = line.decode('utf-8').rstrip()
			print(line_as_string)

	def run_docker(self, command):
		process = Popen(command, stdout=PIPE, shell=True)
		while True:
			line = process.stdout.readline()
			if not line:
				break
			yield line