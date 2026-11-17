# K2 Vizag – YouTube auto-uploader

Claude makes the videos → commits them + their title/description/tags to
`queue.yaml` → GitHub Actions uploads them to your channel every day and
records the links in `uploaded.json`.

- Runs daily at 11:47 IST, also right after `queue.yaml` changes, and from the
  **Actions → YouTube upload → Run workflow** button.
- `mode: schedule` uploads up to 6 videos per run (YouTube's free daily limit)
  and YouTube makes them public one per day at 18:00 IST.
- A video is never uploaded twice (checked against `uploaded.json`).

## One-time setup (about 20 minutes, works in a phone browser)

### 1. Google Cloud project + YouTube API
1. Open https://console.cloud.google.com and sign in with the Google account
   that owns your YouTube channel.
2. Create a project, e.g. "k2vizag-uploader".
3. **APIs & Services → Library** → search **YouTube Data API v3** → **Enable**.

### 2. OAuth consent screen
1. **APIs & Services → OAuth consent screen** (Google Auth Platform) → External.
2. App name "K2 Vizag uploader", your email as support + developer contact.
3. Scopes: add `.../auth/youtube.upload`.
4. **Audience → Publish app** ("In production"). Important: in "Testing" mode
   the login expires every 7 days. You'll see an "unverified app" warning when
   you log in – that's fine for your own use (tap Advanced → Go to app).

### 3. OAuth client
1. **Credentials → Create credentials → OAuth client ID → Web application**.
2. Authorised redirect URI: `https://developers.google.com/oauthplayground`
3. Copy the **Client ID** and **Client secret**.

### 4. Get the refresh token (OAuth Playground)
1. Open https://developers.google.com/oauthplayground
2. ⚙️ (top right) → tick **Use your own OAuth credentials** → paste Client ID
   and Client secret.
3. In "Input your own scopes" type `https://www.googleapis.com/auth/youtube.upload`
   → **Authorize APIs** → choose your channel's account → Allow.
4. **Exchange authorization code for tokens** → copy the **Refresh token**.

### 5. Put the 3 values in GitHub (never in chat)
github.com/k2vizag/fortesting → **Settings → Secrets and variables → Actions →
New repository secret**:
- `YT_CLIENT_ID`
- `YT_CLIENT_SECRET`
- `YT_REFRESH_TOKEN`

### 6. Make the workflow run on the main branch
GitHub only runs daily schedules from the repo's default branch, so the
uploader files must be merged into it (ask Claude to open a pull request, then
tap Merge).

### 7. Public videos – YouTube audit (important)
YouTube keeps videos uploaded by a **new, unaudited** API project **locked as
private**. To let the uploader publish publicly, fill in the free
"YouTube API Services – Audit and Quota Extension" form:
https://support.google.com/youtube/contact/yt_api_form
(say: personal channel, uploads my own Shorts to my own channel.) It usually
takes a few days to a few weeks. Until it's approved, uploads arrive in YouTube
Studio as private.

## Daily use
- Ask Claude for videos as usual; it adds them to `queue.yaml`.
- To change a title before it goes out, edit `queue.yaml` (or ask Claude).
- To hold a video: add `skip: true` under it.
- Check what was uploaded: `uploaded.json` or the Actions tab.
- Check the queue without uploading: `python3 youtube_uploader/upload.py --dry-run`
