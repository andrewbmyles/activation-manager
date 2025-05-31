# User Guide: Enhanced Audience Detail Page

## Getting Started

The Enhanced Audience Detail Page transforms how you refine and configure audiences for activation. Instead of technical variable codes, you now work with an intelligent search interface that understands natural language and provides real-time feedback.

## Accessing the Audience Detail Page

1. **From Saved Audiences**: Click the eye icon (👁️) on any audience card
2. **From Search Results**: Click "View Details" after creating an audience
3. **Direct Link**: Navigate to `/audience/{audienceId}` in your browser

## Page Overview

![Audience Detail Layout](docs/images/audience-detail-layout.png)

The page is divided into three main sections:

### 📋 Header Section
- **Audience Name**: Generated name like "Gaming-Enthusiast Gen Z Males"
- **Description**: Natural language description of your audience
- **Total Reach**: Live-updated final audience size
- **Back Button**: Return to previous page

### 🎯 Left Panel: Refinement Controls
- **Semantic Variable Picker**: Add up to 3 targeting variables
- **Scaling Controls**: Two interactive sliders for audience scaling
- **Activation Filters**: Toggle switches for common filters

### 📊 Right Panel: Summary & Actions
- **Audience Summary**: Size breakdown and scaling factors
- **Insights**: AI-generated audience insights (when available)
- **Action Buttons**: Activate audience or export configuration

## Using the Semantic Variable Picker

### Basic Search

1. **Type Your Query**: Start typing in the search box
   ```
   Example: "high income urban professionals"
   ```

2. **Review Suggestions**: AI-powered suggestions appear as you type
   ![Search Results](docs/images/variable-search.png)

3. **Select Variables**: Click on any suggestion to add it to your audience

### Smart Features

#### Real-time Impact
- **Audience Reduction**: Each variable shows its impact (e.g., -22.7%)
- **Confidence Level**: See how confident the AI is (e.g., 94% confidence)
- **Live Updates**: Total audience size updates immediately

#### Variable Limits
- **Maximum 3 Variables**: Maintains focused targeting
- **Replacement**: Adding a 4th variable will show a warning
- **Removal**: Click the X button to remove any variable

### Example Search Queries

| Query Type | Example | Expected Results |
|------------|---------|------------------|
| **Demographic** | "millennials in urban areas" | AGE_25_34, URBAN_RESIDENT |
| **Behavioral** | "frequent online shoppers" | ECOMMERCE_USERS, DIGITAL_BUYERS |
| **Financial** | "high disposable income" | INCOME_75K_PLUS, AFFLUENT_LIFESTYLE |
| **Interest-based** | "gaming enthusiasts" | GAMING_INTEREST, CONSOLE_OWNERS |
| **Complex** | "eco-conscious suburban families" | ECO_CONSCIOUS, SUBURBAN_FAMILIES |

## Scaling Controls

### Experiments Slider (Test & Control)

**Purpose**: Scale your audience for A/B testing and control groups

**Range**: 0.5x to 10x in 0.25 increments

**Common Use Cases**:
- **1.0x**: No scaling (use original audience size)
- **1.5x**: Small test group expansion
- **2.5x**: Standard A/B test sizing
- **5.0x**: Large-scale campaign testing
- **10x**: Maximum expansion for broad reach

**Example**:
```
Original Audience: 50,000 people
Experiment Scale: 2.5x
Result: 125,000 people for testing
```

### Seed Audience Scaling Slider

**Purpose**: Adjust seed audience size for lookalike modeling

**Range**: 0.5x to 10x in 0.25 increments

**Common Use Cases**:
- **0.5x**: Conservative seed size for precise modeling
- **1.0x**: Standard seed size
- **2.0x**: Balanced reach and precision
- **5.0x**: Broad lookalike expansion
- **10x**: Maximum lookalike reach

**Example**:
```
Base Seed: 30,000 people
Seed Scale: 3.0x
Result: 90,000 people for lookalike modeling
```

## Activation Filters

Toggle switches for common activation workflow requirements:

### Available Filters

1. **Exclude Existing Customers** (15% reduction)
   - Removes people who are already customers
   - Essential for new customer acquisition campaigns

2. **Require Email Permission** (8% reduction)
   - Only includes people with email consent
   - Required for email marketing campaigns

3. **Exclude Competitor Customers** (5% reduction)
   - Removes people loyal to competitor brands
   - Important for competitive positioning

4. **Require Recent Activity** (12% reduction)
   - Only includes recently active users
   - Improves engagement rates

5. **Exclude Suppressed Users** (3% reduction)
   - Removes users on suppression lists
   - Legal compliance requirement

### Filter Combinations

**Email Campaign Setup**:
```
✅ Exclude Existing Customers
✅ Require Email Permission
✅ Exclude Suppressed Users
Impact: ~24% reduction
```

**Brand Protection Setup**:
```
✅ Exclude Existing Customers
✅ Exclude Competitor Customers
✅ Require Recent Activity
Impact: ~29% reduction
```

## Manual Selection Mode

Switch between semantic and traditional selection:

### When to Use Manual Mode

- **Legacy Workflows**: Working with existing audience criteria
- **Specific Variables**: You know exact variable codes needed
- **Compliance**: Regulatory requirements for specific variables
- **Troubleshooting**: Verify semantic selections match expectations

### Switching Modes

