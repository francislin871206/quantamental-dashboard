# How to Share Your Dashboard

You have 3 ways to share this dashboard with your team. Choose the one that fits your situation:

## 1. Quick & Easy (Same WiFi)
**Best for:** Working together in the same room/campus.
**Time:** Instant.

1. Ensure your laptop and your teammates are on the **same WiFi network**.
2. Run the dashboard: `streamlit run app.py`
3. Identify your **Network URL** from the terminal (e.g., `http://10.192.102.168:8501`).
4. Send that link to your team.

---

## 2. Temporary Internet Link (Cloudflare Tunnel)
**Best for:** Showing teammates remotely for a few hours without deploying.
**Time:** 2 minutes.

1. Install `cloudflared` (if not installed).
2. Run your app locally: `streamlit run app.py`
3. In a **new terminal**, run:
   ```powershell
   cloudflared tunnel --url http://localhost:8501
   ```
4. Copy the `https://....trycloudflare.com` link and share it. It works anywhere in the world.

---

## 3. Permanent Deployment (Streamlit Cloud)
**Best for:** The 3-week competition duration.
**Time:** 5 minutes.

1. **Push to GitHub**:
   We just committed your code. Now push it:
   ```powershell
   git push origin master
   ```
2. **Deploy**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign up/Login with GitHub.
   - Click **"New app"**.
   - Select your repository (`quantamental-dashboard`).
   - Main file path: `Competition/app.py`
   - Click **"Deploy!"**.

Your dashboard will be live at `https://quantamental-dashboard-competition.streamlit.app` (or similar) 24/7!
