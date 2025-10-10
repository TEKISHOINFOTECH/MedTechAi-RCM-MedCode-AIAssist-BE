# Clinical Notes SOAP Improvement Feature

## Overview

The Claim Edit page now includes an AI-powered feature to improve and restructure clinical notes using the professional SOAP (Subjective, Objective, Assessment, Plan) format.

## What is SOAP Format?

SOAP is a standardized method of documentation used by healthcare providers:

- **S (Subjective):** Patient's complaints, symptoms, and history in their own words
- **O (Objective):** Observable facts including vital signs, physical exam, lab results
- **A (Assessment):** Provider's clinical impression, diagnosis, and problem list
- **P (Plan):** Treatment plan, medications, tests, referrals, and follow-up

## Feature Location

In the Claim Edit page, look for the **Clinical Notes & Observations** section with the green gradient button labeled:

```
✨ Improve with SOAP Format
```

## How to Use

1. **Enter Clinical Notes:**
   - Type or paste clinical notes into the textarea
   - Notes can be in any format (free text, bullet points, etc.)
   - Minimum 10 characters required

2. **Click the Improve Button:**
   - The button is located in the top-right of the Clinical Notes section
   - Click "Improve with SOAP Format"
   - The button will show a loading state: "Improving with SOAP..."

3. **Review Improved Notes:**
   - A new panel will appear below showing improved SOAP format notes
   - The improved notes are displayed in a separate textarea (original notes remain unchanged)
   - You can edit the improved notes directly in the panel
   - Selected ICD-10 and CPT codes are displayed below the improved notes
   - ICD code suggestions automatically refresh based on improved notes

4. **View Associated Codes:**
   - The improved notes panel includes two side-by-side sections:
     - **Selected ICD-10 Codes**: Shows all diagnosis codes (with count)
     - **Selected CPT Codes**: Shows all procedure codes with categories (with count)
   - Both sections are scrollable if there are many codes

5. **Close or Keep:**
   - Click the X button to close the improved notes panel
   - The panel can be reopened by clicking "Improve with SOAP Format" again
   - Both original and improved notes coexist - choose which to use for your claim

## Visual Presentation

The improved SOAP notes panel features:

- **Teal/Green Gradient Background**: Visually distinct from other sections
- **Large Editable Textarea**: 384px height with monospace font for readability
- **Side-by-Side Code Display**:
  - Left panel: ICD-10 codes in blue theme
  - Right panel: CPT codes in green theme
  - Both panels show code count badges
  - Scrollable for long code lists (max height: 160px)
- **Close Button**: X icon in top-right corner to dismiss panel
- **Sparkles Icon**: Visual indicator that content is AI-generated
- **Helpful Hint**: Reminder that original notes remain unchanged

## Benefits

### 1. Professional Documentation
- Converts informal notes into standardized medical documentation
- Follows industry best practices for clinical documentation

### 2. Better Organization
- Clearly separates subjective vs objective information
- Organizes information logically for easier review

### 3. Improved Coding Accuracy
- Structured format helps identify relevant diagnoses
- Makes it easier to select appropriate ICD and CPT codes

### 4. Compliance
- Meets documentation standards for insurance claims
- Reduces risk of claim denials due to poor documentation

### 5. Time Savings
- Automatically formats notes instead of manual restructuring
- Maintains all clinical information from original notes

## Example Transformation

### Before (Unstructured):
```
Patient comes in with chest pain that started yesterday.
Pain is sharp, worse with breathing. BP 140/90, temp normal.
Sounds like pleurisy. Will order chest x-ray and start on ibuprofen.
Follow up in 1 week.
```

### After (SOAP Format):
```
S (Subjective):
Chief Complaint: Chest pain
History of Present Illness: Patient reports onset of chest pain
approximately 24 hours ago. Pain is characterized as sharp in quality
and exacerbated by respiratory effort. Patient denies fever, cough,
or recent trauma.

O (Objective):
Vital Signs: Blood pressure 140/90 mmHg, temperature within normal limits
Physical Examination: Patient appears in mild discomfort. Respiratory
examination reveals pain on deep inspiration.

A (Assessment):
Primary Diagnosis: Pleurisy (suspected)
Clinical Impression: Patient presents with pleuritic chest pain.
Differential diagnosis includes pleurisy, musculoskeletal pain, and
pulmonary pathology requiring further investigation.

P (Plan):
1. Diagnostic Testing: Chest X-ray ordered to rule out pulmonary pathology
2. Medications: Ibuprofen for pain management and anti-inflammatory effect
3. Follow-up: Scheduled follow-up appointment in 1 week to review imaging
   results and reassess symptoms
4. Patient Education: Advised on warning signs requiring immediate return
```

## Technical Details

### Edge Function
- **Endpoint:** `/functions/v1/improve-clinical-notes`
- **Method:** POST
- **Model:** OpenAI GPT-4o-mini
- **Temperature:** 0.3 (focused output)

### Features
- Preserves all clinical information from original notes
- Adds professional medical terminology where appropriate
- Uses complete, grammatically correct sentences
- Includes specific measurements and timeframes when available
- Makes reasonable clinical inferences only when strongly supported

### Security
- Processed through Supabase Edge Functions
- CORS enabled for secure frontend access
- Requires authentication via Supabase ANON_KEY

## Best Practices

1. **Original Note Quality:**
   - More detailed original notes = better SOAP output
   - Include specific symptoms, measurements, and observations

2. **Review AI Output:**
   - Always review improved notes for accuracy
   - AI preserves clinical info but may rephrase
   - Verify all medical details are correct

3. **Edit as Needed:**
   - Feel free to edit the improved notes
   - Add any missing information
   - Adjust phrasing to match your style

4. **When to Use:**
   - Quick notes that need professional formatting
   - Dictated notes that need structure
   - Converting bullet points to narrative format
   - Standardizing documentation across providers

## Troubleshooting

### Button is Disabled
- Ensure clinical notes have at least 10 characters
- Wait for any ongoing AI operations to complete

### "Failed to improve notes" Error
- Check internet connection
- Verify Supabase Edge Functions are running
- Ensure OpenAI API key is configured

### Notes Don't Change
- Original notes may already be in good SOAP format
- Check browser console for error messages

## Integration with Other Features

The improved SOAP notes automatically trigger:
- **ICD Code Suggestions:** AI analyzes improved notes for diagnosis codes
- **Better Accuracy:** Structured format helps AI identify relevant codes more accurately
- **CPT Suggestions:** When ICD codes are selected, CPT codes are suggested based on improved documentation

## Future Enhancements

Potential improvements being considered:
- Save multiple versions (original vs SOAP)
- Custom SOAP templates by specialty
- Voice-to-SOAP direct dictation
- Batch improvement for multiple claims

---

**Note:** This feature uses AI to assist with documentation improvement. Healthcare providers remain responsible for ensuring accuracy and completeness of all clinical documentation.
