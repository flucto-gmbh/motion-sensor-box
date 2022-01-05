# Debugging Git

## Submodules

Sometimes, for no apparent reason, the head in the submodules gets detached. If this happens, change into the submodule and checkout the main branch:

```bash
cd path/to/submodule
git checkout main
git submodule update --remote --merge
```
