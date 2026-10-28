const {test}=require('node:test');
const assert=require('node:assert/strict');
const {create}=require('./conversation.js');

test('natural wording, either amount order, revenue and expense conventions',()=>{
 const c=create();
 assert.match(c.answer('Budget revenue is $100,000; actual is $90,000.'),/\$-10,000.00.*-10.00%.*unfavorable/);
 assert.match(c.answer('Actual expenses: $90,000; budget: $100,000'),/favorable/);
 assert.match(c.answer('actual 120000, budget 100000'),/20.00%/);
});
test('follow-up retains figures but does not invent a cause',()=>{
 const c=create();c.answer('Budget revenue is $100,000; actual is $90,000.');
 const why=c.answer('Why did that happen?');assert.match(why,/\$90,000.00/);assert.match(why,/not its cause/);
 const scenario=c.answer('What if actual revenue increases 10% from $90,000?');
 assert.match(scenario,/\$99,000.00/);assert.match(scenario,/\$1,000.00 shortfall/);
 assert.match(c.answer('What if revenue increases 20%?'),/\$108,000.00/);
});
test('topic change and simplification use last answer',()=>{
 const c=create();c.answer('actual revenue 90000, budget 100000');
 assert.match(c.answer('Explain cash flow versus profit.'),/credit sale/);
 assert.match(c.answer('Explain that more simply.'),/Profit is what you earn/);
 assert.match(c.answer('What if revenue increases 10%?'),/What actual amount/);
});
test('zero budget, decimal cents, missing amount, and large numbers',()=>{
 const c=create();assert.match(c.answer('actual 10, budget 0'),/undefined/);
 assert.match(c.answer('actual $0.30, budget $0.10'),/\$0.20/);
 assert.match(c.answer('budget revenue $100'),/What actual/);
 assert.match(c.answer('actual 999999999999999999, budget 100'),/supported calculation range/);
 assert.match(c.answer('actual €90, budget €100')||'',/^$/); // unsupported notation is not silently parsed
 assert.match(c.answer('actual EUR 90, budget EUR 100')||'',/^$/);
 assert.match(c.answer('actual $90, budget $100 in GBP'),/currently uses USD/);
});
test('session isolation, reset, bounded history, defensive copy',()=>{
 const a=create(),b=create();a.answer('actual revenue 90000, budget 100000');
 assert.match(b.answer('Why did that happen?'),/Which result/);
 const copy=a.messages();copy[0].content='changed';assert.notEqual(a.messages()[0].content,'changed');
 a.reset();assert.deepEqual(a.messages(),[]);assert.match(a.answer('Why?'),/Which result/);
 for(let i=0;i<20;i++)a.answer('Hello');assert.equal(a.messages().length,20);
});
test('budget scenario is clarified instead of changing actual by mistake',()=>{
 const c=create();c.answer('actual revenue 90000, budget 100000');
 assert.match(c.answer('What if budget increases 10%?'),/Should I change/);
});
