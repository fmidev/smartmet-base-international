# smartmet-base-international

## How to do release
- every push to master build the rpm, test that build works
- change version and version history in spec file
- create new tag, make sure that spec file has same version: git tag v2024.11.25-1
- push tags to origin: git push origin --tags