# Quberneeds

A small Python script that downloads [Helm charts](https://github.com/kubernetes/helm/blob/master/docs/charts.md) and runs [helmfiles](https://github.com/roboll/helmfile) embedded inside them.

Embedding helmfiles inside Helm charts enables environment variable substitution on deployment, a feature currently not supported by Helm directly.

## Usage

Quberneeds takes a command (`install` or `delete`) and the path to a JSON file as command-line arguments.

The JSON file lists a set of charts to download and install and a set of environment variables to set. It looks like this:

```json
{
  "charts": {
    "myrepo/mychart": "1.0.0",
    "myrepo/otherchart": "1.0.0"
  },
  "env": {
    "SOME_VAR": "some-value",
    "OTHER_VAR": "other-value"
  }
}
```

Quberneeds can either be run from Git or using [Zero Install](http://0install.net/) to handle dependencies.

### Run from Git

Clone this Git repository, ensure that `python`, `helmfile` and `helm` are in your `PATH` and then run:

    python quberneeds.py (install|delete) file.json

### Run using Zero Install

Ensure `0install` is in your `PATH` and then run:

    0alias quberneeds http://assets.axoom.cloud/tools/quberneeds.xml
    quberneeds (install|delete) file.json

## Releasing

To package a new release of Quberneeds as a Zero Install feed run:

    0install run http://0install.net/tools/0template.xml quberneeds.xml.template version=0.1
