const assert=require('node:assert/strict');
const {sample,evaluate}=require('./model.js');
const clone=()=>sample.map(x=>({...x}));
let r=evaluate(clone());
assert.equal(r.valid,true);assert.equal(r.totals.revenue,2570000);assert.equal(r.totals.cost,1428000);assert.equal(r.totals.profit,1142000);assert.equal(r.locations[0].breakEven,68);
r=evaluate(clone(),10,10);assert.equal(r.locations[0].visits,176);assert.equal(r.locations[0].revenue,1839200);assert.equal(r.totals.profit,r.totals.revenue-r.totals.cost);
let a=clone();a[0].appointments='';assert.equal(evaluate(a).valid,false);
a=clone();a[0].price=-1;assert.equal(evaluate(a).valid,false);
a=clone();a[0].appointments=1.5;assert.equal(evaluate(a).valid,false);
a=clone();a[0].price=Infinity;assert.equal(evaluate(a).valid,false);
a=clone();a[0].price=10;a[0].supplies=20;r=evaluate(a);assert.equal(r.locations[0].breakEven,null);assert.ok(r.locations[0].profit<0);
a=clone();a.forEach(x=>x.appointments=0);r=evaluate(a);assert.equal(r.totals.revenue,0);assert.equal(r.totals.margin,null);assert.equal(r.totals.profit,-930000);
assert.equal(evaluate(clone(),51).valid,false);
for(const v of [-50,0,50])for(const p of [-25,0,25]){r=evaluate(clone(),v,p);assert.equal(r.totals.profit,r.locations.reduce((s,x)=>s+x.profit,0));assert.equal(r.totals.cost,r.totals.fixed+r.totals.variable)}
console.log('PASS: base totals, scenario math, reconciliation, validation, zero revenue, losses, break-even, boundary scenarios.');
