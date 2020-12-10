from lib.commons import Commons
from pathlib import Path
from shutil import copyfile
import re

RELEASES_JSON_FILE = 'releases.json'

class ReleaseNotes:

	def __init__(self, build_config):
		self.build_config = build_config
		self.commons = Commons(build_config)

	def run(self):
		sources_dir = self.build_config['sourcesDir']
		website_backend_assets = self.build_config['websiteBackendDir']
		self.copy_modules_releases(sources_dir, website_backend_assets)
		self.copy_runtime_releases(sources_dir, website_backend_assets)

	def copy_runtime_releases(self, sources_dir, website_backend_assets):
		version_qualfier = self.build_config['versionQualifier'].lower()
		runtime_dir = 'runtime-' + version_qualfier
		src = Path(sources_dir) / 'reedelk-runtime' / RELEASES_JSON_FILE
		dst = Path(website_backend_assets) / runtime_dir / RELEASES_JSON_FILE
		self.copy(src, dst)

	def copy_modules_releases(self, sources_dir, website_backend_assets):
		module_names = self.commons.extract_module_names()
		for module_name in module_names:
			src = Path(sources_dir) / module_name / RELEASES_JSON_FILE
			dst = Path(website_backend_assets) / 'module' / module_name / RELEASES_JSON_FILE
			self.copy(src, dst)

	def copy(self, src, dst):
		copyfile(src, dst)
		print('Copied src=[' + str(src) + '] to dst=[' + str(dst) + ']')
