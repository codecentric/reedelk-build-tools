import os
import sys
import stat
import zipfile
from lib.commons import Commons
from lib.maven import Maven
from pathlib import Path
from shutil import rmtree
from shutil import copyfile
from shutil import copytree, ignore_patterns

class Build:

	def __init__(self, build_config):
		self.build_config = build_config
		self.commons = Commons(build_config)
		self.maven = Maven()

	def run(self):
		# Create distribution directory
		self.create_distribution_dir()

		# Build the project: simulation (install only) otherwise deploy on artifactory
		if self.build_config['simulation']:
			self.simulation()
		else:
			self.release()

		# Prepare release directories
		[release_dir,bin_dir,logs_dir,modules_dir,config_dir, lib_dir] = self.prepare_release_directories()

		# Copy assets
		self.copy_start_sh(release_dir)
		self.copy_start_bat(release_dir)
		self.copy_modules(modules_dir)
		self.copy_runtime_into_bin(bin_dir)
		self.copy_config_directory(config_dir)
		self.copy_lib_directory(lib_dir)

		# Zip all with version
		self.zip_distribution(release_dir)

		return self.commons.get_release_zip_file_path()

	def release(self):
		print("Release (deploy and package)")
		success = self.maven_deploy()
		if not success:
			print('Release aborted. Maven deploy was not successful.')
			sys.exit()

	def simulation(self):
		print("Release simulation (install and package)")
		success = self.maven_install()
		if not success:
			print('Release aborted. Maven install was not successful.')
			sys.exit()

	def prepare_release_directories(self):
		release_dir = self.commons.get_release_directory()
		bin_dir = str(Path(release_dir) / 'bin') # NAME_CONVENTION
		lib_dir = str(Path(release_dir) / 'lib') # NAME_CONVENTION
		logs_dir = str(Path(release_dir) / 'logs') # NAME_CONVENTION
		modules_dir = str(Path(release_dir) / 'modules') # NAME_CONVENTION
		config_dir = str(Path(release_dir) / 'config') # NAME_CONVENTION
	
		directories_to_create = [bin_dir, lib_dir, logs_dir]
		[self.make_dir(dir) for dir in directories_to_create]
	
		all_directories = [bin_dir, logs_dir, modules_dir, config_dir, lib_dir]
		return [release_dir] + all_directories

	def copy_start_sh(self, release_dir):
		start_sh_file = str(Path(self.get_current_dir()).parent / 'runtime-start.sh')
		release_dir_sh_file = str(Path(release_dir) / 'runtime-start.sh')
		copyfile(start_sh_file, release_dir_sh_file)
		os.chmod(release_dir_sh_file, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

	def copy_start_bat(self, release_dir):
		start_bat_file = str(Path(self.get_current_dir()).parent / 'runtime-start.bat')
		release_dir_bat_file = str(Path(release_dir) / 'runtime-start.bat')
		copyfile(start_bat_file, release_dir_bat_file)

	def copy_modules(self, target_modules_directory):
		excluded_files = ['*.lic','.gitignore','.DS_Store','.gitignore']
		excluded_modules = self.build_config['excludedDistributionModules']
		exclusions = excluded_files + excluded_modules
		modulesDirectory = str(Path(self.get_launcher_directory()) / 'modules')
		copytree(modulesDirectory, target_modules_directory, ignore=ignore_patterns(*exclusions))

	def copy_config_directory(self, target_config_directory):
		configDirectory = str(Path(self.get_launcher_directory()) / 'config')
		# We MUST not copy the license file when we perform a release. 
		# Therefore any .lic file from config folder will not be copied.
		# The same applies for any .gitignore and .DS_Store.
		copytree(configDirectory, target_config_directory, ignore=ignore_patterns('*.lic','.gitignore','.DS_Store','.gitignore'))

	def copy_lib_directory(self, target_lib_directory):
		# We copy only the README.md
		sourceReadme = str(Path(self.get_launcher_directory()) / 'lib' / 'README.md')
		targetReadme = str(Path(target_lib_directory) / 'README.md')
		copyfile(sourceReadme, targetReadme)

	def copy_runtime_into_bin(self, target_bin_directory):
		jar_name = 'runtime.jar'
		runtime_name = Path(self.get_launcher_directory()) /'target' / jar_name
		target_runtime_name = str(Path(target_bin_directory) / jar_name)
		copyfile(str(runtime_name), target_runtime_name)
	
	def zip_distribution(self, release_dir):
		release_directory = self.commons.get_release_directory()
		zip_name = self.commons.get_release_zip_file_path()
		self.zip_dir(release_dir, zip_name)

	def maven_install(self):
		return self.maven_build('install')

	def maven_deploy(self):
		return self.maven_build('deploy')

	def maven_build(self, command):
		version_qualifier = self.build_config['versionQualifier']
		additional_bundles = ''
		skip_tests = str(self.build_config['skipTests'])
		reedelk_openapi_pom = str(Path(self.build_config['sourcesDir']) / 'reedelk-openapi' / 'pom.xml')
		reedelk_runtime_pom = str(Path(self.build_config['sourcesDir']) / 'reedelk-runtime' / 'pom.xml')
		reedelk_modules_pom = str(Path(self.build_config['sourcesDir']) / 'modules' / 'pom.xml')
		reedelk_runtime_license_pom = str(Path(self.build_config['sourcesDir']) / 'runtime-license' / 'pom.xml')


        # Open API module
		clean_and_run = self.clean_and_run_maven_command(command, reedelk_openapi_pom, skip_tests, version_qualifier)
		if not clean_and_run:
			return False

		# Runtime
		clean_and_run = self.clean_and_run_maven_command(command, reedelk_runtime_pom, skip_tests, version_qualifier, additional_bundles)
		if not clean_and_run:
			return False

        # Modules
		return self.clean_and_run_maven_command(command, reedelk_modules_pom, skip_tests, version_qualifier)


	def clean_and_run_maven_command(self, command, pom, skipTests, version_qualifier, additional_bundles = ''):
		clean_successful = self.maven.maven_command('clean', pom)
		if not clean_successful:
			return False
		build_user = self.build_config['userName']
		return self.maven.maven_command(command + ' -DskipTests=' + skipTests + ' -Duser.name=' + build_user + ' -Dadditional.bundles=' + additional_bundles + ' -Dversion.qualifier=' + version_qualifier, pom)


	def create_distribution_dir(self):
		# Cleanup any existing distribution directory if exists
		self.remove_dir(self.build_config['distributionDir'])
		self.make_dir(self.build_config['distributionDir'])

	def remove_dir(self, target_dir):
		if os.path.exists(target_dir) and os.path.isdir(target_dir):
			rmtree(target_dir)

	def make_dir(self, target_dir):
		if not os.path.exists(target_dir):
			os.makedirs(target_dir)

	def get_current_dir(self):
		return os.path.dirname(os.path.realpath(__file__))

	def get_launcher_directory(self):
		return Path(self.build_config['sourcesDir']) / 'reedelk-runtime' / 'runtime-launcher'

	def zip_dir(self, directory, zipname):
		if os.path.exists(directory):
			outZipFile = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)
    		# The root directory within the ZIP file.
			rootdir = os.path.basename(directory)
			for dirpath, dirnames, filenames in os.walk(directory):
				for filename in filenames:
					# Write the file named filename to the archive,
					# giving it the archive name 'arcname'.
					filepath   = os.path.join(dirpath, filename)
					parentpath = os.path.relpath(filepath, directory)
					arcname    = os.path.join(rootdir, parentpath)
					outZipFile.write(filepath, arcname)
			outZipFile.close()
