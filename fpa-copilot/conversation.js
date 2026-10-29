/* Session-local dialogue and deterministic USD calculations. No storage or credentials. */
(function (root) {
  'use strict';
  const money = cents => '$' + (cents / 100).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
  function create() {
    let history = [], figures = null, last = null;
    const remember = (question, answer, topic) => {
      history.push({role: 'user', content: question}, {role: 'assistant', content: answer});
      history = history.slice(-20);
      last = {answer, topic};
      return answer;
    };
    function describe(f) {
      const difference = f.actual - f.budget;
      const percentage = f.budget === 0 ? 'undefined because the budget is zero' : (100 * difference / f.budget).toFixed(2) + '% of budget';
      const favorable = f.metric === 'revenue' ? difference > 0 : difference < 0;
      const meaning = difference === 0 ? 'on budget' : f.metric ? (favorable ? 'favorable' : 'unfavorable') : 'above budget for revenue is favorable; above budget for expenses is unfavorable';
      return `Using USD and the same period: actual ${money(f.actual)}, budget ${money(f.budget)}. Actual minus budget is ${money(difference)} (${percentage}); ${meaning}.`;
    }
    function answer(question) {
      const q = question.trim(), lower = q.toLowerCase();
      if (/^(hi|hello|hey)(\b|[!.])/.test(lower)) {
        return remember(q, "Hello, I'm ARIA. What would you like to talk about or work on together?", 'greeting');
      }
      if (/what can you (do|help)|capabilities/.test(lower)) {
        return remember(q, "You can talk with me, type questions, or add information for us to review. I can explain ideas and calculate supported financial examples. General AI replies depend on the connected reasoning service.", 'capabilities');
      }
      if (/simpl(er|y)|plain (english|language)/.test(lower)) {
        if (!last) return remember(q, 'What would you like me to explain more simply?', 'clarification');
        let text = last.topic === 'cash' ? 'Profit is what you earn after expenses. Cash flow is when money actually enters or leaves your account. A sale on credit can increase profit before you receive cash.' : last.topic === 'variance' && figures ? `You brought in or spent ${money(figures.actual)}, compared with a ${money(figures.budget)} plan. The difference is ${money(figures.actual - figures.budget)}.` : 'Here is the previous explanation in brief: ' + last.answer.split(/(?<=[.!?])\s+/).slice(0,2).join(' ');
        return remember(q, text, last.topic);
      }
      if (/cash\s*flow/.test(lower) && /profit/.test(lower)) {
        return remember(q, 'Profit is revenue minus recognized expenses for a period. Cash flow measures cash received and paid. They differ because credit sales, unpaid bills, depreciation, and investment timing affect them differently. For example, a $1,000 credit sale can increase profit before the customer pays, while cash flow increases when payment arrives.', 'cash');
      }
      const amount = '(?:\\$\\s*)?(-?(?:\\d{1,3}(?:,\\d{3})+|\\d+)(?:\\.\\d{1,2})?)(?!\\d|[.,]\\d)';
      const read = label => {
        const match = q.match(new RegExp('\\b' + label + '(?:\\s+(?:revenue|sales|expense(?:s)?|costs?))?\\s*(?:(?:is|was|equals|of)\\s*)?[:=]?\\s*' + amount, 'i'));
        return match ? Math.round(Number(match[1].replaceAll(',', '')) * 100) : null;
      };
      const budget = read('budget(?:ed)?'), actual = read('actual');
      if (budget !== null && actual !== null) {
        if (/€|£|\b(?:EUR|GBP|CAD|AUD)\b/i.test(q)) return remember(q, 'This calculator currently uses USD. Please provide USD amounts or confirm that you want only a currency-neutral explanation.', 'clarification');
        if (![budget, actual, actual-budget].every(Number.isSafeInteger)) return remember(q, 'These amounts exceed the supported calculation range. Please use smaller USD figures.', 'clarification');
        figures = {budget, actual, metric: /\b(expenses?|costs?)\b/.test(lower) ? 'expense' : /\b(revenue|sales)\b/.test(lower) ? 'revenue' : null};
        return remember(q, describe(figures), 'variance');
      }
      if (/^(why|what caused)|why did/.test(lower)) {
        if (!figures || !['variance', 'cause'].includes(last?.topic)) return remember(q, 'Which result would you like to investigate?', 'clarification');
        return remember(q, describe(figures) + ' Those figures show the size of the difference, not its cause. Possible drivers include price, volume, mix, or timing. Do you have a price-and-volume breakdown for that period?', 'cause');
      }
      if (/what if|increas|decreas|drop|rise/.test(lower) && /%/.test(q)) {
        if (!figures || !['variance','cause','scenario'].includes(last?.topic)) return remember(q, 'What actual amount and budget should I use for this scenario?', 'clarification');
        const change = q.match(/(?:increas\w*|decreas\w*|drop\w*|ris\w*)\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%/i);
        if (!change || !/revenue|sales|actual/.test(lower) || /budget\s+(?:increas|decreas|drop|rise)/.test(lower)) return remember(q, 'Should I change actual revenue or the budget, and by what percentage?', 'clarification');
        const from = q.match(new RegExp('\\bfrom\\s+' + amount, 'i'));
        const base = from ? Math.round(Number(from[1].replaceAll(',', '')) * 100) : figures.actual;
        const direction = /decreas|drop/.test(change[0].toLowerCase()) ? -1 : 1;
        const updated = Math.round(base * (1 + direction * Number(change[1]) / 100));
        if (!Number.isSafeInteger(updated) || !Number.isSafeInteger(updated-figures.budget)) return remember(q, 'That scenario exceeds the supported calculation range.', 'clarification');
        const scenario = {...figures, actual: updated};
        const difference = updated - figures.budget;
        return remember(q, `Hypothetically, ${money(base)} ${direction === 1 ? 'increased' : 'decreased'} by ${change[1]}% becomes ${money(updated)}. Against the unchanged ${money(figures.budget)} budget, that is a ${money(Math.abs(difference))} ${difference < 0 ? 'shortfall' : difference > 0 ? 'surplus' : 'difference'}. The original actual remains ${money(figures.actual)}.`, 'scenario');
      }
      if (budget !== null || actual !== null) return remember(q, `What ${budget === null ? 'budget' : 'actual'} amount should I use, in USD for the same period?`, 'clarification');
      return null;
    }
    return {answer, remember, messages: () => history.map(item => ({...item})), reset: () => {history = []; figures = null; last = null;}};
  }
  root.ARIAConversation = {create};
  if (typeof module !== 'undefined') module.exports = root.ARIAConversation;
})(typeof globalThis !== 'undefined' ? globalThis : this);
