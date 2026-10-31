const portrait=document.getElementById('aria-portrait');
const intro=document.getElementById('aria-intro');
const play=document.getElementById('play-intro');
const restore=document.getElementById('show-portrait');
const status=document.getElementById('media-status');
play.addEventListener('click',async()=>{
  portrait.hidden=true;intro.hidden=false;restore.hidden=false;
  intro.currentTime=0;intro.muted=false;
  status.textContent='Loading ARIA’s recorded introduction…';
  try{await intro.play();}catch{status.textContent='Select the video’s play control to hear ARIA’s introduction.';intro.focus();}
});
intro.addEventListener('playing',()=>{play.textContent='Replay my introduction ▷';status.textContent='ARIA’s recorded introduction is playing. Begin the guided tour whenever you are ready.';});
intro.addEventListener('ended',()=>{status.textContent='Ready to explore? Select “Begin the guided tour” or choose a project below.';});
intro.addEventListener('error',()=>{status.textContent='The introduction could not load. You can still begin the guided tour or explore the projects below.';});
restore.addEventListener('click',()=>{intro.pause();intro.hidden=true;portrait.hidden=false;restore.hidden=true;status.textContent='Welcome. Select “Begin the guided tour” to explore Vannetta’s portfolio with ARIA.';});
document.addEventListener('visibilitychange',()=>{if(document.hidden)intro.pause();});
document.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>intro.pause()));

// Preserve existing portfolio links that target named sections at the original address.
const legacyPortfolioSections=new Set(["resumes", "hire-ready", "fpa-evidence-center", "npv-irr-flagship", "saas-financial-model", "fpa-command-center", "enterprise-flagships", "featured-delivery-lab", "featured-cfo-suite", "featured-aria", "featured-fpa-copilot", "featured-ai-evaluation", "featured-automation", "featured-decision-lab", "showcase-directory", "enterprise-showcase", "technical-lab", "excel-business", "work", "business", "patient-transport", "education", "credentials", "specializations", "certificates", "technical-projects", "finance-projects", "salon-dashboard", "creative-lab", "codex", "contact"]);
let legacySection="";try{legacySection=decodeURIComponent(location.hash.slice(1));}catch{}
if(legacyPortfolioSections.has(legacySection)){location.replace("https://vhane-create.github.io/portfolio/portfolio.html#"+encodeURIComponent(legacySection));}
