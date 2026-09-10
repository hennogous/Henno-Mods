---
name: working-files-mac-access
description: Shadow PC "Working Files" folder is reachable from the Mac via Google Drive sync
metadata:
  type: project
---

The Shadow desktop's `C:\Users\Shadow\Desktop\Working Files\` is synced to Google Drive and mounted on the Mac at:

`~/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/`

**Why:** CLAUDE.md only lists the Windows path; when a session runs on the Mac, files dropped in the Google Drive path sync to the Shadow desktop (and vice versa). Confirmed working 2026-07-04 by delivering a Blender screenshot this way.

**How to apply:** To hand files to/from the Shadow PC (screenshots, textures, exports), read/write this Mac path directly instead of saying the Windows path is unreachable. Note there is no "Working Files" on the Mac's own Desktop.
