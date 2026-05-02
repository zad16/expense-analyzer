# Security Changes Log

This document outlines the security improvements made to the repository before making it public.

## Changes Made
1. **Removed Hardcoded Secrets**: 
   - `app.py`: Removed the hardcoded `APP_PIN` value for the mobile variant. The application will now strictly rely on the environment variable `.env`.
2. **Updated `.gitignore`**:
   - Added `.env_recovery` and `rclone.conf` to `.gitignore` to prevent these sensitive files from being tracked by Git in the future.
3. **Untracked Sensitive Files**:
   - Ran `git rm --cached` on `.env_recovery` and `rclone.conf` to remove them from Git tracking while preserving them on the local filesystem.
4. **Git History Rewriting**:
   - Squashed all previous commits into a single "Initial commit" to completely eliminate the historical footprint of all secrets previously stored in the repository.

**Important Note for the User:** 
Although the repository history has been wiped of these secrets, it is still strongly recommended that you revoke your Groq API key and Google Drive access tokens. As best practice, consider treating keys that were briefly in a repository as compromised.