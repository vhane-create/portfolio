import assert from 'node:assert/strict';
import {evaluate,adjustmentGroups} from './model.mjs';
const close=(a,b)=>assert.ok(Math.abs(a-b)<.000001,`${a} != ${b}`);
const base=evaluate();close(base.netIncome,14790);close(base.balances['1000'],44250);close(base.assets,141990);close(base.cfo,1250);close(base.balances['1220'],7000);close(base.balances['1200'],13000);close(base.balances['1100'],32000);close(base.balances['1110'],-960);assert.ok(base.checks.every(x=>Math.abs(x[1])<.001));
const omitDep=evaluate({},adjustmentGroups.map(g=>g[0]).filter(g=>g!=='depreciation'));close(omitDep.netIncome-base.netIncome,800);assert.ok(omitDep.checks.every(x=>Math.abs(x[1])<.001));assert.equal(omitDep.complete,false);
const omitBank=evaluate({},adjustmentGroups.map(g=>g[0]).filter(g=>g!=='bank'));close(omitBank.checks.find(x=>x[0]==='Adjusted bank less ledger cash')[1],-50);
const omitOh=evaluate({},adjustmentGroups.map(g=>g[0]).filter(g=>g!=='overhead'));close(omitOh.balances['5100'],500);
close(evaluate({allowance:.05}).netIncome,14150);close(evaluate({wages:0}).netIncome,15990);close(evaluate({bankFee:200}).balances['1000'],44150);
for(let mask=0;mask<128;mask++){const chosen=adjustmentGroups.filter((g,i)=>mask&(1<<i)).map(g=>g[0]);const r=evaluate({},chosen);for(const [name,value] of r.checks.slice(0,5))close(value,0);}
assert.throws(()=>evaluate({wages:-1}));assert.throws(()=>evaluate({allowance:1.1}));assert.throws(()=>evaluate({wages:NaN}));assert.throws(()=>evaluate({insurance:6001}));
console.log('PASS: independent baseline totals; 128 close combinations; omitted entries; zero and changed inputs; invalid input rejection.');
