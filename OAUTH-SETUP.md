# OAuth Configuration Guide for CVBooster

Supabase project: https://siekxlkhsppcqwyoxrvn.supabase.co

## Step 1: Sign in to Supabase Dashboard
Go to: https://supabase.com/dashboard/project/siekxlkhsppcqwyoxrvn/auth/providers

## Step 2: Configure Google OAuth

### 2a. Create Google OAuth Credentials
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Go to **APIs & Services > Credentials**
4. Click **Create Credentials > OAuth client ID**
5. Application type: **Web application**
6. Authorized JavaScript origins:
   ```
   http://localhost:3000
   http://localhost:80
   ```
7. Authorized redirect URIs:
   ```
   https://siekxlkhsppcqwyoxrvn.supabase.co/auth/v1/callback
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

### 2b. Configure in Supabase
1. In Supabase dashboard → **Authentication > Providers**
2. Find **Google** and click **Enable**
3. Paste:
   - **Client ID**: from Google Cloud Console
   - **Client Secret**: from Google Cloud Console
4. Save

## Step 3: Configure Facebook OAuth

### 3a. Create Facebook App
1. Go to https://developers.facebook.com/
2. Click **Create App**
3. Purpose: **Other** → Create App
4. Go to **Settings > Basic**
5. Copy **App ID** (this is the Client ID)
6. Copy **App Secret** (this is the Client Secret)
7. Add **Platform**: **Website**
8. Site URL: `http://localhost:3000`

### 3b. Add Facebook Login
1. Go to **Add Feature > Facebook Login**
2. Add **Client OAuth Login** method
3. Add Valid OAuth redirect URIs:
   ```
   https://siekxlkhsppcqwyoxrvn.supabase.co/auth/v1/callback
   ```

### 3c. Configure in Supabase
1. In Supabase → **Authentication > Providers**
2. Find **Facebook** and click **Enable**
3. Paste:
   - **Client ID**: the App ID from Facebook
   - **Client Secret**: the App Secret from Facebook
4. Save

## Step 4: Configure TikTok OAuth (Custom Provider)

### 4a. Create TikTok Developer App
1. Go to https://developers.tiktok.com/
2. Create account + new app
3. Product: **Login Kit**
4. Website URL: `http://localhost:3000`
5. Redirect URI: `https://siekxlkhsppcqwyoxrvn.supabase.co/auth/v1/callback`
6. Scope: `user.basic.profile`
7. Copy **API Key** and **API Secret**

### 4b. Configure in Supabase
1. In Supabase → **Authentication > Providers**
2. Scroll to **Custom OAuth/OIDC Providers**
3. Click **Add Custom Provider**
4. Fill in:
   - **Name**: `tiktok`
   - **Client ID**: TikTok API Key
   - **Client Secret**: TikTok API Secret
   - **Authorize URL**: `https://www.tiktok.com/v2/auth/authorize/`
   - **Token URL**: `https://open.tiktokapis.com/v2/oauth/token/`
   - **User Info URL**: `https://open.tiktokapis.com/v2/user/info/`
   - **Redirect URL**: `https://siekxlkhsppcqwyoxrvn.supabase.co/auth/v1/callback`
   - **Scope**: `user.basic.profile`
5. Save

## Step 5: Configure OpenRouter API Key

Edit the `.env` file in the project root:

```bash
OPENROUTER_API_KEY=sk-or-your-key-here
```

Use the model: `nvidia/nemotron-3-ultra-550b-a55b:free`
(already configured in the backend LLM service)

## Step 6: Update Redirect URLs in Frontend

The frontend redirects to: `http://localhost:3000/auth/callback`

Make sure this URL is added to:
- Google Cloud Console → Authorized redirect URIs
- Facebook Developer → Valid OAuth redirect URIs
- TikTok Developer → Redirect URIs

## Step 7: Test

After configuration:
1. Start the app: `docker compose up`
2. Go to http://localhost/login
3. Click "Continue with Google" or "Continue with Facebook"
4. You should be redirected to the provider, then back to your app
5. You should land on the dashboard
