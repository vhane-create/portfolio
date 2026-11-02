import assert from 'node:assert/strict';
import fs from 'node:fs';
import {model,validateImport,seasonality} from './model.mjs';
const v={revenue:120,demand:0,price:0,variable:38,fixed:24,headcount:220,salary:95000,benefits:28,cash:18,tax:20,capex:5,debt:3,wc:20,openWc:2.88,floor:8,hires:0,hireMonth:1,invest:0,investMonth:4};
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
assert.equal(seasonality.reduce((a,b)=>a+b),100);
const r=model(v);close(r.rev,120);close(r.payroll,26.752);close(r.ebitda,23.648);close(r.wc,0);close(r.ending,28.9184);
for(const key of ['rev','expense','ebitda']){close(r.monthly.reduce((s,m)=>s+m[key],0),r[key]);close(r.quarter.reduce((s,m)=>s+m[key],0),r[key]);}
close(r.monthly[0].rev,7.2);close(r.monthly[11].rev,14.4);close(r.ending,v.cash+r.freeCash);
const early=model({...v,hires:20}),late=model({...v,hires:20,hireMonth:10});close(early.payroll-late.payroll,20*95000*1.28*.75/1e6);
const bridge=validateImport(JSON.parse(fs.readFileSync(new URL('../finance-automation/output/forecast_bridge.json',import.meta.url))));
close(bridge.variance,101000);const connected=model(v,bridge);close(connected.expense-r.expense,.101);close(connected.adjustment,.101);
const tampered={schema:'fpa-expense-bridge-v1',synthetic:true,rows:bridge.rows,totals:{budget:0,actual:0}};assert.throws(()=>validateImport(tampered),/reconcile/);
assert.throws(()=>validateImport({...tampered,rows:[...bridge.rows,bridge.rows[0]]}),/duplicate/);
const business=model({...v,demand:-12,salary:102600,hires:20,invest:3});assert.ok(business.investment);close(business.investment.initial,-3e6-business.investment.initialNwc);close(business.monthly[3].capex,5/12+3);assert.ok(business.minimumCash<=business.ending);
close(model({...v,revenue:0}).rev,0);assert.ok(Number.isFinite(model({...v,revenue:0}).ending));
console.log('PASS: annual reconciliation, seasonal revenue, hiring timing, cash roll-forward, imported variance, invalid imports and investment funding.');
console.log(JSON.stringify({baseline:{ebitda:r.ebitda,cash:r.ending},business:{ebitda:business.ebitda,minCash:business.minimumCash,npv:business.investment.npv,irr:business.investment.irr},deferred:model({...v,demand:-12,salary:102600,hires:20,invest:3,hireMonth:10}).ending},null,2));
