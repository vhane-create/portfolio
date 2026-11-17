export const accounts = [
 ['1000','Cash','asset'],['1100','Accounts receivable','asset'],['1110','Allowance for credit losses','contraAsset'],['1200','Medical supplies','asset'],['1300','Prepaid insurance','asset'],['1500','Equipment','asset'],['1510','Accumulated depreciation','contraAsset'],['2000','Accounts payable','liability'],['2100','Accrued payroll','liability'],['2500','Loan payable','liability'],['3000','Opening equity','equity'],['3100','Owner distributions','distribution'],['4000','Gross service revenue','revenue'],['4100','Contractual adjustments','contraRevenue'],['5000','Payroll expense','expense'],['5100','Occupancy expense','expense'],['5200','Supplies expense','expense'],['5300','Insurance expense','expense'],['5400','Depreciation expense','expense'],['5500','Credit loss expense','expense'],['5600','Interest expense','expense'],['5700','Bank fees','expense'],['4200','Interest income','revenue']
];
export const opening = Object.fromEntries(Object.entries({'1000':40000,'1100':18000,'1200':3000,'1300':6000,'1500':60000,'1510':-12000,'2000':-7000,'2500':-30000,'3000':-78000}).map(([k,v])=>[k,v*1000]));
export const invoices = [
 {id:'INS-OPEN',payer:'Insurance A',issued:'2026-09-01',due:'2026-10-01',gross:12000,contract:0,paid:12000,opening:true,lossRate:0},
 {id:'PAT-OPEN',payer:'Patient pool A',issued:'2026-10-01',due:'2026-10-15',gross:6000,contract:0,paid:3000,opening:true,lossRate:.4},
 {id:'INS-NOV',payer:'Insurance B',issued:'2026-11-01',due:'2026-11-30',gross:70000,contract:25000,paid:30000,opening:false,lossRate:.02},
 {id:'PAT-NOV',payer:'Patient pool B',issued:'2026-11-01',due:'2026-11-20',gross:20000,contract:0,paid:12000,opening:false,lossRate:.1}
].map(i=>({...i,gross:i.gross*1000,contract:i.contract*1000,paid:i.paid*1000}));
export const defaults={payroll:3500000,supplies:2200000,bankFee:75000};
export const network={annualPatients:2400000,monthlyPatients:300000,encounters:400000,employees:5000,locations:480,regions:4};
export const adjustments=[['contract','Contractual revenue adjustment','ADJ-01'],['supplies','Supplies consumption','ADJ-02'],['insurance','Insurance amortization','ADJ-03'],['payroll','Payroll accrual','ADJ-04'],['depreciation','Equipment depreciation','ADJ-05'],['allowance','Receivables allowance','ADJ-06'],['bank','Bank fee and interest','ADJ-07']];
export function model(inputs=defaults, enabled=adjustments.map(a=>a[0])){
 const p={...defaults,...inputs}; for(const key of Object.keys(defaults)) if(!Number.isFinite(p[key])||p[key]<0)throw new Error('Enter a nonnegative number for '+key); if(p.supplies>7000000)throw new Error('Ending supplies cannot exceed $7,000,000 available.');
 const active=new Set(enabled), journal=[];
 function entry(id,date,description,source,lines,group='operating'){lines.forEach(([account,debit,credit])=>journal.push({id,date,description,source,group,account,debit,credit}));}
 entry('OPEN','2026-10-31','Opening balances','OB-01',Object.entries(opening).map(([a,v])=>[a,Math.max(v,0),Math.max(-v,0)]),'opening');
 entry('J01','2026-11-01','Insurance services billed','INS-NOV',[['1100',70000000,0],['4000',0,70000000]]);
 entry('J02','2026-11-01','Patient services billed','PAT-NOV',[['1100',20000000,0],['4000',0,20000000]]);
 invoices.forEach((i,n)=>entry('J0'+(n+3),'2026-11-18','Collection: '+i.id,'RCPT-0'+(n+1),[['1000',i.paid,0],['1100',0,i.paid]]));
 entry('J07','2026-11-20','Payroll paid','PAY-01',[['5000',26000000,0],['1000',0,26000000]]);
 entry('J08','2026-11-02','Monthly rent paid','RENT-01',[['5100',4500000,0],['1000',0,4500000]]);
 entry('J09','2026-11-12','Supplies received on account','SUP-01',[['1200',4000000,0],['2000',0,4000000]]);
 entry('J10','2026-11-22','Vendor balances paid','AP-01',[['2000',5000000,0],['1000',0,5000000]]);
 entry('J11','2026-11-24','Equipment purchased','CAP-01',[['1500',6000000,0],['1000',0,6000000]]);
 entry('J12','2026-11-25','Loan principal and interest paid','DEBT-01',[['2500',2000000,0],['5600',300000,0],['1000',0,2300000]]);
 entry('J13','2026-11-26','Owner distribution','DIST-01',[['3100',2000000,0],['1000',0,2000000]]);
 entry('J14','2026-11-01','Second insurance policy purchased','INSURANCE-01',[['1300',6000000,0],['1000',0,6000000]]);
 const aging=invoices.map(i=>({...i,net:i.gross-i.contract,balance:i.gross-i.contract-i.paid,days:Math.max(0,Math.round((Date.parse('2026-11-30')-Date.parse(i.due))/86400000))}));
 const allowance=aging.reduce((s,i)=>s+i.balance*i.lossRate,0);
 if(active.has('contract'))entry('A01','2026-11-30','Contractual reduction to billed fees','ADJ-01',[['4100',25000000,0],['1100',0,25000000]],'adjustment');
 if(active.has('supplies'))entry('A02','2026-11-30','Supplies used per physical count','ADJ-02',[['5200',7000000-p.supplies,0],['1200',0,7000000-p.supplies]],'adjustment');
 if(active.has('insurance'))entry('A03','2026-11-30','One month of two insurance policies','ADJ-03',[['5300',1000000,0],['1300',0,1000000]],'adjustment');
 if(active.has('payroll'))entry('A04','2026-11-30','Unpaid November payroll','ADJ-04',[['5000',p.payroll,0],['2100',0,p.payroll]],'adjustment');
 if(active.has('depreciation'))entry('A05','2026-11-30','Monthly depreciation schedule','ADJ-05',[['5400',1000000,0],['1510',0,1000000]],'adjustment');
 if(active.has('allowance'))entry('A06','2026-11-30','Expected losses by receivable pool','ADJ-06',[['5500',allowance,0],['1110',0,allowance]],'adjustment');
 if(active.has('bank')){entry('A07','2026-11-30','Statement fee','ADJ-07',[['5700',p.bankFee,0],['1000',0,p.bankFee]],'adjustment');entry('A08','2026-11-30','Statement interest earned','ADJ-07',[['1000',25000,0],['4200',0,25000]],'adjustment');}
 const balances=Object.fromEntries(accounts.map(([a])=>[a,0]));journal.forEach(j=>balances[j.account]+=j.debit-j.credit);
 const sumType=t=>accounts.filter(a=>t.includes(a[2])).reduce((s,[a])=>s+balances[a],0);
 const revenue=-sumType(['revenue','contraRevenue']),expenses=sumType(['expense']),profit=revenue-expenses;
 const assets=sumType(['asset','contraAsset']),liabilities=-sumType(['liability']),equity=-sumType(['equity'])-sumType(['distribution'])+profit;
 const bankStatement=44700000-p.bankFee+25000; const transit=3000000,outstanding=2500000, bankAdjusted=bankStatement+transit-outstanding;
 const cash=balances['1000']; const cfoDirect=57000000-26000000-4500000-5000000-6000000-300000-(active.has('bank')?p.bankFee-25000:0);
 const cfoIndirect=profit-balances['1510']+opening['1510']-balances['1110']-(balances['1100']-opening['1100'])-(balances['1200']-opening['1200'])-(balances['1300']-opening['1300'])-(balances['2000']-opening['2000'])-balances['2100'];
 const tb=accounts.map(([id,name,type])=>({id,name,type,balance:balances[id],debit:Math.max(0,balances[id]),credit:Math.max(0,-balances[id])}));
 const checks=[['Journal debits less credits',journal.reduce((s,j)=>s+j.debit-j.credit,0)],['Assets less liabilities and equity',assets-liabilities-equity],['Book cash less adjusted bank',cash-bankAdjusted],['Receivables ledger less subledger',balances['1100']-aging.reduce((s,i)=>s+i.balance,0)],['Direct less indirect operating cash flow',cfoDirect-cfoIndirect],['Cash movement less statement movement',cash-40000000-(cfoDirect-6000000-4000000)]];
 return {inputs:p,enabled:[...active],journal,balances,aging,allowance,revenue,expenses,profit,assets,liabilities,equity,cash,bankStatement,transit,outstanding,bankAdjusted,cfoDirect,cfoIndirect,investing:-6000000,financing:-4000000,tb,checks,complete:adjustments.every(([k])=>active.has(k))&&checks.every(([,v])=>Math.abs(v)<.005)};
}
export const csv=rows=>rows.map(r=>r.map(c=>'"'+String(c??'').replaceAll('"','""')+'"').join(',')).join('\r\n');
