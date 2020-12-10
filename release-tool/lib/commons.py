from pathlib import Path
import os
import re

class Commons:

	def __init__(self, build_config):
		self.build_config = build_config

	def get_release_zip_distribution_name(self):
		return self.get_release_distribution_name() + '.zip'

	def get_distribution_name_without_version(self):
		release_dir_prefix = self.build_config['runtimeReleaseDirPrefix']
		qualifier = self.build_config['versionQualifier'].lower()
		return release_dir_prefix + qualifier

	def get_release_distribution_name(self):
		distribution_name_without_version = self.get_distribution_name_without_version()
		runtime_version_from_pom = self.get_runtime_version_from_pom()
		return distribution_name_without_version + '-' + runtime_version_from_pom

	def get_release_zip_file_path(self):
		distribution_dir = self.build_config['distributionDir']
		zip_distribution_name = self.get_release_zip_distribution_name()
		return os.path.join(distribution_dir, zip_distribution_name)

	def get_release_directory(self):
		release_distribution_name = self.get_release_distribution_name()
		distribution_dir = self.build_config['distributionDir']
		return os.path.join(distribution_dir, release_distribution_name)

	def get_runtime_version_from_pom(self):
		runtime_pom = Path(self.build_config['sourcesDir']) / 'reedelk-runtime' / 'pom.xml'
		with open (runtime_pom, 'r') as pom_content:
			content = pom_content.readlines()
			for line in content:
				searchObj = re.search(r'<revision>(.*)</revision>', line, re.M|re.I)
				if searchObj:
					return searchObj.group(1)
		return None

	def extract_module_names(self):
		# Extract all the modules from the superpom
		release_pom = str(Path(self.build_config['sourcesDir']) / 'modules' / 'pom.xml')
		modules = []
		with open (release_pom, 'r') as pom_content:
			content = pom_content.readlines()
			for line in content:
				searchObj = re.search(r'<module>(.*)</module>', line, re.M|re.I)
				if searchObj:
					# remove the leading ../
					value = searchObj.group(1)[3:]
					if value.startswith('module-'):
						modules.append(value)
		return modules