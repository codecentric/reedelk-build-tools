from lib.commons import Commons
from pathlib import Path
from shutil import copyfile
import re

MODULE_DESCRIPTOR_FILE = 'module-descriptor.json'

class ModuleDescriptor:

	def __init__(self, build_config):
		self.build_config = build_config
		self.commons = Commons(build_config)

	def run(self):
		sources_dir = self.build_config['sourcesDir']
		website_backend_assets = self.build_config['websiteBackendDir']
		self.copy_modules_descriptors(sources_dir, website_backend_assets)
		self.copy_flow_control_descriptor(sources_dir, website_backend_assets)

	def copy_flow_control_descriptor(self, sources_dir, website_backend_assets):
		src = Path(sources_dir) / 'reedelk-runtime' / 'runtime-commons' / 'src' / 'main' / 'resources' / MODULE_DESCRIPTOR_FILE
		dst = Path(website_backend_assets) / 'module' / 'flow-control' / MODULE_DESCRIPTOR_FILE
		self.copy(src, dst)

	def copy_modules_descriptors(self, sources_dir, website_backend_assets):
		module_names = self.commons.extract_module_names()
		for module_name in module_names:
			src = Path(sources_dir) / module_name / 'src' / 'main' / 'resources' / MODULE_DESCRIPTOR_FILE
			dst = Path(website_backend_assets) / 'module' / module_name / MODULE_DESCRIPTOR_FILE
			self.copy(src, dst)

	def copy(self, src, dst):
		copyfile(src, dst)
		print('Copied src=[' + str(src) + '] to dst=[' + str(dst) + ']')
