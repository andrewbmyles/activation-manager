# Data Persistence User Guide

## Overview

The Data Persistence feature allows you to save, manage, and reuse your created audiences. This guide explains how to use these features effectively.

## Features

### 1. Saving Audiences

After creating an audience through the Natural Language Multi-Variate Audience Builder:

1. Complete the audience creation workflow until you see your segments
2. Look for the **"Save Audience"** button next to "Confirm Segments"
3. Click the button to save your audience
4. You'll see a success message confirming the save

**What gets saved:**
- Your original natural language query
- All selected variables with their relevance scores
- Generated segments with size and characteristics
- Data type selection (First Party, Third Party, Clean Room)
- Metadata including creation time and session information

### 2. Viewing Saved Audiences

Access your saved audiences through the navigation menu:

1. Click **"Saved Audiences"** in the left sidebar
2. View all your saved audiences in a list format
3. Each audience shows:
   - Name and description
   - Total audience size
   - Number of segments
   - Creation date
   - Selected variables (first 5 shown)

### 3. Managing Audiences

For each saved audience, you can:

- **View Details** 👁️ - See full audience information (coming soon)
- **Export** 📥 - Download audience data (coming soon)
- **Archive** 📁 - Remove from active list while preserving data

### 4. Archive Functionality

To archive an audience:
1. Click the Archive button (📁) on any audience
2. Confirm the archive action
3. The audience will be moved to archived status
4. Archived audiences can be restored later (feature coming soon)

## Best Practices

### Naming Conventions
- Audiences are automatically named with the creation date
- Consider adding descriptive names in future versions
- Your original query serves as the description

### Storage Limits
- No hard limits on number of saved audiences
- Each user's data is isolated
- Older audiences may be auto-archived after 90 days (configurable)

### Performance Tips
- The Saved Audiences page loads quickly even with many audiences
- Search and filter features coming in next version
- Data is partitioned by date for optimal performance

## Technical Details

### Data Storage
- Audiences are stored in Parquet format for efficiency
- Data is partitioned by user and date
- Thread-safe operations ensure data integrity
- All data is stored within your organization's App Engine instance

### Data Security
- User isolation: You can only see your own audiences
- No cross-user data access
- Platform credentials are encrypted (when platform features are enabled)
- Data remains within your GCP project

### API Access
For developers, audiences can be accessed via API:

```bash
# List audiences
GET /api/audiences?user_id={user_id}

# Get specific audience
GET /api/audiences/{audience_id}?user_id={user_id}

# Save new audience
POST /api/audiences
Content-Type: application/json
{
  "user_id": "your_user_id",
  "name": "Audience Name",
  "data_type": "first_party",
  "selected_variables": ["VAR1", "VAR2"],
  ...
}

# Archive audience
PUT /api/audiences/{audience_id}/status
{
  "user_id": "your_user_id",
  "status": "archived"
}
```

## Troubleshooting

### Save Button Not Appearing
- Ensure you've completed the segment creation step
- The button appears only after segments are generated
- Check browser console for any errors

### Audience Not Saving
- Verify you're logged in
- Check network connectivity
- Ensure all required fields are present
- Look for error messages in the UI

### Can't See Saved Audiences
- Refresh the Saved Audiences page
- Check you're using the same user account
- Verify the audience was saved successfully

## Limitations

Current limitations (to be addressed in future updates):
- Using demo_user for all saves (full auth coming soon)
- No audience editing after save
- Export functionality is placeholder
- No search/filter on saved audiences page
- Maximum 50 audiences shown (pagination coming)

## Future Enhancements

Planned features:
- Edit saved audiences
- Duplicate audiences
- Share audiences with team members
- Advanced search and filtering
- Bulk operations
- Integration with distribution platforms
- Audience versioning and history

## Support

For issues or questions:
1. Check the error messages in the UI
2. Review browser console for detailed errors
3. Contact support with your session ID and timestamp