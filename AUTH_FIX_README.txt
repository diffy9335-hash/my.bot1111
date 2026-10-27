RDG Telegram authorization diagnosis
===================================
1. Unpack updates into the EXISTING project directory, keeping your private .env and football.sqlite3.
2. Run: python -m app.auth_check
   This reports the effective token's bot ID and whether Windows environment variables shadow the .env value; it never prints the secret portion.
3. Check that the BotFather token is current for the SAME bot whose chat launches the Mini App. Revoke previously shared bot tokens in BotFather and put the new token in your .env. Restart BOTH server (run.py) and bot after changing it.
4. Reopen the bot chat, send /start and press its newly sent Mini App button (not an old button), while ngrok is still up and PUBLIC_URL matches its HTTPS Forwarding URL (without -> localhost:8000).
5. Do not enable DEV_AUTH on a public tunnel and do not share .env or initData.

If app.auth_check reports no shadowing and the token is current, the issue requires inspecting the actual request-handling/Telegram client path with safe logging; a 401 should not be bypassed.
