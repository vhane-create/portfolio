import assert from 'node:assert/strict';
import {model,defaults,adjustments} from './model.mjs';
const base=model();
assert.equal(base.profit,21550000);assert.equal(base.cash,45150000);assert.equal(base.assets,135050000);assert.equal(base.liabilities,37500000);assert.equal(base.equity,97550000);assert.equal(base.cfoDirect,15150000);assert.equal(base.balances['1100'],26000000);assert.equal(base.allowance,2300000);assert.equal(base.complete,true);
for(let mask=0;mask<128;mask++){
 const keys=adjustments.filter((_,i)=>mask&(1<<i)).map(a=>a[0]),m=model(defaults,keys);
 for(const name of ['Journal debits less credits','Assets less liabilities and equity','Direct less indirect operating cash flow','Cash movement less statement movement'])assert.equal(m.checks.find(c=>c[0]===name)[1],0);
 assert.equal(m.complete,mask===127);
 assert.equal(m.checks[2][1],keys.includes('bank')?0:50000);
 assert.equal(m.checks[3][1],keys.includes('contract')?0:25000000);
}
const payroll=model({...defaults,payroll:4500000});assert.equal(payroll.profit,20550000);assert.equal(payroll.cash,base.cash);assert.equal(payroll.cfoDirect,payroll.cfoIndirect);
const fee=model({...defaults,bankFee:0});assert.equal(fee.cash,45225000);assert.equal(fee.profit,21625000);assert.equal(fee.checks[2][1],0);
const supplies=model({...defaults,supplies:0});assert.equal(supplies.profit,19350000);assert.equal(supplies.cash,base.cash);assert.equal(supplies.cfoDirect,supplies.cfoIndirect);
assert.throws(()=>model({...defaults,payroll:NaN}));assert.throws(()=>model({...defaults,bankFee:-1}));assert.throws(()=>model({...defaults,supplies:7000001}));
const groups=new Map();for(const j of base.journal)groups.set(j.id,(groups.get(j.id)||0)+j.debit-j.credit);for(const v of groups.values())assert.equal(v,0);
console.log('Verified baseline, each posting batch, all 128 adjustment combinations, revised estimates, zero values and invalid inputs.');
