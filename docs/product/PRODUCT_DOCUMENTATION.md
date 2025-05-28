# Activation Manager - Product Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Natural Language Audience Builder](#natural-language-audience-builder)
4. [Data Types and Sources](#data-types-and-sources)
5. [Variable Selection](#variable-selection)
6. [Audience Segmentation](#audience-segmentation)
7. [Export and Distribution](#export-and-distribution)
8. [Best Practices](#best-practices)
9. [Frequently Asked Questions](#frequently-asked-questions)

## Introduction

### What is Activation Manager?

Activation Manager is an advanced audience segmentation platform that enables marketers to build precise, actionable customer segments using natural language. Simply describe your target audience in plain English, and our AI-powered system will identify the right data variables, create optimized segments, and prepare them for activation across your marketing platforms.

### Key Features

- **Natural Language Processing**: Describe audiences conversationally
- **Intelligent Variable Selection**: AI identifies the most relevant data points
- **Advanced Clustering**: Creates balanced segments using K-Medians algorithm
- **Multi-Source Data**: Supports First Party, Third Party, and Clean Room data
- **Visual Analytics**: Understand your data through interactive visualizations
- **One-Click Distribution**: Deploy segments to marketing platforms instantly

### Who Should Use This?

- **Marketing Managers**: Build targeted campaigns without technical expertise
- **Data Analysts**: Accelerate audience creation with AI assistance
- **Campaign Strategists**: Discover new audience opportunities
- **Media Buyers**: Create precise segments for programmatic advertising

## Getting Started

### Accessing the Platform

1. Navigate to your Activation Manager URL
2. Log in with your credentials
3. Click on "Audience Builder" in the main navigation

### Choosing Your Builder Mode

Activation Manager offers two modes:

#### Manual Builder
Traditional interface with dropdown selectors for precise control over criteria.

#### Natural Language Builder (Recommended)
AI-powered interface where you describe your audience in plain English.

To switch modes, use the toggle at the top of the Audience Builder page:
- **Manual Builder** (Sliders icon)
- **Natural Language** (Sparkles icon)

## Natural Language Audience Builder

### Step 1: Select Your Data Environment

Choose the data source that best fits your activation strategy:

#### First Party Data
- **What it is**: Your direct customer data with full activation rights
- **Subtypes Available**:
  - **RampID**: LiveRamp's identity resolution
  - **UID2.0**: The Trade Desk's unified ID solution
  - **Custom ID**: Your proprietary identity system
- **Best for**: Retargeting, customer retention, lookalike modeling

#### Third Party Data
- **What it is**: Licensed external data with usage restrictions
- **Subtypes Available**:
  - **Postal Code**: Geographic targeting data
  - **IAB Standard**: Industry-standard audience segments
- **Best for**: Prospecting, market expansion, competitive conquesting

#### Clean Room Data
- **What it is**: Privacy-compliant collaborative data environments
- **Subtypes Available**:
  - **Clean Room Matched**: Cross-party matched audiences
- **Best for**: Partner collaborations, privacy-first campaigns

### Step 2: Describe Your Target Audience

After selecting your data type, you'll see a personalized prompt. Enter your audience description using natural language.

#### Example Descriptions:

**E-commerce Campaign**:
"Find fashion-conscious women aged 25-40 with high online shopping frequency who live in major metropolitan areas"

**Automotive Campaign**:
"Identify families with children who are likely in-market for SUVs or minivans with household income above $75,000"

**Sustainability Campaign**:
"Target environmentally conscious millennials with high disposable income who prefer eco-friendly products"

**B2B Campaign**:
"Small business owners in technology sector who are decision makers with company size 10-50 employees"

### Step 3: Review Variable Selection

The AI analyzes your description and suggests relevant variables. You'll see:

#### Variable Model Visualization
- **Bar Chart**: Shows relevance scores for top variables
- **Pie Chart**: Displays distribution across variable types
- **Explanation**: How variables relate to your query

#### Variable List
Each suggested variable shows:
- **Description**: What the variable measures
- **Type**: Category (Demographic, Behavioral, etc.)
- **Score**: Relevance to your query (0-10)
- **Data Availability**: Icons showing which data sources have this variable

#### Customizing Selection
- Pre-selected variables are the AI's top recommendations
- Check/uncheck variables to customize
- Aim for 5-10 variables for optimal results

### Step 4: Confirm and Process

Click "Confirm Selection" to proceed. The system will:
1. Retrieve data for your selected variables
2. Apply K-Medians clustering algorithm
3. Create balanced segments (5-10% each)
4. Generate descriptive names

### Step 5: Review Segments

#### Understanding Your Results

Each segment displays:
- **Descriptive Name**: AI-generated name based on characteristics
- **Size**: Number of records and percentage
- **Dominant Traits**: Key characteristics of the segment
- **PRIZM Profile**: Consumer lifestyle classification (if available)

#### Segment Visualization
- **Bar Chart**: Size distribution across segments
- **Scatter Plot**: Visual clustering representation
- **K-Medians Explanation**: How the algorithm created balanced groups

### Step 6: Export or Distribute

#### Export Options
- **Download CSV**: Export full audience data with metadata
  - Includes segment assignments
  - Contains all variable values
  - Adds descriptive headers

#### Distribution
1. Click "Confirm Segments" to finalize
2. Click "Distribute to Platforms"
3. View success animation
4. Automatically redirected to Distribution Center

## Data Types and Sources

### Understanding Variable Types

#### Demographics
- Age, gender, income, education
- Household composition
- Geographic location

#### Behavioral
- Purchase history
- Website interactions
- Product preferences
- Engagement patterns

#### Psychographic
- Lifestyle preferences
- Values and attitudes
- Interest categories
- Brand affinities

#### Financial
- Income levels
- Credit indicators
- Spending patterns
- Investment behavior

### Data Quality Indicators

Look for these quality markers:
- **High Relevance Scores**: Variables scoring 7+ are strongly related
- **Multiple Data Sources**: Variables available across platforms
- **Balanced Type Distribution**: Mix of different variable types

## Variable Selection

### Best Practices

#### Optimal Variable Count
- **Minimum**: 3-4 variables for basic segmentation
- **Recommended**: 5-7 variables for balanced segments
- **Maximum**: 10 variables to avoid over-specification

#### Variable Combinations
Strong combinations include:
- Demographics + Behavioral
- Psychographic + Financial
- Geographic + Purchase Intent

### Understanding Relevance Scores

- **8-10**: Highly relevant, directly mentioned in query
- **6-7**: Relevant, related to query concepts
- **4-5**: Potentially useful, indirect relationship
- **Below 4**: Low relevance, consider removing

## Audience Segmentation

### K-Medians Algorithm

#### What it Does
- Creates distinct groups based on variable similarities
- Ensures each segment is 5-10% of total population
- Balances statistical significance with actionability

#### Why Size Constraints Matter
- **Minimum 5%**: Ensures statistical reliability
- **Maximum 10%**: Prevents over-broad segments
- **Result**: Each segment is large enough to target effectively

### Interpreting Segments

#### Segment Names
AI generates names based on:
- Dominant characteristics
- User's original query
- Market positioning

Examples:
- "Eco-Forward Innovators"
- "Urban Millennials"
- "Premium Market Leaders"

#### Dominant Traits
Key differentiators like:
- "High Income"
- "Urban Location"
- "Environmental Focus"
- "Tech-Savvy"

## Export and Distribution

### CSV Export

#### What's Included
- **Metadata Section**:
  - Export timestamp
  - Original query
  - Data type used
  - Segment summary
- **Data Section**:
  - All records with segment assignments
  - Variable values
  - Unique identifiers

#### File Format
```csv
# Audience Export - 2024-01-15 14:30:00
# Query: environmentally conscious millennials
# Data Type: first_party
# Total Records: 1000
# Segments: 3
#
# Segment Summary:
# - Eco-Forward Innovators: 350 records (35.0%)
# - Sustainable Lifestyle Leaders: 330 records (33.0%)
# - Green Premium Buyers: 320 records (32.0%)
#
PostalCode,AGE_RANGE,INCOME_LEVEL,ENV_SCORE,Group
...
```

### Distribution Center

After confirming segments, you can:
1. Select target platforms
2. Map segment attributes
3. Set activation schedules
4. Monitor deployment status

## Best Practices

### Writing Effective Queries

#### Be Specific
❌ "Find good customers"
✅ "Find loyal customers who purchase monthly with average order value above $100"

#### Include Key Attributes
- Demographics: Age, location, gender
- Behaviors: Purchase patterns, engagement
- Interests: Categories, preferences
- Value: Income, spending levels

#### Use Business Language
The AI understands marketing terms:
- "High-value customers"
- "Likely to churn"
- "Early adopters"
- "Brand advocates"

### Optimizing Results

1. **Start Broad, Then Refine**: Begin with core attributes, add specifics if needed
2. **Review Variable Scores**: Focus on variables scoring 6+
3. **Check Segment Sizes**: Ensure all segments meet 5-10% constraint
4. **Validate Business Logic**: Confirm segments align with campaign goals

### Common Use Cases

#### Customer Retention
"Identify customers at risk of churning who have decreased purchase frequency in last 3 months but were previously high-value"

#### New Product Launch
"Find early adopters who purchase new products within first month and have high social media engagement"

#### Market Expansion
"Target households similar to our best customers but in new geographic markets we're entering"

#### Competitive Conquest
"Identify customers who shop at competitors but match our ideal customer profile"

## Frequently Asked Questions

### General Questions

**Q: How many records can I process?**
A: The system handles millions of records efficiently. Segment sizes are percentage-based, so it scales automatically.

**Q: Can I save my queries for reuse?**
A: Yes, exported audiences include the original query in metadata for future reference.

**Q: How often is the data updated?**
A: Data refresh frequency depends on your data sources. First Party data typically updates daily, Third Party monthly.

### Technical Questions

**Q: What's the difference between K-Means and K-Medians?**
A: K-Medians is more robust to outliers and creates more balanced segments, ideal for marketing activation.

**Q: Why can't I create segments smaller than 5%?**
A: This ensures statistical reliability and prevents over-targeting that could impact campaign performance.

**Q: Can I combine multiple data types?**
A: Currently, select one primary data type per audience. You can create multiple audiences and combine them in Distribution Center.

### Troubleshooting

**Q: No variables were found for my query**
A: Try:
- Using different terminology
- Being more specific about attributes
- Checking data type selection

**Q: Segments seem unbalanced**
A: The algorithm ensures 5-10% per segment. If you need different sizes, create multiple audiences with different criteria.

**Q: Export is taking too long**
A: Large audiences may take a moment. The system will notify you when ready. Check your download folder.

### Best Practices

**Q: How many variables should I select?**
A: 5-7 variables typically produce the best results - enough for differentiation without over-specification.

**Q: Should I always use the AI's suggestions?**
A: The AI provides strong recommendations, but review based on your campaign knowledge and adjust as needed.

**Q: When should I use Clean Room vs First Party data?**
A: Use Clean Room when you need to collaborate with partners while maintaining privacy. Use First Party for direct customer targeting.

## Getting Help

### Support Resources
- **In-App Help**: Click the (?) icon for contextual help
- **Video Tutorials**: Available in the Help Center
- **Support Team**: support@activationmanager.com
- **Documentation**: This guide and technical docs

### Feature Requests
We're constantly improving! Submit feature requests through the feedback button in the app.

---

*Last Updated: May 2024*
*Version: 2.0 - Enhanced Natural Language Interface*