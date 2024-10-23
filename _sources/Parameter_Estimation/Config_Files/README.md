# Configs

General configs for the runs are stored here, and then combined

## Generating ini files for each analysis

The ini files for each injection can be generated using the `Makefile` in configs.

```bash
make create_ini_files
```

> 📝 This will not overwrite existing files. You can run `make clean_ini_files` to remove the existing files.

> ⚠️ This randomly sets the observing time such that the merger will be between 12 and 24 hours before the end of data. This is seeded but different numpy versions may result in different times. The final ini files will be uploaded to ensure the results can be reproduced.