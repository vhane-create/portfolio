import {evaluate, cases} from '../npv-irr-model/model.js';
export const seasonality=[6,6,7,7,8,8,8,8,9,10,11,12];
export const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
export function validateImport(data){
  if(data?.schema!=='fpa-expense-bridge-v1'||data.synthetic!==true||!Array.isArray(data.rows)||!data.rows.length)throw Error('Choose a synthetic fpa-expense-bridge-v1 report.');
  const keys=new Set(),years=new Set();let budget=0,actual=0;
  for(const r of data.rows){const key=[r.period,r.department,r.account].join('|');
    if(!/^\d{4}-Q[1-4]$/.test(r.period)||typeof r.department!=='string'||!r.department.trim()||typeof r.account!=='string'||!r.account.trim()||keys.has(key))throw Error('Invalid period, department, account or duplicate expense row.');
    keys.add(key);years.add(r.period.slice(0,4));if(years.size>1)throw Error('Import one reporting year at a time.');for(const k of ['budget','actual'])if(typeof r[k]!=='number'||!Number.isFinite(r[k])||r[k]<0)throw Error('Expense values must be finite nonnegative numbers.');
    budget+=r.budget;actual+=r.actual;
  }
  if(!data.totals||!Number.isFinite(data.totals.budget)||!Number.isFinite(data.totals.actual)||Math.abs(budget-data.totals.budget)>.01||Math.abs(actual-data.totals.actual)>.01)throw Error('Detailed expenses do not reconcile to reported totals.');
  return {budget,actual,variance:actual-budget,rows:data.rows};
}
export function model(v,bridge=null){
  const rev=v.revenue*(1+v.demand/100)*(1+v.price/100);
  let cash=v.cash,previousWc=v.openWc;
  const monthly=months.map((name,i)=>{
    const revenue=rev*seasonality[i]/100,fte=v.headcount+(i+1>=v.hireMonth?v.hires:0);
    const payroll=fte*v.salary*(1+v.benefits/100)/12/1e6;
    // Imported expenses are a subset of plan costs: apply only their variance once, in the quarter close month.
    const adjustment=bridge?bridge.rows.filter(r=>Number(r.period.slice(-1))*3===i+1).reduce((s,r)=>s+r.actual-r.budget,0)/1e6:0;
    const variable=revenue*v.variable/100,fixed=v.fixed/12,expense=variable+fixed+payroll+adjustment,ebitda=revenue-expense;
    const tax=Math.max(0,ebitda)*v.tax/100,closingWc=revenue*v.wc/100,wc=closingWc-previousWc+(i+1===v.investMonth?v.invest*(520000/750000)*Math.max(.01,(1+v.demand/100)*(1+v.price/100))*.1:0);
    const capex=v.capex/12+(i+1===v.investMonth?v.invest:0),debt=v.debt/12;
    const freeCash=ebitda-tax-capex-debt-wc;cash+=freeCash;previousWc=closingWc;
    return {name,rev:revenue,variable,fixed,payroll,adjustment,expense,ebitda,tax,wc,capex,debt,freeCash,cash,fte};
  });
  const total=k=>monthly.reduce((s,m)=>s+m[k],0);
  const r=Object.fromEntries(['rev','variable','payroll','expense','ebitda','tax','wc','freeCash','adjustment'].map(k=>[k,total(k)]));
  r.ending=cash;r.margin=rev===0?0:r.ebitda/rev*100;r.monthly=monthly;r.minimumCash=Math.min(...monthly.map(m=>m.cash));
  r.quarter=Array.from({length:4},(_,i)=>{const rows=monthly.slice(i*3,i*3+3);return {name:'Q'+(i+1),...Object.fromEntries(['rev','expense','ebitda'].map(k=>[k,rows.reduce((s,m)=>s+m[k],0)])),cash:rows[2].cash}});
  // Existing five-year Excel project assumptions, scaled to the proposed investment; its future returns are separate from this year's operating cash forecast.
  const scale=v.invest*1e6/cases.Base.capex;
  r.investment=v.invest>0?evaluate({...cases.Base,capex:v.invest*1e6,revenue:cases.Base.revenue*scale,opex:cases.Base.opex*scale,salvage:cases.Base.salvage*scale,maintenance:30000*scale,revenueScale:Math.max(.01,(1+v.demand/100)*(1+v.price/100)),margin:.65,discount:.12}):null;
  return r;
}
