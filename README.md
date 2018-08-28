# mmdzanata
## Prerequisites
* [libmodulemd](https://github.com/fedora-modularity/libmodulemd)
* [koji](https://pagure.io/koji)
* [zanata-client](https://github.com/zanata/zanata-client)

To install on Fedora 28+, run:
```
dnf install libmodulemd koji zanata-client
```

## Installation
With the prerequisites installed, the latest version can be installed with
`pip install mmdzanata` or on Fedora 28+ with `dnf install mmdzanata`
(recommended).

## CLI Usage
### Zanata Client Setup
Use of the upload feature for string extraction requires setting up the
Zanata client appropriately. Follow the
[instructions](http://docs.zanata.org/en/release/client/configuration/) from
Zanata to set up your `~/.config/zanata.ini` file appropriately. Note that
you will want to do this against
https://fedora.zanata.org
and not
https://translate.zanata.org

### Extract Translatable Strings
To extract translatable strings from modules for a particular Fedora
release (e.g. f29):
```
mmdzanata --branch f29 extract [--upload]
```
This will read all of the module metadata from the Koji build-system and
convert the translatable strings to a Zanata-compatible gettext document. If
 `--upload` is passed, it will also attempt to use the `zanata-cli` tool to
 upload the strings to the Zanata server. See the "Zanata Client Setup"
 section above for information on how to configure this.

 ### Produce modulemd-translations YAML
 To read the translated strings from Zanata and convert them into
 modulemd-translations YAML documents that can be included in repodata:
 ```
 mmdzanata --branch f29 generate_modulemd
 ```

 This will produce a YAML file in the current directory with all known
 translated strings.

## API
### mmdzanata
The mmdzanata class has two primary methods:
* get_module_catalog_from_tags()
* generate_metadata()

#### mmdzanata.get_module_catalog_from_tags()
This returns a babel.message.Catalog object containing all of the
translatable strings from any module tagged with one of the passed tags.

#### mmmdzanata.generate_metadata()
This returns an iterable of modulemd-translation objects from the supplied
Zanata project and branch.

### mmdzanata.fedora
This class provides helper routines for dealing with translations in Fedora
Modules.
