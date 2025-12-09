# Testing Guide - New Features

**Date**: December 2024  
**Features to Test**: HITL, Explainability, Domain Compliance Packs

---

## 🚀 Server Status

### Backend Server
- **URL**: http://localhost:8000
- **Status**: Running (check with `curl http://localhost:8000/`)
- **API Docs**: http://localhost:8000/docs

### Frontend Server
- **URL**: http://localhost:5173
- **Status**: Running (check in browser)

---

## ✅ 1. TEST HITL WORKFLOW

### Backend API Tests:

#### Test 1: Submit Accept Feedback
```bash
curl -X POST http://localhost:8000/api/hitl/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "research",
    "action": "accept",
    "original_output": {
      "query": "test query",
      "summary": "test summary",
      "confidence_score": 0.85
    }
  }'
```

#### Test 2: Submit Reject Feedback
```bash
curl -X POST http://localhost:8000/api/hitl/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "research",
    "action": "reject",
    "original_output": {
      "query": "test query",
      "summary": "test summary"
    },
    "feedback_reason": "Output is too generic and lacks specific legal citations"
  }'
```

#### Test 3: Submit Edit Feedback
```bash
curl -X POST http://localhost:8000/api/hitl/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "feature_type": "drafting",
    "action": "edit",
    "original_output": {
      "draft_content": "Original draft content"
    },
    "user_edit": "Edited and improved draft content with better clauses"
  }'
```

#### Test 4: Get Feedback Statistics
```bash
curl http://localhost:8000/api/hitl/stats
```

#### Test 5: Get Learning Insights
```bash
curl http://localhost:8000/api/hitl/insights
```

#### Test 6: Get Recent Feedback
```bash
curl http://localhost:8000/api/hitl/recent?limit=5
```

### Frontend UI Tests:

1. **Open Research Page**:
   - Navigate to http://localhost:5173/research
   - Enter a research query (e.g., "What are GDPR compliance requirements?")
   - Wait for results to appear
   - **Look for HITLPanel** below the research summary
   - Click **"Accept"** button → Should show success toast
   - Click **"Reject"** button → Should show feedback form
   - Fill in rejection reason → Submit → Should show success toast
   - Click **"Edit"** button → Should show edit textarea
   - Edit the content → Click **"Save Edit"** → Should show success toast

2. **Open Drafting Page**:
   - Navigate to http://localhost:5173/drafting
   - Enter a draft query (e.g., "Create a service agreement")
   - Wait for draft to generate
   - **Look for HITLPanel** below the draft content
   - Test Accept/Reject/Edit buttons

3. **Open Compliance Page**:
   - Navigate to http://localhost:5173/compliance
   - Paste some legal content
   - Run compliance check
   - **Look for HITLPanel** below the analysis
   - Test Accept/Reject/Edit buttons

---

## ✅ 2. TEST DOMAIN COMPLIANCE PACKS

### Backend API Tests:

#### Test 1: Get Available Domains
```bash
curl http://localhost:8000/api/compliance/domains
```

**Expected Response**:
```json
{
  "status": "success",
  "domains": ["finance", "healthcare", "labor", "gdpr", "ccpa", "general"]
}
```

#### Test 2: Get Domain Information
```bash
curl http://localhost:8000/api/compliance/domain/finance
```

#### Test 3: Check Finance Domain Compliance
```bash
curl -X POST http://localhost:8000/api/compliance/domain-check \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This loan agreement includes an interest rate of 5% APR. The borrower has the right of rescission within three days.",
    "domains": ["finance"],
    "jurisdiction": "US"
  }'
```

#### Test 4: Check Healthcare Domain Compliance
```bash
curl -X POST http://localhost:8000/api/compliance/domain-check \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This medical service agreement includes patient privacy notice and HIPAA compliance clauses.",
    "domains": ["healthcare"],
    "jurisdiction": "US"
  }'
```

#### Test 5: Check Multiple Domains
```bash
curl -X POST http://localhost:8000/api/compliance/domain-check \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This employment contract includes minimum wage requirements and FMLA leave rights.",
    "domains": ["labor", "finance"],
    "jurisdiction": "US"
  }'
```

### Frontend UI Tests:

1. **Test via API Client** (Browser Console):
   ```javascript
   // Get available domains
   fetch('http://localhost:8000/api/compliance/domains')
     .then(r => r.json())
     .then(console.log)

   // Check domain compliance
   fetch('http://localhost:8000/api/compliance/domain-check', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       content: "This contract includes interest rate disclosure.",
       domains: ["finance"],
       jurisdiction: "US"
     })
   })
     .then(r => r.json())
     .then(console.log)
   ```

