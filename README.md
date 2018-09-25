# ModulemdTranslationHelpers
## Prerequisites
* [libmodulemd](https://github.com/fedora-modularity/libmodulemd)
* [koji](https://pagure.io/koji)

To install on Fedora 28+, run:
```
dnf install libmodulemd koji
```

## Installation
With the prerequisites installed, the latest version can be installed with
`pip install ModulemdTranslationHelpers` or on Fedora 28+ with `dnf install
python3-ModulemdTranslationHelpers` (recommended).

## CLI Usage

### Extract Translatable Strings
To extract translatable strings from modules for a particular Fedora
release (e.g. f29):
```
ModulemdTranslationHelpers --branch f29 extract [--pot-file <path>]
```
This will read all of the module metadata from the Koji build-system and
convert the translatable strings to a portable object template (`.pot`)
document.

Specify the destination for the output file with `--pot-file`.

 ### Produce modulemd-translations YAML
 To convert portable object (`.po`) files into
 modulemd-translations YAML documents that can be included in repodata:
 ```
 ModulemdTranslationHelpers --branch f29 generate_metadata \
                            [--pofile-dir <path>] \
                            [--yaml-file <path>]

 ```

 This will read all files with a `.po` suffix in the `pofile-dir` path and
 write the modulemd YAML to `yaml-file`.

## API
### ModulemdTranslationHelpers
The ModulemdTranslationHelpers package has two primary functions:
* get_module_catalog_from_tags()
* get_modulemd_translations()

#### ModulemdTranslationHelpers.get_module_catalog_from_tags()
This returns a `babel.message.Catalog` object containing all of the
translatable strings from any module tagged with one of the passed tags. It
can be passed to `babel.messages.pofile.write_po()` to create a portable
object template (`.pot`) file.

#### ModulemdTranslationHelpers.get_modulemd_translations()
This returns an iterable of modulemd-translation objects generated from a
set of paths to portable object (`.po`) files containing translation
information.

### ModulemdTranslationHelpers.Fedora
This package provides helper routines for dealing with translations in Fedora
Modules.

#### ModulemdTranslationHelpers.Fedora.KOJI_URL
The URL to the standard Fedora Koji instance.

#### ModulemdTranslationHelpers.Fedora.get_fedora_rawhide_version()
Looks up which Fedora version the current Rawhide branch will become.

#### ModulemdTranslationHelpers.Fedora.get_tags_for_fedora_branch()
Gets the list of tags for modules in a given Fedora branch. (For rawhide,
make sure to use the value returned from get_fedora_rawhide_version.)