1. **To Manual**: Click "Switch to Manual Selection →"
2. **View Criteria**: See original technical variable codes
3. **Back to Semantic**: Click "← Back to Semantic Selection"

### Manual Mode Display

```
Original Audience Criteria:
🗃️ AGE_18_24
🗃️ GENDER_MALE  
🗃️ GAMING_INTEREST
```

## Real-time Calculations

### Calculation Formula

The final audience size is calculated as:

```
Final Size = Base Size 
  × Variable Impact 1
  × Variable Impact 2  
  × Variable Impact 3
  × Experiment Scale
  × Seed Audience Scale
  × Filter Reductions
```

### Example Calculation

```
Base Audience: 67,842
+ "High Income Urban" (-22.7%): × 0.773 = 52,448
+ "Console Owners" (-15.2%): × 0.848 = 44,476
× Experiment Scale (2.5x): × 2.5 = 111,190
× Seed Scale (1.8x): × 1.8 = 200,142
× Filters (exclude customers): × 0.85 = 170,121
Final Reach: 170,121 people
```

## Best Practices

### Variable Selection Strategy

1. **Start with Demographics**: Age, gender, location
2. **Add Behavioral**: Interests, purchase patterns
3. **Layer Financial**: Income, spending habits
4. **Monitor Impact**: Keep total reduction under 60%

### Scaling Guidelines

#### For A/B Testing:
- **Small Tests**: 1.5-2x scaling
- **Standard Tests**: 2-3x scaling  
- **Large Tests**: 3-5x scaling
- **Avoid**: >5x unless needed for statistical significance

#### For Lookalike Modeling:
- **Precise Targeting**: 1-2x scaling
- **Balanced Approach**: 2-4x scaling
- **Broad Reach**: 4-8x scaling
- **Maximum Reach**: 8-10x scaling

### Filter Best Practices

#### Always Enable:
- ✅ **Exclude Suppressed Users**: Legal compliance

#### Email Campaigns:
- ✅ **Require Email Permission**: Essential
- ✅ **Exclude Existing Customers**: For acquisition
- ✅ **Require Recent Activity**: Improves engagement

#### Brand Campaigns:
- ✅ **Exclude Competitor Customers**: Protect brand message
- ✅ **Require Recent Activity**: Ensure active audience

## Troubleshooting

### Common Issues

#### 🚫 No Search Results
**Cause**: Query too specific or misspelled
**Solution**: 
- Try broader terms: "income" instead of "high-income-earners"
- Check spelling
- Use common words: "young adults" instead of "gen z"

#### 📉 Audience Size Too Small
**Cause**: Too many restrictive filters
**Solution**:
- Remove some variables
- Disable non-essential filters
- Increase scaling factors
- Use broader demographic variables

#### ⚡ Slow Search Response
**Cause**: Network connectivity or server load
**Solution**:
- Check internet connection
- Wait a moment and try again
- Use shorter, simpler queries

#### 🔄 Calculations Not Updating
**Cause**: JavaScript error or browser issue
**Solution**:
- Refresh the page
- Clear browser cache
- Try different browser

### Error Messages

| Message | Meaning | Solution |
|---------|---------|----------|
| "You can add up to 3 variables only" | Variable limit reached | Remove a variable first |
| "Search service unavailable" | API connection issue | Check network, try again |
| "Audience not found" | Invalid audience ID | Verify URL or return to saved audiences |

## Advanced Features

### Keyboard Shortcuts

- **Enter**: Add first search result
- **Escape**: Clear search box
- **Tab**: Navigate between controls
- **Space**: Toggle filter switches

### URL Parameters

Share specific configurations:
```
/audience/123?experiment=2.5&seed=1.8&filters=email,customers
```

### Browser Compatibility

**Fully Supported**:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Partially Supported**:
- Internet Explorer 11 (basic functionality only)

## Performance Tips

### For Best Performance:

1. **Use Specific Queries**: "urban millennials" vs "people in cities who are young"
2. **Limit Variables**: 2-3 variables are usually sufficient
3. **Cache Friendly**: Repeated searches are faster
4. **Mobile Optimized**: Works well on tablets and phones

### Expected Response Times:

- **Search Results**: < 500ms
- **Calculation Updates**: < 100ms (real-time)
- **Page Load**: < 2 seconds

## Integration with Marketing Platforms

### Export Options

After configuring your audience:

1. **Export Configuration**: Save settings as JSON
2. **Activate Audience**: Send to marketing platforms
3. **Download Report**: Get PDF summary

### Supported Platforms

- Google Ads
- Facebook Ads Manager
- LinkedIn Campaign Manager
- The Trade Desk
- Amazon DSP
- Custom API integrations

## Getting Help

### In-App Help

- **Hover Tooltips**: Hover over any control for help
- **Confidence Indicators**: Green = high confidence, Yellow = medium
- **Real-time Feedback**: Immediate visual feedback on all changes

### Support Resources

- **Documentation**: Full technical documentation
- **Video Tutorials**: Step-by-step walkthroughs
- **Support Team**: Contact support@tobermory.ai
- **Community**: User community forum

### Feedback

Help us improve by providing feedback:
- **Feature Requests**: What would make this better?
- **Bug Reports**: Found an issue? Let us know!
- **Usage Patterns**: How do you use these features?

---

*Ready to create your first enhanced audience? Start with a simple search like "millennials interested in technology" and explore the features!*