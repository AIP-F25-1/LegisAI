# Servers Running Status

**Date**: December 2024

---

## 🚀 SERVER STATUS

### Backend Server
- **Status**: ✅ Running
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/
- **Port**: 8000

### Frontend Server
- **Status**: ✅ Running
- **URL**: http://localhost:5173
- **Port**: 5173

---

## 📋 QUICK ACCESS

### Backend Endpoints:
- **Root**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Research**: http://localhost:8000/api/research
- **Drafting**: http://localhost:8000/api/draft
- **Compliance**: http://localhost:8000/api/compliance/check
- **HITL Stats**: http://localhost:8000/api/hitl/stats
- **Domain Compliance**: http://localhost:8000/api/compliance/domains

### Frontend Pages:
- **Home**: http://localhost:5173/
- **Research**: http://localhost:5173/research
- **Drafting**: http://localhost:5173/drafting
- **Compliance**: http://localhost:5173/compliance
- **Upload**: http://localhost:5173/upload

---

## 🛠️ MANAGEMENT COMMANDS

### Stop Servers:
```bash
# Stop backend (port 8000)
lsof -ti:8000 | xargs kill -9

# Stop frontend (port 5173)
lsof -ti:5173 | xargs kill -9

# Stop both
lsof -ti:8000,5173 | xargs kill -9
```

### Restart Servers:
```bash
# Backend
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev
```

### Check Status:
```bash
# Check if servers are running
curl http://localhost:8000/
curl http://localhost:5173/
```

---

## ✅ FEATURES AVAILABLE

### New Features (Just Implemented):
1. **HITL Workflow** - Accept/Reject/Edit agent outputs
2. **Domain Compliance Packs** - Finance, Healthcare, Labor, GDPR, CCPA
3. **Enhanced Explainability** - Citations with credibility scores

### All Features:
- Hybrid Legal Research (FAISS + BM25)
- AI-Powered Document Drafting
- Compliance Checking
- Clause Analysis & Risk Detection
- Multi-Agent Orchestration (LangGraph)
- Knowledge Graph Builder
- Regulatory Monitoring
- Monte Carlo Risk Simulations
- Document OCR
- Timeline Builder
- Speech-to-Text + TTS

---

## 🧪 TESTING

### Test New Features:

1. **HITL Workflow**:
   - Go to http://localhost:5173/research
   - Run a query
   - Look for HITLPanel below results
   - Test Accept/Reject/Edit buttons

2. **Domain Compliance**:
   ```bash
   curl http://localhost:8000/api/compliance/domains
   curl -X POST http://localhost:8000/api/compliance/domain-check \
     -H "Content-Type: application/json" \
     -d '{"content": "test", "domains": ["finance"], "jurisdiction": "US"}'
   ```

3. **Explainability**:
   ```bash
   curl -X POST "http://localhost:8000/api/explainability/format-citation?citation_text=Smith%20v.%20Jones&citation_type=case"
   ```

---

**Both servers are running and ready for testing!**

