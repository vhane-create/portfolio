const $=s=>document.querySelector(s),M=SalonModel;
const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n/100);
const signed=n=>(n>=0?'+':'−')+money(Math.abs(n));
let result;
$('#inputs').innerHTML=M.sample.map((r,i)=>`<div class="location"><h4>${r.name}</h4><div class="fields">${[['appointments','Monthly appointments'],['price','Average service price ($)'],['supplies','Supplies per appointment ($)'],['fixed','Monthly fixed expenses ($)']].map(([k,label])=>`<label for="location-${i}-${k}">${label}<input id="location-${i}-${k}" data-row="${i}" data-key="${k}" type="number" required min="0" max="${k==='appointments'?2000:k==='fixed'?100000:2000}" step="${k==='appointments'?1:.01}" value="${r[k]}"></label>`).join('')}</div></div>`).join('');
function rows(){return M.sample.map((r,i)=>{let copy={...r};for(const k of ['appointments','price','supplies','fixed']){let v=$('#location-'+i+'-'+k).value;copy[k]=v===''?'':Number(v)}return copy})}
function update(){
 const volume=Number($('#volume').value),pricing=Number($('#pricing').value);
 $('#volumeLabel').value=(volume>=0?'+':'')+volume+'%';$('#pricingLabel').value=(pricing>=0?'+':'')+pricing+'%';
 result=M.evaluate(rows(),volume,pricing);$('#export').disabled=!result.valid;
 document.querySelectorAll('[data-key]').forEach(x=>x.setAttribute('aria-invalid',String(!x.validity.valid)));
 $('#errors').hidden=result.valid;$('#errors').textContent=result.valid?'':result.errors.join(' ');
 if(!result.valid){for(const k of ['revenue','cost','profit','margin'])$('#'+k).textContent='—';$('#revenueVar').textContent=$('#profitVar').textContent='';$('#detail').replaceChildren();$('#bars').replaceChildren();$('#checks').innerHTML='<li>Fix the highlighted inputs to recalculate.</li>';$('#insight').textContent='Calculations are paused until all inputs are valid.';$('#status').textContent='Inputs need attention';return}
 const t=result.totals;
 for(const k of ['revenue','cost','profit'])$('#'+k).textContent=money(t[k]);$('#margin').textContent=t.margin===null?'N/A':t.margin.toFixed(1)+'%';
 $('#revenueVar').textContent=signed(t.revenue-t.budgetRevenue)+' vs sample budget';$('#profitVar').textContent=signed(t.profit-t.budgetProfit)+' vs sample budget';
 const base=M.evaluate(rows()).totals,delta=t.profit-base.profit;
 $('#insight').textContent=(volume===0&&pricing===0?'Base case. ':signed(delta)+' operating profit versus your base inputs. ')+t.visits+' projected appointments across both locations.';
 const max=Math.max(1,...result.locations.flatMap(r=>[r.revenue,r.cost]));
 $('#bars').innerHTML=result.locations.map(r=>`<div class="bar-group"><strong>${r.name}</strong><div class="bar-label"><span>Revenue</span><span>${money(r.revenue)}</span></div><div class="track"><div class="bar" style="width:${r.revenue/max*100}%"></div></div><div class="bar-label"><span>Expenses</span><span>${money(r.cost)}</span></div><div class="track"><div class="bar expense" style="width:${r.cost/max*100}%"></div></div></div>`).join('');
 const row=r=>`<tr><th scope="row">${r.name}</th><td>${r.visits}</td><td>${money(r.revenue)}</td><td>${money(r.cost)}</td><td class="${r.profit<0?'negative':''}">${money(r.profit)}</td><td>${signed(r.profit-r.budgetProfit)}</td><td>${r.breakEven===null?'Not attainable':r.breakEven}</td></tr>`;
 $('#detail').innerHTML=result.locations.map(row).join('')+`<tr><th scope="row">Combined</th><td>${t.visits}</td><td>${money(t.revenue)}</td><td>${money(t.cost)}</td><td>${money(t.profit)}</td><td>${signed(t.profit-t.budgetProfit)}</td><td>By location</td></tr>`;
 const checks=['✓ All required inputs are valid.','✓ Revenue − expenses reconciles to operating profit.','✓ Combined totals equal the two location totals.'];
 result.locations.forEach(r=>{if(r.price<=Math.round(Number(r.supplies)*100))checks.push('Review: '+r.name+' service price does not exceed supply cost.');if(r.visits===0)checks.push('Review: '+r.name+' has no projected appointments.');if(r.profit<0)checks.push('Review: '+r.name+' projects an operating loss.');});
 $('#checks').innerHTML=checks.map(x=>'<li>'+x+'</li>').join('');$('#status').textContent='Scenario calculated · sample data · monthly USD';
}
document.querySelectorAll('input').forEach(x=>x.addEventListener('input',update));
$('#reset').onclick=()=>{M.sample.forEach((r,i)=>{for(const k of ['appointments','price','supplies','fixed'])$('#location-'+i+'-'+k).value=r[k]});$('#volume').value=$('#pricing').value=0;update()};
$('#export').onclick=()=>{if(!result.valid)return;const lines=[['Sample scenario — not actual business results'],['Location','Appointments','Revenue USD','Expenses USD','Operating profit USD','Budget profit USD','Break-even visits']];result.locations.forEach(r=>lines.push([r.name,r.visits,r.revenue/100,r.cost/100,r.profit/100,r.budgetProfit/100,r.breakEven===null?'Not attainable':r.breakEven]));const t=result.totals;lines.push(['Combined',t.visits,t.revenue/100,t.cost/100,t.profit/100,t.budgetProfit/100,'By location']);const csv=lines.map(row=>row.map(x=>'"'+String(x).replaceAll('"','""')+'"').join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='salon-sample-scenario.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};
update();
