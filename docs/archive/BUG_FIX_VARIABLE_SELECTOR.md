# Bug Fix: Variable Selector Form Submission Issue

## Problem
When creating an audience in the Audience Builder:
- If the form fields (name, description, type) were filled in and a user selected a variable from the modal, the page would crash and redirect to the main audience page
- If the form fields were empty, the variable selection worked correctly

## Root Cause
The buttons inside the VariableSelector component were missing the `type="button"` attribute. In HTML forms, buttons without an explicit type default to `type="submit"`. When clicking a variable to select it, the button was submitting the form prematurely, causing the redirect.

## Solution
Added `type="button"` to all interactive buttons in the VariableSelector component:
1. Variable selection buttons (line 159)
2. Category toggle buttons (line 135)

## Files Modified
- `/audience-manager/src/components/VariableSelector.tsx`

## Test Added
- `/audience-manager/src/components/__tests__/VariableSelector.test.tsx`
  - Verifies all buttons have `type="button"`
  - Tests that selecting a variable doesn't submit the form
  - Tests dropdown behavior and search functionality

## How to Test Manually
1. Go to Audience Builder page
2. Click "Create Audience"
3. Fill in audience name, description, and select type
4. Click "Add Criteria"
5. Select a variable from the dropdown
6. The variable should be added without redirecting to the main page

## Prevention
- Always add `type="button"` to buttons inside forms unless they are meant to submit
- Consider adding an ESLint rule to catch missing button types in forms