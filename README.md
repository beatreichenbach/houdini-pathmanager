# Houdini Path Manager

Path Manager is a tool for SideFX Houdini to manage file paths. It allows the user to replace and change paths,
and copy or move files.

## Installation

Meadow is installed as a Houdini Package.

1. Go to the [Releases](https://github.com/beatreichenbach/houdini-pathmanager/releases) page and download the latest `pathmanager.zip`.
2. Navigate to your Houdini user preferences folder: `$HOME/houdini‹X›.‹Y›`
3. If you don't have a folder named `packages` in that directory, create it.
4. Extract the contents of the `.zip` file into the `packages` folder.
5. Restart Houdini. You can verify the installation by opening the **Package Browser** (**Windows > Package Browser**) and ensuring "Path Manager" is listed.

**Example Folder Structure:**
```text
├── houdini21.0
    ├── packages/
        ├── pathmanager.json
        └── /pathmanager
            └── (package files)
```

## License

MIT License. Copyright 2026 - Beat Reichenbach.
See the [License file](LICENSE) for details.

## Features

### Filters:
- node path
- node type
- parm name
- parm type

- Show empty parameters
- show missing paths

### Replace Path
- methods:
  - replace
    - regex
    - glob
    - match case
  - copy
  - move
  - search
  - version
    - set version latest
    - set version
- preserve relative structure
- relative root

### Path Mode
- Make paths relative to $HIP, limit parent dirs
- expand/collapse variables

- <UDIM>, $F, $F4
- Preview
- icon for status
- context:
  - Open in explorer
  - copy path
  - go to node

