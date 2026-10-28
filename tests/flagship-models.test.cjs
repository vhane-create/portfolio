// Dependency-free model regression checks. Run: node tests/flagship-models.test.cjs
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const cases=[
['three-statement-forecast',[120,8,65,25,20,15,10,45,30,8,5,25,6,3],r=>{assert.ok(r.check);assert.ok(Math.abs(r.rows.at(-2)[1]-r.rows.at(-1)[1])<1e-7);assert.ok(Math.abs(r.metrics[0][1]-129.6)<1e-8)}],
['global-consolidation',[90,45,1.1,65,32,8,8],r=>{assert.ok(r.check);assert.ok(Math.abs(r.metrics[0][1]-131.5)<1e-8);assert.ok(Math.abs(r.metrics[2][1]-31.3)<1e-8)}],
['workforce-planning',[220,95000,28,25,7,8,4,29],r=>{assert.ok(r.check);assert.ok(Math.abs(r.metrics[0][1]-227.4)<1e-8)}],
['financial-controls-sox',[2500000,2495000,4000,2500,1,1],r=>{assert.ok(r.check);assert.equal(r.metrics[0][1],1000)}],
['treasury-liquidity',[16,5,4.8,10,8,0.35],r=>{assert.equal(r.rows.length,14);assert.ok(Math.abs(r.metrics[0][1]-7.55)<1e-8);assert.equal(r.check,false)}],
['enterprise-data-pipeline',[10000,325,2,1,205,100000],r=>{assert.ok(r.check);assert.equal(r.metrics[0][1],9700);assert.equal(r.metrics[1][1],300)}]
];
let passed=0;for(const [slug,defaults,verify] of cases){const html=fs.readFileSync(path.join(__dirname,'..',slug,'index.html'),'utf8');const match=html.match(/function calculate\(v\)\{([\s\S]*?)\}function render\(/);assert.ok(match,slug+': calculation function found');const calculate=vm.runInNewContext('(function(v){'+match[1]+'})');const result=calculate(defaults);assert.ok(result.metrics.length>0&&result.rows.length>0,slug+': populated results');for(const [,value] of [...result.metrics,...result.rows])assert.ok(Number.isFinite(value),slug+': finite outputs');verify(result);const changed=defaults.slice();changed[0]+=Math.max(1,Math.abs(changed[0])*.1);const other=calculate(changed);assert.ok(other.metrics.some(([name,value],i)=>value!==result.metrics[i][1]),slug+': responds to input changes');console.log('PASS '+slug);passed++}console.log(passed+' flagship model regression checks passed.');
