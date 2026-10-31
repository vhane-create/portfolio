import {cases,shared,evaluate,npv} from './model.js';
const $=id=>document.getElementById(id),keys=['revenue','growth','margin','opex','capex','discount','tax','maintenance','nwc','opexGrowth','salvage'];
const percent=new Set(['growth','margin','discount','tax','nwc','opexGrowth']);
const money=n=>Math.abs(n)<.5?'$0':n<0?'($'+Math.abs(n).toLocaleString('en-US',{maximumFractionDigits:0})+')':'$'+n.toLocaleString('en-US',{maximumFractionDigits:0});
const pct=n=>(n*100).toFixed(1)+'%';let current;
function loadCase(){const a={...shared,...cases[$('case').value]};for(const k of keys)$(k).value=percent.has(k)?+(a[k]*100).toFixed(6):a[k];update(false);}
function svgWrap(label,body){return `<svg viewBox="0 0 560 270" role="img" aria-label="${label}">${body}</svg>`;}
function draw(r){
 const cf=r.flows,max=Math.max(...cf,0),min=Math.min(...cf,0),x=i=>63+i*89,y=v=>28+(max-v)/(max-min)*190,zero=y(0);let s=`<line x1="43" x2="545" y1="${zero}" y2="${zero}" stroke="#9aaabd"/>`;
 for(let i=0;i<6;i++){const top=Math.min(y(cf[i]),zero),height=Math.max(1,Math.abs(y(cf[i])-zero));s+=`<rect x="${x(i)-22}" y="${top}" width="44" height="${height}" fill="${cf[i]<0?'#a75454':'#3d6fa6'}"/><text text-anchor="middle" x="${x(i)}" y="${cf[i]>=0?top-8:top+height+15}">${Math.round(cf[i]/1000)}k</text><text text-anchor="middle" x="${x(i)}" y="254">Year ${i}</text>`;}
 $('cash-chart').innerHTML=svgWrap('Cash flows in thousands of USD for Year 0 through Year 5',s);
 const points=Array.from({length:41},(_,i)=>({rate:i/100,value:npv(i/100,r.flows)}));const vmax=Math.max(0,...points.map(p=>p.value)),vmin=Math.min(0,...points.map(p=>p.value));const yy=v=>25+(vmax-v)/(vmax-vmin||1)*185,xx=t=>68+t/.4*465;
 let p=`<line x1="68" x2="533" y1="${yy(0)}" y2="${yy(0)}" stroke="#9aaabd"/><text x="4" y="${yy(0)+4}">$0</text><text x="4" y="25">${Math.round(vmax/1000)}k</text><text x="4" y="215">${Math.round(vmin/1000)}k</text><polyline points="${points.map(p=>xx(p.rate)+','+yy(p.value)).join(' ')}" fill="none" stroke="#2c62a0" stroke-width="3"/>`;
 for(const d of [0,.1,.2,.3,.4])p+=`<text text-anchor="middle" x="${xx(d)}" y="247">${Math.round(d*100)}%</text>`;
 if(r.assumptions.discount<=.4)p+=`<circle cx="${xx(r.assumptions.discount)}" cy="${yy(r.npv)}" r="5" fill="#14263f"/>`;
 $('npv-chart').innerHTML=svgWrap('NPV curve at discount rates from zero to forty percent',p);
}
function update(edited=true){try{const a={};for(const k of keys){a[k]=$(k).value.trim()===''?NaN:Number($(k).value);if(percent.has(k))a[k]/=100;}const r=evaluate(a);current=r;$('error').hidden=true;$('valid-results').hidden=false;$('analysis').hidden=false;$('npv').textContent=money(r.npv);$('decision').textContent=r.decision+' at '+pct(a.discount);$('irr').textContent=r.irr===null?'Unavailable':pct(r.irr);$('payback').textContent=r.payback===null?'> 5 years':'Year '+r.payback;$('pi').textContent=r.profitabilityIndex.toFixed(2)+'×';$('memo-title').textContent=r.npv>0?'Value-positive under these assumptions.':'Rework the economics before committing capital.';
 $('memo').textContent=`The modeled initial cash outlay is ${money(-r.initial)}, including ${money(r.initialNwc)} of working capital. At a ${pct(a.discount)} hurdle rate, the project produces ${money(r.npv)} of NPV. ${r.npv>0?'Advance to diligence on vendor cost, revenue realization and implementation capacity.':'Review the capital cost, revenue ramp and operating margin. These assumptions do not currently clear the hurdle.'}`;
 $('irr-note').textContent=r.irr===null?'IRR is unavailable because these cash flows do not meet this model’s conventional-flow requirement. Review NPV and the cash flow schedule.':'IRR exceeds the hurdle only when the modeled cash flows support it. NPV remains the primary dollar-value measure.';
 $('case-status').textContent=$('case').value+(edited?' case / edited inputs':' assumptions');
 const row=(name,vals)=>'<tr><th scope="row" style="background:white;color:#14263f">'+name+'</th>'+vals.map(v=>`<td${v<0?' class="negative"':''}>${money(v)}</td>`).join('')+'</tr>';
 $('cash-table').innerHTML=row('Year 0',[0,0,0,0,-a.capex,r.initialNwc,0,r.initial,r.initial])+r.rows.map(t=>row('Year '+t.year,[t.revenue,t.ebitda,-t.taxes,t.depreciation,-t.maintenance,-t.changeNwc,t.release+t.salvage,t.fcf,t.discounted])).join('');
 $('outlay').textContent=`Year 0 working capital is an outflow of ${money(r.initialNwc)}. The table displays this as a negative cash contribution. Discounting includes Year 0 exactly once. All dollar displays are rounded; calculations retain full precision.`;
 // Match the Year 0 cash sign with the annual change-in-WC cash contribution column.
 $('cash-table').firstElementChild.children[6].textContent=money(-r.initialNwc);
 draw(r);
 }catch(e){current=null;$('error').textContent=e.message;$('error').hidden=false;$('valid-results').hidden=true;$('analysis').hidden=true;}}
 $('inputs').addEventListener('submit',e=>e.preventDefault());for(const k of keys)$(k).addEventListener('input',()=>update());$('case').addEventListener('change',loadCase);$('reset').addEventListener('click',loadCase);
 $('export').addEventListener('click',()=>{if(!current)return;const head=['Year','Revenue','EBITDA','Depreciation','Cash taxes','Maintenance capex','Change in NWC','NWC recovery','After-tax disposal','Free cash flow','PV of cash flow'];const rows=[[0,0,0,0,0,currCapex(),current.initialNwc,0,0,current.initial,current.initial],...current.rows.map(t=>[t.year,t.revenue,t.ebitda,t.depreciation,t.taxes,t.maintenance,t.changeNwc,t.release,t.salvage,t.fcf,t.discounted])];const csv=[head.join(','),...rows.map(r=>r.join(','))].join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='NPV_IRR_'+$('case').value+'_cash_flows.csv';a.click();URL.revokeObjectURL(url);});
 function currCapex(){return current.assumptions.capex;}
 loadCase();