2. **Integration Test** (Future):
   - Add domain selection to Compliance page UI
   - Test domain-specific compliance checking

---

## ✅ 3. TEST EXPLAINABILITY FEATURES

### Backend API Tests:

#### Test 1: Format Citation
```bash
curl -X POST http://localhost:8000/api/explainability/format-citation \
  -H "Content-Type: application/json" \
  -d '{
    "citation_text": "Smith v. Jones, 2023 SC 123",
    "citation_type": "case"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "citation": {
    "text": "Smith v. Jones, 2023 SC 123",
    "type": "case",
    "credibility_score": 0.93,
    "probability": 0.85,
    "metadata": {
      "plaintiff": "Smith",
      "defendant": "Jones",
      "year": "2023",
      ...
    }
  }
}
```

#### Test 2: Format Statute Citation
```bash
curl -X POST http://localhost:8000/api/explainability/format-citation \
  -H "Content-Type: application/json" \
  -d '{
    "citation_text": "US Code § 101",
    "citation_type": "statute"
  }'
```

#### Test 3: Research with Explainability
```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "GDPR compliance requirements",
    "max_results": 5
  }'
```

**Check Response For**:
- `citations` array with formatted citations
- `explainability` object with:
  - `confidence_score`
  - `probability`
  - `credibility_score`
  - `citation_count`
  - `reasoning`

### Frontend UI Tests:

1. **Research Page**:
   - Navigate to http://localhost:5173/research
   - Enter query: "What are the requirements for a valid contract?"
   - Check the response in browser DevTools (Network tab)
   - Look for `explainability` object in the response
   - Verify citations are formatted with credibility scores

2. **Check Citations in Results**:
   - Research results should include formatted citations
   - Each citation should have:
     - Type (case, statute, regulation, treatise)
     - Credibility score (0.0-1.0)
     - Probability score
     - Metadata

---

## 📊 VERIFICATION CHECKLIST

### HITL Workflow:
- [ ] Backend accepts feedback submissions
- [ ] Feedback is stored in `feedback_data.json`
- [ ] Statistics endpoint returns correct data
- [ ] Insights endpoint returns learning patterns
- [ ] HITLPanel appears in Research page
- [ ] HITLPanel appears in Drafting page
- [ ] HITLPanel appears in Compliance page
- [ ] Accept button works
- [ ] Reject button shows feedback form
- [ ] Edit button shows edit interface
- [ ] All actions show success toasts

### Domain Compliance:
- [ ] Available domains endpoint works
- [ ] Domain info endpoint works
- [ ] Finance domain checking works
- [ ] Healthcare domain checking works
- [ ] Labor domain checking works
- [ ] Multiple domain checking works
- [ ] Violations are detected correctly
- [ ] Compliance scores are calculated

### Explainability:
- [ ] Citation formatting endpoint works
- [ ] Citation credibility scoring works
- [ ] Research endpoint includes explainability metadata
- [ ] Citations are formatted consistently
- [ ] Probability scores are included
- [ ] Credibility scores are calculated

---

## 🐛 TROUBLESHOOTING

### Backend Not Starting:
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Start backend manually
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Not Starting:
```bash
# Check if port 5173 is in use
lsof -i :5173

# Kill process if needed
kill -9 <PID>

# Start frontend manually
cd frontend
npm run dev
```

### Import Errors:
```bash
# Check if services are importable
cd backend
python3 -c "from services.hitl_service import HITLService; print('OK')"
python3 -c "from services.explainability_service import ExplainabilityService; print('OK')"
python3 -c "from services.domain_compliance_packs import DomainCompliancePacks; print('OK')"
```

### Missing Dependencies:
```bash
# Install missing packages
pip install -r requirements.txt
```

---

## 📝 TEST RESULTS TEMPLATE

```
Date: ___________
Tester: ___________

HITL Workflow:
- Backend API: [ ] Pass [ ] Fail
- Frontend UI: [ ] Pass [ ] Fail
- Feedback Storage: [ ] Pass [ ] Fail

Domain Compliance:
- Available Domains: [ ] Pass [ ] Fail
- Finance Domain: [ ] Pass [ ] Fail
- Healthcare Domain: [ ] Pass [ ] Fail
- Labor Domain: [ ] Pass [ ] Fail

Explainability:
- Citation Formatting: [ ] Pass [ ] Fail
- Research Explainability: [ ] Pass [ ] Fail
- Credibility Scoring: [ ] Pass [ ] Fail

Overall: [ ] All Pass [ ] Some Failures
Notes: ___________
```

---

**End of Testing Guide**

