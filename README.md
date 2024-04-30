# 3DEqualizer AYON Addon

## Introduction

This is addon providing integration of [3DEqualizer4 from Science-D-Vision](https://www.3dequalizer.com/) into [AYON](https://ayon.ynput.io/).

Integration includes:

- Workfiles
- Loading plates (cameras)
- Publishing scripts to Maya and Nuke
- Publishing of lens data

## Building and Installing
Run `python create_package.py` in the root of the repository and upload resulting zip file to your AYON instance.

## Notes

This integration is installing PySide2 into 3DEqualizer environment as it doesn't ship with Qt support. This comes with some price - to make Qt UI work with 3DEqualizer, `processEvent()` is periodically called. This is not optimal and it might create some issues, like 3Dequalizer crashing or UI lags.

For extraction, it is using 3de4 native scripts, but since they are depending on some UI, there are few hacks around it but this is better than rewriting the whole export logic to publishing plugins.
