This Python script implements a Telegram bot with the following key functionalities:

1. User Submission System
Command: /submit <wallet_address>

Functionality:

Users can submit a cryptocurrency wallet address to claim a "win".

Enforces a 42-hour cooldown between submissions per user.

Stores user data in Firebase Realtime Database under winners/<user_id>.

Tracks:

Telegram username

Total wins

List of submitted wallet addresses

Dates of wins

Last submission timestamp

2. Admin Features
Command: /winners

Admin-only (restricted to ADMINS_ID)

Retrieves and displays all winner data from Firebase:

Usernames

Win counts

Submission dates

Wallet addresses

3. Automated Data Cleanup
Runs daily at 3 AM UTC:

Removes win records older than 3 weeks.

Deletes entire user entries if all their wins are expired.

4. Notifications
Sends real-time alerts to the moderator (MODERATOR_ID) when a user submits an address:

text
📢 New Submission!
👤 User: {username} (ID: {user_id})
💳 Address: {address}
🏆 Total Wins: {win_count}
5. Security & Validation
User cooldown enforcement (42 hours)

Admin command access control

Firebase authentication via service account key

Technical Workflow
Initialization:

Connects to Firebase using credentials from serviceAccountKey.json

Sets up Telegram bot with token

User Interaction:

Diagram
Code








Database Structure:

json
"winners": {
  "123456789": {
    "username": "john_doe",
    "wins": 3,
    "addresses": ["0xabc...", "0xdef..."],
    "win_dates": ["2025-07-28", "2025-07-30"],
    "last_submission": "2025-07-30 14:22:05"
  }
}
Scheduled Maintenance:

Daily job prunes old records:

python
if win_date < (current_time - 3_weeks):
    delete_record()

Use Case
This bot is designed for crypto giveaway/contest systems where:
Users claim rewards via wallet submissions
Admins need to track legitimate winners
Old data needs automatic cleanup to prevent DB bloat

Note: The bot token and Firebase credentials shown in this code sample are intentionally visible as non-functional examples for demonstration purposes. These placeholder values have no active privileges and will never be deployed in a production environment.
