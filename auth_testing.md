# Auth-Gated App Testing Playbook (Emergent Google Auth)

## Step 1: Create Test User & Session in MongoDB

```js
mongosh --eval "
use('test_database');
var userId = 'test-user-' + Date.now();
var sessionToken = 'test_session_' + Date.now();
db.users.insertOne({
  user_id: userId,
  email: 'test.user.' + Date.now() + '@example.com',
  name: 'Test User',
  picture: 'https://via.placeholder.com/150',
  created_at: new Date()
});
db.user_sessions.insertOne({
  user_id: userId,
  session_token: sessionToken,
  expires_at: new Date(Date.now() + 7*24*60*60*1000),
  created_at: new Date()
});
print('Session token: ' + sessionToken);
print('User ID: ' + userId);
"
```

## Step 2: Test Backend API

```bash
# /api/auth/me with Bearer token
curl -X GET "$REACT_APP_BACKEND_URL/api/auth/me" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"

# Protected endpoint
curl -X POST "$REACT_APP_BACKEND_URL/api/ideas/save" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{"idea_id": "..."}'
```

## Step 3: Browser Testing (Playwright)

```python
await page.context.add_cookies([{
    "name": "session_token",
    "value": "YOUR_SESSION_TOKEN",
    "domain": "your-app.com",
    "path": "/",
    "httpOnly": True,
    "secure": True,
    "sameSite": "None"
}])
await page.goto("https://your-app.com/dashboard")
```

## Checklist
- [ ] User has `user_id` (custom UUID)
- [ ] Session `user_id` matches user `user_id`
- [ ] All Mongo queries use `{"_id": 0}` projection
- [ ] `/api/auth/me` returns user data with both cookie and Bearer
- [ ] Dashboard loads when authenticated, redirects to /login when not
- [ ] Public routes (/, /ideas, /ideas/:slug) work without auth
