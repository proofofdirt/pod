# Uploading the Website to Turbify (proofofdirt.com)

Upload everything inside `website/` (NOT the folder itself) so `index.html` sits at the web root:

```
index.html
oracle/index.html
contribute/index.html
dao/index.html
```
(Do not upload TURBIFY-UPLOAD.md.)

## Option A — Turbify File Manager (browser, no software)
1. Log in at turbify.com → My Services → **Web Hosting** control panel
2. Open **File Manager**
3. At the web root, click **Upload** and add `index.html`
4. Create folders `oracle`, `contribute`, `dao` (New Folder), open each, upload its `index.html`
5. Visit proofofdirt.com, /oracle/, /contribute/, /dao/ to verify

## Option B — FTPS client (FileZilla / WinSCP — better for updates)
Turbify requires **FTPS (explicit TLS, TLS 1.2)**:
- Host: `ftp.proofofdirt.com` · Port: `21`
- Encryption: "Require explicit FTP over TLS"
- Credentials: Hosting control panel → **FTP Accounts** → *Configure FTP Client*
1. Connect, navigate to the web root on the remote pane
2. Drag the contents of `D:\ClaudeWorkspace\PODFinal\website\` (index.html + the three folders) into it
3. Overwrite when re-uploading after changes

## Before going live — replace placeholders
- `POD_TREASURY_MULTISIG_ADDRESS` (index.html ×2, dao/index.html ×2) → real Squads address
- Team bios + photos on dao/index.html
- Landing page meta description/title still carry earlier messaging — update if desired
