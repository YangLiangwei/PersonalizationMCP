# Reddit API Integration

Reddit platform integration module with OAuth2 authentication and complete Reddit API access functionality.

## 🔧 Authentication Setup

### 1. Get Reddit API Credentials

1. Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in application information:
   - **Name**: Application name (e.g., PersonalHub)
   - **App type**: Select "web app"
   - **Description**: Application description (optional)
   - **About URL**: About page URL (optional)
   - **Redirect URI**: `http://localhost:8888/callback`
4. After creation, record the following information:
   - **Client ID**: Application ID (below the app name)
   - **Client Secret**: Client secret key

### 2. Configure Authentication

Add Reddit configuration to the `config` file in the project root directory:

```bash
# Reddit API Configuration
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_REDIRECT_URI=http://localhost:8888/callback
```

### 3. OAuth2 Authentication Flow

#### Method 1: Using MCP Functions for Authentication

```python
# 1. Setup OAuth2 authentication
setup_result = mcp_personalhub_setup_reddit_oauth(
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# 2. Visit the returned authentication URL for authorization
# User needs to visit the auth URL in browser and authorize

# 3. Complete authentication (after getting authorization code)
complete_result = mcp_personalhub_complete_reddit_oauth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    authorization_code="authorization_code_from_callback"
)
```

#### Method 2: Manual Configuration

If you already have valid access tokens, you can configure directly:

```bash
REDDIT_ACCESS_TOKEN=your_access_token
REDDIT_REFRESH_TOKEN=your_refresh_token
```

## 🚀 Features

### 📊 Account Information
- **User Overview**: Get mixed timeline of posts and comments
- **Karma Breakdown**: View karma distribution across subreddits
- **User Preferences**: Get account settings and preferences
- **Trophies & Achievements**: View Reddit trophies and achievements

### 📝 Content Management
- **Submitted Posts**: Get all user-submitted posts
- **Comment History**: View user's comment records
- **Saved Content**: Get saved posts and comments
- **Hidden Posts**: View hidden content
- **Voting Records**: Get upvoted/downvoted content

### 👥 Community Interaction
- **Subscribed Subreddits**: View followed communities
- **Moderated Communities**: Get subreddits where user is moderator
- **Contributor Permissions**: View subreddits with contributor access

### 💬 Messaging System
- **Inbox**: Get all messages
- **Unread Messages**: View unread messages
- **Sent Messages**: View sent message history

## 🛠️ API Function List

### Authentication Management
```python
# Configuration status check
get_reddit_config()
test_reddit_credentials()

# OAuth2 authentication flow
setup_reddit_oauth(client_id, client_secret, redirect_uri?)
complete_reddit_oauth(client_id, client_secret, authorization_code, redirect_uri?)

# Token management
get_reddit_token_status()
refresh_reddit_token()
auto_refresh_reddit_token_if_needed()
```

### User Information
```python
# Basic information
get_user_subreddits(access_token?, limit=100)
get_user_trophies(access_token?)
get_user_preferences(access_token?)
get_user_karma_breakdown(access_token?)

# Community permissions
get_moderated_subreddits(access_token?, limit=100)
get_contributor_subreddits(access_token?, limit=100)
```

### Content Retrieval
```python
# Posts and comments
get_user_submitted_posts(username?, access_token?, limit=100, sort="new")
get_user_comments(username?, access_token?, limit=100, sort="new")
get_user_overview(username?, access_token?, limit=100, sort="new")

# Saved and interactions
get_saved_content(username?, access_token?, limit=100)
get_hidden_posts(username?, access_token?, limit=100)
get_upvoted_content(username?, access_token?, limit=100)
get_downvoted_content(username?, access_token?, limit=100)
```

### Messaging System
```python
# Message management (requires privatemessages scope)
get_inbox_messages(access_token?, limit=100)
get_unread_messages(access_token?, limit=100)
get_sent_messages(access_token?, limit=100)
```

## 📋 Usage Examples

### Get User Activity Overview
```python
# Get recent posts and comments
overview = get_user_overview(limit=20, sort="new")

# Get subscribed communities
subreddits = get_user_subreddits(limit=50)

# Get karma distribution
karma = get_user_karma_breakdown()
```

### View Content History
```python
# Get submitted posts
posts = get_user_submitted_posts(limit=10, sort="top")

# Get comment history
comments = get_user_comments(limit=10, sort="new")

# Get saved content
saved = get_saved_content(limit=20)
```

### Check Messages
```python
# Get inbox messages
inbox = get_inbox_messages(limit=10)

# Get unread messages
unread = get_unread_messages(limit=5)
```

## 🔒 Permission Scopes

Reddit API uses the following OAuth2 permission scopes:

- `identity`: Access user basic information
- `read`: Read user content and subscriptions
- `history`: Access voting and hidden content history
- `privatemessages`: Access private messages (optional, requires special permission)

## ⚠️ Important Notes

### API Limitations
- **Request Rate**: Reddit API has strict rate limiting
- **Permission Requirements**: Some features require specific OAuth permissions
- **Data Access**: Can only access data for the currently authenticated user

### Privacy Settings
- User privacy settings may affect data retrieval
- Some content may be inaccessible due to user settings
- Private messaging functionality requires additional permission requests

### Token Management
- Access tokens are valid for 1 hour
- Refresh tokens can be used to automatically update access tokens
- Recommended to use `auto_refresh_reddit_token_if_needed()` for automatic token management

## 🔍 Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Check OAuth permission scopes
   - Verify token validity
   - Confirm user privacy settings

2. **Authentication Failure**
   - Ensure Client ID and Secret are correct
   - Check redirect URI matches
   - Verify authorization code hasn't expired

3. **Empty Data Returns**
   - May be due to user privacy setting restrictions
   - Check query parameters (username, limits, etc.)
   - Confirm user has relevant content

### Debugging Tips
- Use `get_reddit_config()` to check configuration status
- Use `test_reddit_credentials()` to verify credentials
- Check `get_reddit_token_status()` to understand token status

## 📚 Related Resources

- [Reddit API Documentation](https://www.reddit.com/dev/api/)
- [Reddit OAuth2 Guide](https://github.com/reddit-archive/reddit/wiki/OAuth2)
- [Reddit App Management](https://www.reddit.com/prefs/apps)
- [Reddit API Best Practices](https://www.reddit.com/wiki/api)
