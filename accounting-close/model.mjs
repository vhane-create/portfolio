export const accounts=[
['1000','Cash','asset',50000],['1100','Accounts receivable','asset',12000],['1110','Allowance for doubtful accounts','contra',0],['1200','Raw materials','asset',10000],['1210','Work in process','asset',0],['1220','Finished goods','asset',8000],['1300','Prepaid insurance','asset',6000],['1500','Equipment','asset',48000],['1510','Accumulated depreciation','contra',-12000],['2000','Accounts payable','liability',-14000],['2100','Wages payable','liability',-2000],['2200','Deferred service revenue','liability',0],['2500','Loan payable','liability',-20000],['3000','Member capital','equity',-80000],['3100','Opening retained earnings','equity',-6000],['4000','Product revenue','revenue',0],['4100','Service revenue','revenue',0],['4200','Interest income','income',0],['5000','Cost of goods sold','cogs',0],['5100','Manufacturing overhead control','asset',0],['6000','Office salaries','expense',0],['6100','Rent expense','expense',0],['6200','Insurance expense','expense',0],['6300','Depreciation expense','expense',0],['6400','Bad debt expense','expense',0],['6500','Bank fees','expense',0],['6600','Interest expense','interest',0]];
export const adjustmentGroups=[['insurance','Insurance expiry'],['depreciation','Depreciation'],['wages','Accrued office wages'],['allowance','Receivables allowance'],['earned','Earned service revenue'],['overhead','Underapplied manufacturing overhead'],['bank','Bank fee and interest']];
export const defaults={insurance:500,depreciation:800,wages:1200,allowance:.03,earned:1000,bankFee:100,bankInterest:50};
export function evaluate(overrides={},selected=adjustmentGroups.map(g=>g[0])){
const v={...defaults,...overrides};for(const[k,x]of Object.entries(v))if(!Number.isFinite(x)||x<0)throw Error(k+' must be a finite nonnegative number.');
if(v.allowance>1||v.earned>4000||v.insurance>6000)throw Error('Allowance must be 0–100%, earned revenue cannot exceed $4,000 and insurance expiry cannot exceed $6,000.');
const active=new Set(selected),journal=[];
function entry(id,date,description,lines,group='operating',evidence='Synthetic case document'){
 const rows=lines.map(([account,debit,credit])=>({id,date,description,account,debit:debit||0,credit:credit||0,group,evidence}));
 if(Math.abs(rows.reduce((s,l)=>s+l.debit-l.credit,0))>.00001)throw Error(id+' is not balanced');journal.push(...rows);
}
entry('T01','2026-10-02','Purchase raw materials on credit',[['1200',12000,0],['2000',0,12000]],'operating','Supplier invoice RM-102');
entry('T02','2026-10-04','Collect opening customer invoices',[['1000',10000,0],['1100',0,10000]],'operating','Customer remittance CR-104');
entry('T03','2026-10-06','Pay suppliers',[['2000',9000,0],['1000',0,9000]],'operating','Payment batch AP-106');
entry('T04','2026-10-07','Pay opening wages payable',[['2100',2000,0],['1000',0,2000]],'operating','Payroll settlement PR-107');
entry('T05','2026-10-10','Issue materials to production',[['1210',9000,0],['1200',0,9000]],'operating','Materials issue MI-110');
entry('T06','2026-10-12','Pay direct production labor',[['1210',6000,0],['1000',0,6000]],'operating','Production time report PT-112');
entry('T07','2026-10-15','Record actual factory overhead',[['5100',5500,0],['1000',0,4500],['2000',0,1000]],'operating','Factory overhead register FO-115');
entry('T08','2026-10-17','Apply overhead at $25 per unit × 200 units',[['1210',5000,0],['5100',0,5000]],'operating','Normal-capacity allocation OA-117');
entry('T09','2026-10-20','Complete 200 units at $100 per unit',[['1220',20000,0],['1210',0,20000]],'operating','Production completion PC-120');
entry('T10','2026-10-22','Cash sale: 80 units × $200',[['1000',16000,0],['4000',0,16000]],'operating','Sales invoice SI-122');
entry('T11','2026-10-24','Credit sale: 150 units × $200',[['1100',30000,0],['4000',0,30000]],'operating','Sales invoice SI-124');
entry('T12','2026-10-24','FIFO cost: 100 opening units × $80 + 130 units × $100',[['5000',21000,0],['1220',0,21000]],'operating','FIFO inventory schedule IC-124');
entry('T13','2026-10-25','Pay office salaries',[['6000',4000,0],['1000',0,4000]],'operating','Office payroll OP-125');
entry('T14','2026-10-26','Pay rent',[['6100',3000,0],['1000',0,3000]],'operating','Lease payment LP-126');
entry('T15','2026-10-27','Pay loan interest',[['6600',200,0],['1000',0,200]],'operating','Loan statement LS-127');
entry('T16','2026-10-27','Repay loan principal',[['2500',1000,0],['1000',0,1000]],'financing','Loan statement LS-127');
entry('T17','2026-10-28','Purchase equipment; placed in service November 1',[['1500',6000,0],['1000',0,6000]],'investing','Equipment invoice EQ-128');
entry('T18','2026-10-29','Receive service deposit before completion',[['1000',4000,0],['2200',0,4000]],'operating','Service contract SC-129');
const baseJournal=journal.map(l=>({...l}));
if(active.has('insurance'))entry('A01','2026-10-31','Recognize one month of annual insurance',[['6200',v.insurance,0],['1300',0,v.insurance]],'insurance','Policy schedule INS-131');
if(active.has('depreciation'))entry('A02','2026-10-31','Depreciate existing office equipment',[['6300',v.depreciation,0],['1510',0,v.depreciation]],'depreciation','Existing office equipment: $48,000 / 60 months; zero residual');
if(active.has('wages'))entry('A03','2026-10-31','Accrue unpaid office wages',[['6000',v.wages,0],['2100',0,v.wages]],'wages','Unpaid office time report WT-131');
if(active.has('allowance'))entry('A04','2026-10-31','Estimate expected credit losses on $32,000 closing gross receivables',[['6400',32000*v.allowance,0],['1110',0,32000*v.allowance]],'allowance','Illustrative 3% receivables aging estimate');
if(active.has('earned'))entry('A05','2026-10-31','Recognize completed portion of deposited service',[['2200',v.earned,0],['4100',0,v.earned]],'earned','Service completion certificate SC-131');
if(active.has('overhead'))entry('A06','2026-10-31','Close $500 underapplied overhead to cost of goods sold',[['5000',500,0],['5100',0,500]],'overhead','Actual overhead $5,500 less applied $5,000; immaterial variance assumption');
if(active.has('bank')){entry('A07','2026-10-31','Record bank service fee',[['6500',v.bankFee,0],['1000',0,v.bankFee]],'bank','Bank statement BS-131');entry('A08','2026-10-31','Record deposit interest',[['1000',v.bankInterest,0],['4200',0,v.bankInterest]],'bank','Bank statement BS-131');}
const balances=Object.fromEntries(accounts.map(([code,,,opening])=>[code,opening]));for(const l of journal)balances[l.account]+=l.debit-l.credit;
const unadjusted=Object.fromEntries(accounts.map(([code,,,opening])=>[code,opening]));for(const l of baseJournal)unadjusted[l.account]+=l.debit-l.credit;
const revenue=-balances['4000']-balances['4100'],cogs=balances['5000'],grossProfit=revenue-cogs,opex=accounts.filter(a=>a[2]==='expense').reduce((s,a)=>s+balances[a[0]],0),netIncome=grossProfit-opex-balances['6600']-balances['4200'];
const assets=accounts.filter(a=>['asset','contra'].includes(a[2])).reduce((s,a)=>s+balances[a[0]],0),liabilities=-accounts.filter(a=>a[2]==='liability').reduce((s,a)=>s+balances[a[0]],0),equity=-balances['3000']-balances['3100']+netIncome;
const workingCapital=[['Gross accounts receivable',-(balances['1100']-12000)],['Raw materials',-(balances['1200']-10000)],['Finished goods',-(balances['1220']-8000)],['Work in process',-balances['1210']],['Overhead control',-balances['5100']],['Prepaid insurance',-(balances['1300']-6000)],['Accounts payable',-balances['2000']-14000],['Wages payable',-balances['2100']-2000],['Deferred revenue',-balances['2200']]];
const cfo=netIncome+balances['6300']+balances['6400']+workingCapital.reduce((s,r)=>s+r[1],0),cfi=-6000,cff=-1000,directCfo=journal.filter(l=>l.account==='1000'&&!['investing','financing'].includes(l.group)).reduce((s,l)=>s+l.debit-l.credit,0);
const bankStatement=46200-v.bankFee+v.bankInterest,bankAdjusted=bankStatement+3000-4900;
const checks=[['Journal debits less credits',journal.reduce((s,l)=>s+l.debit-l.credit,0)],['Trial balance signed total',Object.values(balances).reduce((s,n)=>s+n,0)],['Assets less liabilities and equity',assets-liabilities-equity],['Indirect less direct operating cash',cfo-directCfo],['Cash-flow ending cash less ledger cash',50000+cfo+cfi+cff-balances['1000']],['Adjusted bank less ledger cash',bankAdjusted-balances['1000']],['Work in process remaining',balances['1210']],['Overhead control remaining',balances['5100']]];
return {v,selected:[...active],journal,unadjusted,balances,revenue,cogs,grossProfit,opex,netIncome,assets,liabilities,equity,cfo,cfi,cff,directCfo,workingCapital,bankStatement,bankAdjusted,checks,complete:adjustmentGroups.every(g=>active.has(g[0]))};
}
