import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const __dirname = path.dirname(fileURLToPath(import.meta.url));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const demoResearch = [
  {id:1,type:'Opportunity',tag:'OPEN CALL',title:'New media residency — Asia',meta:'Deadline · 18 Oct',why:'Strong fit for artists working with AI, moving image and installation.',credits:0},
  {id:2,type:'Research',tag:'FIELD SIGNAL',title:'What collectors are buying from digital-native artists',meta:'6 min read',why:'Useful for offer design and positioning editions vs originals.',credits:0},
  {id:3,type:'Lead',tag:'COMMERCIAL',title:'Brand looking for generative-video collaborators',meta:'Remote · paid',why:'Matches AI-video production capability and portfolio-led outreach.',credits:0},
  {id:4,type:'Deep research',tag:'AI ANALYSIS',title:'Map my top 25 opportunities this month',meta:'Personalised',why:'Uses your profile, geography, goals and portfolio constraints.',credits:12}
];

app.get('/api/health', (_req,res)=>res.json({ok:true,version:'2.0.0'}));
app.get('/api/feed', (_req,res)=>res.json({items:demoResearch}));
app.post('/api/research', (req,res)=>{
  const {credits=0, query=''} = req.body || {};
  const cost = 8;
  if (credits < cost) return res.status(402).json({ok:false,error:'Not enough credits',required:cost});
  res.json({ok:true,cost,remaining:credits-cost,result:{title:`Research brief: ${query || 'your field'}`,summary:'Demo mode is active. Connect OPENAI_API_KEY to replace this deterministic preview with live personalised research.',actions:['Review 10 current opportunities','Score by fit and effort','Add top 3 to your weekly plan']}});
});

app.get('*', (_req,res)=>res.sendFile(path.join(__dirname,'public','index.html')));
const port = process.env.PORT || 3000;
app.listen(port,()=>console.log(`2S running on ${port}`));