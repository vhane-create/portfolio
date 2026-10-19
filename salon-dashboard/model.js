(function(root){
  const sample = [
    {name:'Springfield, Missouri',appointments:160,price:95,supplies:18,fixed:5200,budgetRevenue:15000,budgetProfit:7000},
    {name:'Springfield, Illinois',appointments:100,price:105,supplies:21,fixed:4100,budgetRevenue:11000,budgetProfit:4500}
  ];
  const limits={appointments:2000,price:2000,supplies:2000,fixed:100000};
  const cents=n=>Math.round((n+Number.EPSILON)*100);
  function evaluate(rows,volume=0,pricing=0){
    let errors=[];
    if(!Number.isFinite(volume)||volume< -50||volume>50||!Number.isFinite(pricing)||pricing< -25||pricing>25)errors.push('Scenario adjustments are outside the allowed range.');
    rows.forEach(r=>Object.keys(limits).forEach(k=>{const x=r[k];if(x===''||x===null||!Number.isFinite(Number(x))||Number(x)<0||Number(x)>limits[k]||(k==='appointments'&&!Number.isInteger(Number(x))))errors.push(r.name+': '+k+' must be '+(k==='appointments'?'a whole number':'a number')+' between 0 and '+limits[k]+'.');}));
    if(errors.length)return {valid:false,errors};
    const locations=rows.map(r=>{const visits=Math.round(Number(r.appointments)*(1+volume/100)),price=cents(Number(r.price)*(1+pricing/100)),unitCost=cents(Number(r.supplies)),fixed=cents(Number(r.fixed)),revenue=visits*price,variable=visits*unitCost,cost=variable+fixed,profit=revenue-cost,contribution=price-unitCost;
      return {...r,visits,price,revenue,variable,fixed,cost,profit,margin:revenue?profit/revenue*100:null,breakEven:contribution>0?Math.ceil(fixed/contribution):null,budgetRevenue:cents(r.budgetRevenue),budgetProfit:cents(r.budgetProfit)};
    });
    const totals=locations.reduce((t,r)=>{for(const k of ['visits','revenue','variable','fixed','cost','profit','budgetRevenue','budgetProfit'])t[k]+=r[k];return t;},{visits:0,revenue:0,variable:0,fixed:0,cost:0,profit:0,budgetRevenue:0,budgetProfit:0});
    totals.margin=totals.revenue?totals.profit/totals.revenue*100:null;
    return {valid:true,errors:[],locations,totals};
  }
  const api={sample,evaluate};if(typeof module!=='undefined')module.exports=api;else root.SalonModel=api;
})(typeof window!=='undefined'?window:globalThis);
