### Basic structure for composing Azure Pipelines.

The minimal block is `steps` that contains a single task to be completed.

`Jobs` is for job templates that are composed of multiple `steps`.

`Pipelines` may include both `jobs` and individual `steps` in some specific manner that gets reused across multiple repositories.

All of `steps`, `jobs` and `pipelines` templates should have input parameters defined.

`Variables` may include specific sets of shared values that can be imported in many locations.

See `azure-pipelines.yaml` file with the extended parts for demo purposes of how full composition looks like.
