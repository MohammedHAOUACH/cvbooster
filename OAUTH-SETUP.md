# OAuth Configuration Guide for CVBooster

CVBooster uses **direct Google OAuth** (authorization code flow) against the FastAPI
backend. No Supabase is involved.

## How the flow works

1. Frontend redirects the browser to `GET /api/auth/google`
2. Backend redirects to Google with a one-time `state` token
3. Google redirects back to `GOOGLE_REDIRECT_URI` with `code` + `state`
4. Backend validates the state, exchanges the code, creates/updates the profile,
   and generates a signed JWT
5. Backend redirects to `/login?token=<jwt>`; the login page stores the token
   (localStorage) and redirects to the dashboard
6. All API calls send `Authorization: Bearer <jwt>`

## Step 1 — Create Google OAuth credentials

1. Go to https://console.cloud.google.com/
2. Create a project (or select an existing one)
3. **APIs & Services > OAuth consent screen**: configure your app (External, add
   the `email` and `profile` scopes)
4. **APIs & Services > Credentials > Create credentials > OAuth client ID**
   - Application type: **Web application**
   - Authorized JavaScript origins:
     ```
     http://localhost
     http://your-vps-ip
     https://your-domain
     ```
   - Authorized redirect URIs (must exactly match `GOOGLE_REDIRECT_URI`):
     ```
     http://localhost/api/auth/google/callback
     http://your-vps-ip/api/auth/google/callback
     https://your-domain/api/auth/google/callback
     ```
5. Copy the **Client ID** and **Client Secret**

## Step 2 — Configure `.env`

```bash
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GOOGLE_REDIRECT_URI=http://your-vps-ip/api/auth/google/callback

# Generate a real secret for production:
# python3 -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET=change-me
SKIP_AUTH=false
```

Then rebuild the frontend image (auth flags are baked at build time):

```bash
docker compose up -d --build
```

## Notes

- `SKIP_AUTH=true` disables authentication entirely (development only). When it is
  false, the frontend is built without the skip-auth flag and users must sign in.
- The JWT is signed with `JWT_SECRET` (HS256) and expires after 24 h. Tokens are
  never accepted unless they are correctly signed — unsigned/forged tokens are
  rejected.
- Facebook/TikTok sign-in are not implemented; the login screen only offers Google.
