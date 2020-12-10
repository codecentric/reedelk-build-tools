from lib.build import Build
from lib.docker_build import DockerBuild
from lib.artifactory_deploy_runtime import DeployRuntime
from lib.module_descriptor import ModuleDescriptor
from lib.release_notes import ReleaseNotes
import json
import sys
import traceback


def print_operation(title, build_config):
	print('--- ' + title + ' ---')
	print('Configuration: ' + str(build_config))
	print('--------------------------------------------')

def build_release(build_config):
	try:
		print_operation('Reedelk Integration Platform Build', build_config)
		build = Build(build_config)
		final_zip_distribution = build.run()
		print("Release success, release distribution: " + final_zip_distribution)
	except:
		traceback.print_exc()
		print("[RELEASE_ERROR]: Could not Build Reedelk runtime. Release will be stopped.")
		sys.exit()

def deploy_artifactory(build_config):
	try:
		print_operation('Reedelk Integration Platform Deploy Artifactory', build_config)
		deploy_runtime_dist = DeployRuntime(build_config)
		deploy_runtime_dist.run()
	except:
		print("[RELEASE_ERROR]: Could not successfully deploy to artifactory. This step will have to manually be performed.")

def copy_release_notes(build_config):
	try:
		print_operation('Reedelk Integration Platform Copy Release Notes', build_config)
		release_notes = ReleaseNotes(build_config)
		release_notes.run()
	except:
		print("[RELEASE_ERROR]: Could not successfully copy release notes to website backend. This step will have to manually be performed.")

def copy_module_descriptors(build_config):
	try:
		print_operation('Reedelk Integration Platform Copy Module Descriptor', build_config)
		module_descriptor = ModuleDescriptor(build_config)
		module_descriptor.run()
	except:
		print("[RELEASE_ERROR]: Could not successfully copy module descriptors to website backend. This step will have to manually be performed.")

def docker_image(build_config):
	try:
		print_operation('Reedelk Integration Platform Push Docker Image', build_config)
		docker_build = DockerBuild(build_config)
		docker_build.run()
	except:
		print("[RELEASE_ERROR]: Could not successfully create and push docker images. This step will have to manually be performed.")


# The first argument is the build configuration
arguments_length = len(sys.argv)
if arguments_length != 2:
	print('Usage: python3 release.py my-build-config.json')
	sys.exit()
build_config_file = sys.argv[1]

# Execute Release
with open(build_config_file) as json_file:
	# Read build config
	build_config = json.load(json_file)

	# Build Release
	build_release(build_config)

	# If it is a simulation we don't deploy on artifactory,
	# we don't copy over release notes and module descriptors
	# and don't push any docker image on Dockerhub.
	if not build_config['simulation']:
	
		# Deploy Runtime Release Distribution on Artifactory
		deploy_artifactory(build_config)

		# Release release notes
		copy_release_notes(build_config)

		# Module descriptor
		copy_module_descriptors(build_config)

		# Create and push docker image on Dockerhub
		docker_image(build_config)

