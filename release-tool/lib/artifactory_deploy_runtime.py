from lib.maven import Maven
from lib.commons import Commons

class DeployRuntime:

	def __init__(self, build_config):
		self.build_config = build_config
		self.commons = Commons(build_config)
		self.maven = Maven()

	def run(self):
		release_zip_file_path = self.commons.get_release_zip_file_path()
		artifact_id = self.commons.get_distribution_name_without_version() # reedelk-runtime-ce
		version = self.commons.get_runtime_version_from_pom() # 1.0.3-SNAPSHOT
		repository_id = self.build_config['mavenRepositoryId']
		repository_url = self.build_config['mavenRepositoryUrl']
		maven_command = 'mvn deploy:deploy-file -DgroupId=com.reedelk \
				-DartifactId=' + artifact_id + '\
  				-Dversion=' + version + ' \
  				-DgeneratePom=false \
  				-Dpackaging=zip \
  				-Dfile=' + release_zip_file_path + ' \
  				-DrepositoryId=' + repository_id + ' \
  				-Durl=' + repository_url
		self.maven.run_command(maven_command)
