# Clinical Document Intelligence Hub

A tool that reads clinical documents, figures out how serious the patient's condition is, and tells you when they should follow up. Built to save doctors and nurses hours of paperwork and help catch risky cases.

**Live Demo**: https://josephin-clinical-ai-demo-2026.streamlit.app/

## The Problem

Doctors and nurses spend way too much time reading the same patient files over and over. Important stuff gets missed. Sick patients don't get seen fast enough.

## What I Built

I made a system that:
- Reads clinical notes (PDF, text, or images)
- Pulls out patient info, what meds they're on, vital signs, what problems the doctors found
- Looks at the information and decides how risky the case is
- Suggests when they should come back for a follow-up visit
- Creates a PDF report you can download and keep

Instead of spending 20 minutes reading and taking notes, the whole thing is done in 5-10 seconds.

## How It Works

**You give it**: A clinical note (paste it or upload a PDF)

**It does**: 
- Reads the document
- Sends it to an AI to pull out the important stuff
- Scores how risky it is based on what it sees
- Works out a follow-up schedule

**You get back**: A risk score (0-10), patient info, meds list, what's wrong, when to see them next

## Installation

```bash
git clone https://github.com/josephinshajan-a11y/clinical-document-intelligence-hub.git
cd clinical-document-intelligence-hub
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_actual_key_here" > .env
streamlit run streamlit_app.py
```

**Get your free API key**: https://console.groq.com (takes 2 minutes)

## Usage

1. Go to the live app or run it on your computer
2. Paste in a clinical note or upload a PDF
3. Click "Analyze Document"
4. See the risk score, medications, problems, and follow-up dates
5. Download the PDF if you want to save it

## Example: Marcus Thompson (Test Case)

**What you paste in**:
```
PATIENT: Marcus Thompson, 52-year-old male
COMPLAINT: Acute chest pain for 2 hours, radiating to left arm

HISTORY: Type 2 Diabetes, Hypertension, Obesity (BMI 32), former smoker
VITALS: BP 162/96, HR 96, Temp 37.2°C
MEDICATIONS: Metformin 1000mg, Lisinopril 20mg, Atorvastatin 80mg, Aspirin 325mg

ASSESSMENT: Rule out acute coronary syndrome
PLAN: EKG, troponin, cardiology consultation, ICU monitoring
```

**What you get back**:
```
Risk Score: 7.5/10 - HIGH RISK
Confidence: 94%

Medications: Metformin, Lisinopril, Atorvastatin, Aspirin
Problems: Acute chest pain, diabetes, high BP (not controlled), obesity, used to smoke

Follow-up:
- Day 1: Cardiology + labs
- Day 3: Team check-in
- Day 7: Specialist visit
- Day 14: Check if meds are working
- Day 30: Full checkup
```

## How I Score Risk

I look at the clinical notes and count up keywords. If I see serious stuff like "stroke", "sepsis", or "acute" - that's +3 points. If I see problems like "diabetes" or "high blood pressure" - that's +1.5 points each. Other health problems are +1 point. If they're over 70, add 1 more.

Then I sort them:
- **7 or higher** = HIGH RISK (needs urgent help)
- **4 to 7** = MEDIUM RISK (should see a doctor soon)
- **Below 4** = LOW RISK (normal follow-up is fine)

### Why I Picked This Way

I could have used fancy machine learning, but keyword counting works better because:
- It's fast (done in seconds)
- Doctors can understand exactly why it gave that score
- Doesn't need a big database of patient info
- Good enough to show the idea works
- When something seems wrong, you can see why

### The Follow-up Schedule

The schedule changes depending on how sick they are:
- **HIGH RISK**: See a specialist today, get labs done today, check in after 3 days, appointment in a week
- **MEDIUM RISK**: Schedule a doctor visit in the next few days, come back in 2 weeks, another checkup a month later
- **LOW RISK**: Schedule something for next week, check in after a couple weeks, see doctor in a month

## What I Used

- **AI**: Llama 3.3 70B language model from Groq
- **Website**: Streamlit (it's simple and free to host)
- **Reading PDFs**: PyPDF2 for normal ones, OCR for scanned images
- **Making reports**: ReportLab to create PDFs
- **Hosting**: Streamlit Cloud (free)
- **Code**: Python 3.10+

## What I'm Assuming

- You're putting real medical info in (not random text)
- You'll double-check what the AI pulls out before you use it (it's a starting point, not the final word)
- This simple scoring is good enough for a demo (there are more complicated ways, but they take way longer)
- You know this is a test, not approved for real patient care yet
- A doctor always makes the final decision, not the computer

## The Ethics Part

The Marcus Thompson example above is just made up for testing. In the real demo, I use my dad's actual discharge summary - and he said it was okay. That's the right way to handle real patient info.

If this was going into a real hospital, you'd need:
- Patients to agree their info could be used
- An ethics board to look it over and approve it
- To follow HIPAA rules to keep patient info private
- To not save people's names or anything that could identify them
- Real doctors to test it and make sure it works

Right now it's just a proof of concept - showing what's possible, not ready for patients yet.

## Real Talk

This works great as a demo. But if you wanted to actually use this in a hospital, you'd need:
- Doctors to test it and say it's accurate
- Lawyers and the hospital's permission
- The hospital's ethics committee to say yes
- Insurance
- All the privacy rules followed properly

The tool gives you a suggestion - doctors still decide what actually happens.

---

**Built by**: Josephin Shajan  
**Email**: josephinshajan@gmail.com  
**Phone**: +44 7553 779990  
**GitHub**: https://github.com/josephinshajan-a11y/clinical-document-intelligence-hub
