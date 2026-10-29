(() => {
 const $ = id => document.getElementById(id);
 document.body.classList.add('aria-immersive');
 const nav = document.querySelector('header nav'); nav.replaceChildren();
 const drawer = document.createElement('aside'); drawer.id = 'aria-drawer'; drawer.hidden = true; drawer.className = 'aria-drawer'; drawer.setAttribute('aria-label','Conversation and information');
 const close = document.createElement('button'); close.textContent = 'Close panel'; close.onclick = () => { drawer.hidden = true; }; drawer.append(close);
 document.body.append(drawer);
 const sections = {};
 sections.conversation = $('history').closest('.panel');
 sections.information = document.querySelector('[aria-label="Information for ARIA"]');
 const settings = document.createElement('section'); settings.setAttribute('aria-label','Voice and playback controls'); sections.settings = settings;
 const heading = document.createElement('h2'); heading.textContent = 'Voice & playback'; settings.append(heading);
 const voiceControls = document.querySelector('.overlay .actions');
 settings.append(voiceControls);
 const topics = document.querySelector('[aria-label="Explore ARIA finance skills"]'); if(topics) settings.append(topics);
 for (const section of Object.values(sections)) if(section) drawer.append(section);
 function show(name) {
  for (const [key, section] of Object.entries(sections)) if(section) section.hidden = key !== name;
  drawer.hidden = false; close.focus();
 }
 for (const [name, title] of [['information','Add information'],['conversation','Conversation'],['settings','Voice & controls']]) {
  const button = document.createElement('button'); button.textContent = title; button.onclick=()=>show(name); nav.append(button);
 }
 document.addEventListener('keydown', e => { if(e.key==='Escape') drawer.hidden=true; });
 const dock = document.querySelector('.aria-bottom-dock');
 const mic = $('mic'); mic.textContent='Speak'; dock.querySelector('.actions').prepend(mic);
 const loopButton=[...voiceControls.querySelectorAll('button')].find(b=>b.textContent==='Start voice conversation');
 if(loopButton) dock.querySelector('.actions').prepend(loopButton);
 $('send').textContent='Ask ARIA'; $('question').placeholder='Ask ARIA anything…';
 const latest=document.createElement('div');latest.id='aria-caption';latest.setAttribute('role','status');latest.textContent='Here with you. Type a message or open Voice & controls to enable Heart.';document.body.append(latest);
 new MutationObserver(()=>{
  const messages=$('history').querySelectorAll('.msg');
  const last=[...messages].reverse().find(el=>el.querySelector('small')?.textContent==='ARIA');
  if(last){const clone=last.cloneNode(true);clone.querySelector('small')?.remove();latest.textContent=clone.textContent;}
 }).observe($('history'),{childList:true,subtree:true});
 const warning=document.createElement('p'); warning.className='muted'; warning.textContent='New Heart speech uses the approved portrait. Natural blinking, new lip sync and body gestures are still in development.'; settings.append(warning);
 // No generated-looking idle motion: hold the actual approved portrait while waiting.
 const v=$('aria-heart-video'); v.poster='assets/aria-full-body-approved.png'; v.preload='none';
 v.removeAttribute('src'); v.load();
})();
