import test from 'node:test';
import assert from 'node:assert/strict';
import {cases,shared,evaluate,npv,irr} from './model.js';
const near=(a,b,tol=1e-7)=>assert.ok(Math.abs(a-b)<=tol,`${a} vs ${b}`);
test('NPV time zero and known IRR',()=>{near(npv(.10,[-100,110]),0);near(irr([-100,110]),.10);});
test('base reconciles to an independent five-year calculation',()=>{
 const r=evaluate(cases.Base);near(r.initial,-802000);near(r.rows[0].fcf,186000);
 const expected=[-802000];let prior=52000;
 for(let t=0;t<5;t++){const rev=520000*1.08**t,ebit=rev*.65-100000*1.03**t-150000;const wc=rev*.1;expected.push(ebit-Math.max(ebit,0)*.25+150000-30000-(wc-prior)+(t===4?wc+75000:0));prior=wc;}
 expected.forEach((v,i)=>near(v,r.flows[i]));near(r.npv,expected.reduce((s,v,t)=>s+v/1.12**t,0));near(npv(r.irr,r.flows),0,1e-6);
 near(r.rows[4].release,r.rows[4].closingNwc);near(r.rows[4].salvage,75000);near(r.profitabilityIndex,(r.npv+802000)/802000);
});
test('all cases evaluate and downside reduces NPV',()=>{const b=evaluate(cases.Base),d=evaluate(cases.Downside),u=evaluate(cases.Upside);assert.ok(d.npv<b.npv&&b.npv<u.npv);});
test('discount, revenue and initial investment controls affect valuation',()=>{const b=evaluate(cases.Base);assert.ok(evaluate({...cases.Base,discount:.20}).npv<b.npv);assert.ok(evaluate({...cases.Base,revenueScale:1.1}).npv>b.npv);assert.ok(evaluate({...cases.Base,capex:900000}).npv<b.npv);});
test('zero revenue gives losses, no false payback and no unsupported IRR',()=>{const r=evaluate({...cases.Base,revenue:0,salvage:0});assert.ok(r.npv<0);assert.equal(r.irr,null);assert.equal(r.payback,null);assert.equal(r.rows[0].taxes,0);});
test('tax, working capital and discount zero retain their meaning',()=>{const r=evaluate({...cases.Base,tax:0,nwc:0,discount:0});near(r.initial,-750000);near(r.npv,r.flows.reduce((s,v)=>s+v,0));assert.equal(r.initialNwc,0);assert.equal(r.rows[4].release,0);});
test('invalid inputs are rejected',()=>{for(const patch of [{revenue:NaN},{capex:0},{margin:1.1},{discount:-.1},{growth:-1},{revenueScale:0}])assert.throws(()=>evaluate({...cases.Base,...patch}));});
