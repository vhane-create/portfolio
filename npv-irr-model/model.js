export const cases = {
  Base: {revenue:520000,growth:.08,margin:.65,opex:100000,capex:750000,salvage:100000},
  Downside: {revenue:440000,growth:.03,margin:.60,opex:115000,capex:825000,salvage:75000},
  Upside: {revenue:600000,growth:.12,margin:.68,opex:95000,capex:725000,salvage:120000}
};
export const shared = {discount:.12,tax:.25,maintenance:30000,nwc:.10,opexGrowth:.03,revenueScale:1};
export function npv(rate,flows) {return flows.reduce((s,c,t)=>s+c/Math.pow(1+rate,t),0);}
export function irr(flows) {
  if (!(flows[0]<0) || flows.slice(1).some(c=>c<0) || !flows.slice(1).some(c=>c>0)) return null;
  let lo=-.9999,hi=1;
  while(npv(hi,flows)>0 && hi<1e8) hi=hi*2+1;
  if(npv(hi,flows)>0) return null;
  for(let i=0;i<160;i++){const m=(lo+hi)/2;if(npv(m,flows)>0)lo=m;else hi=m;}
  return (lo+hi)/2;
}
export function evaluate(input) {
  const a={...shared,...input};
  for(const [k,v] of Object.entries(a)) if(!Number.isFinite(v)) throw new Error(`Enter a number for ${k}.`);
  for(const k of ['revenue','opex','maintenance','salvage']) if(a[k]<0) throw new Error(`${k} must be zero or greater.`);
  if(a.capex<=0)throw new Error('Initial capital expenditure must be greater than zero.');
  if(a.discount<0 || a.discount>1)throw new Error('Discount rate must be between 0% and 100%.');
  if(a.growth<-.9 || a.growth>1 || a.opexGrowth<-.9 || a.opexGrowth>1)throw new Error('Annual growth must be between -90% and 100%.');
  for(const k of ['margin','tax','nwc']) if(a[k]<0||a[k]>1)throw new Error(`${k} must be between 0% and 100%.`);
  if(a.revenueScale<=0||a.revenueScale>3)throw new Error('Revenue multiplier must be greater than zero and no more than 3.');
  const firstRevenue=a.revenue*a.revenueScale, initialNwc=firstRevenue*a.nwc;
  const initial=-(a.capex+initialNwc), flows=[initial], rows=[];
  let prevNwc=initialNwc,cumulative=initial,payback=null;
  for(let year=1;year<=5;year++){
    const revenue=firstRevenue*(1+a.growth)**(year-1),grossProfit=revenue*a.margin;
    const opex=a.opex*(1+a.opexGrowth)**(year-1), ebitda=grossProfit-opex;
    const depreciation=a.capex/5,ebit=ebitda-depreciation,taxes=Math.max(ebit,0)*a.tax;
    const operatingCash=ebit-taxes+depreciation,closingNwc=revenue*a.nwc,changeNwc=closingNwc-prevNwc;
    const release=year===5?closingNwc:0,salvage=year===5?a.salvage*(1-a.tax):0;
    const fcf=operatingCash-a.maintenance-changeNwc+release+salvage;
    const discounted=fcf/(1+a.discount)**year;cumulative+=fcf;
    if(payback===null&&cumulative>=0)payback=year;
    rows.push({year,revenue,grossProfit,opex,ebitda,depreciation,ebit,taxes,operatingCash,maintenance:a.maintenance,closingNwc,changeNwc,release,salvage,fcf,discounted,cumulative});
    flows.push(fcf);prevNwc=closingNwc;
  }
  const value=npv(a.discount,flows),rate=irr(flows);
  return {assumptions:a,initial,initialNwc,flows,rows,npv:value,irr:rate,payback,profitabilityIndex:(value-initial)/-initial,decision:value>0?'Creates value':value<0?'Does not meet hurdle':'At break-even'};
}
