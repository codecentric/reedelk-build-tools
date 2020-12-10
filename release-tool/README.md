# Reedelk Integration Platform Release Tool

## Example build configuration file:

```
{
	"sourcesDir": "/Users/myuser/Desktop/reedelk-project",
	"distributionDir": "/Users/myuser/Desktop/reedelk-project/tools/release-tool/dist",
	"websiteBackendDir": "/Users/myuser/Desktop/reedelk-project-support/reedelk-website/reedelk-website-backend/src/main/resources/assets",
	"userName": "Reedelk",
	"skipTests": false,
	"simulation": true,
	"versionQualifier": "CE",
	"runtimeReleaseDirPrefix": "reedelk-runtime-",
	"mavenRepositoryId": "reedelk-release",
	"mavenRepositoryUrl": "http://repository.reedelk.com/release/",
	"excludedDistributionModules": [
		"module-aws-s3-*",
		....
	]
}
```

* sourcesDir: directory of the Reedelk project sources
* distributionDir: the target directory of the distribution build
* integrationTestsPom: pom of the integration tests project
* websiteBackendDir: directory of the website backend project
* userName: name of the user performing the build
* skipTests: if true maven tests are skipped. Note that integration tests will not be skipped.
* simulation: if true, the distribution will not be deployed on artifactory, no docker images created.
* versionQualifier: the qualifier of the distribution, it could be only: 'CE' (Community Edition) or 'EE' (Enterprise Edition)
* testLicense: path to a test license to be used during integration tests for 'EE' build.
* runtimeReleaseDirPrefix: prefix of the final distribution file
* mavenRepositoryId: id in the user's .m2/settings.xml of the release repository containin password.
* mavenRepositoryUrl: url of the target release repository
* excludedDistributionModules: the modules to be excluded from the Reedelk distribution package
""

## Usage


Community Edition
```
python3 release.py build-config-ce.json
```

Enterprise Edition
```
python3 release.py build-config-ee.json
```
