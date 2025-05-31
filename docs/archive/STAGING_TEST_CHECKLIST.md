# Staging Environment Test Checklist

Use this checklist to verify staging deployments before promoting to production.

**Staging Version:** _______________  
**Tester:** _______________  
**Date:** _______________

## 🔐 Authentication Tests
- [ ] Login page loads correctly
- [ ] Password authentication works
- [ ] Session persists across page refreshes
- [ ] Logout functionality works

## 🔍 Variable Picker Tests
- [ ] Search returns relevant results
- [ ] Results show 🧠 semantic label
- [ ] Pagination works (if > 10 results)
- [ ] Refine search functionality works
- [ ] Selected variables persist through refine
- [ ] Confirm button works
- [ ] Export to JSON works
- [ ] Export to CSV works
- [ ] Clear/Reset functionality works

## 💬 Natural Language Interface Tests
- [ ] Chat interface loads
- [ ] Processes natural language queries
- [ ] Shows variable suggestions
- [ ] Variable selection works
- [ ] Workflow completion works
- [ ] UI scales properly on larger screens

## 🎨 Visual/UI Tests
- [ ] All pages render correctly
- [ ] Navigation menu works
- [ ] "NL Multi-Variate Audience Builder" label shows
- [ ] Responsive design works on different screen sizes
- [ ] No broken images or assets
- [ ] Fonts load correctly

## ⚡ Performance Tests
- [ ] Initial page load < 3 seconds
- [ ] Search response < 2 seconds
- [ ] No significant lag in UI interactions
- [ ] Memory usage stable (no leaks)

## 🛠️ API Tests
- [ ] `/api/health` returns 200
- [ ] `/api/embeddings-status` shows correct status
- [ ] All API endpoints return expected data
- [ ] CORS headers present
- [ ] Error responses properly formatted

## 📊 Data Tests
- [ ] Variable data loads (49,000+ variables)
- [ ] Search returns relevant results
- [ ] Categories properly assigned
- [ ] Export contains correct data

## 🚨 Error Handling Tests
- [ ] Invalid search queries handled gracefully
- [ ] Network errors show appropriate messages
- [ ] 404 pages work correctly
- [ ] Console shows no critical errors

## 📱 Browser Compatibility
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge

## 📝 Console & Logs Check
- [ ] No JavaScript errors in console
- [ ] No 404s for assets
- [ ] No CORS errors
- [ ] Backend logs show normal operation

## ✅ Final Verification

### Must Pass (Critical)
- [ ] All authentication features work
- [ ] Variable search and selection works
- [ ] No data loss or corruption
- [ ] No security vulnerabilities exposed

### Should Pass (Important)
- [ ] Performance acceptable
- [ ] UI renders correctly
- [ ] All features accessible

### Nice to Have
- [ ] Optimal performance
- [ ] Perfect pixel rendering
- [ ] All browsers supported

## 📋 Sign-off

**All critical tests passed:** ⬜ Yes ⬜ No

**Ready for production:** ⬜ Yes ⬜ No

**Notes/Issues Found:**
```
[Add any issues or observations here]
```

**Approved by:** _______________ **Date:** _______________

---

## Quick Test Commands

```bash
# Check staging URL
curl -I https://stg-TIMESTAMP-dot-PROJECT-ID.appspot.com/api/health

# View staging logs
gcloud app logs tail --version=stg-TIMESTAMP

# Compare with production
gcloud app versions describe PROD-VERSION
gcloud app versions describe STG-VERSION
```

## Promotion Command

Once all tests pass:
```bash
./promote-to-prod.sh stg-TIMESTAMP
```