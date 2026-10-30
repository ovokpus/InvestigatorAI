'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import { createApiUrl } from '@/utils/api';

type Tx = {
  amount: number; merchant_category: string; hour: number; day_of_week: number;
  user_country: string; merchant_country: string; payment_method: string; card_present: boolean;
};
type AgentOut = Record<string, unknown> & { agent: string };
type Result = {
  transaction_id: string; is_fraud: boolean; risk_score: number; confidence: number;
  recommendation: 'approve' | 'review' | 'escalate'; explanation: string; agent_outputs: AgentOut[]; processing_time_ms: number;
};
type Metrics = { samples: number; threshold: number; accuracy: number; precision: number; recall: number; false_positive_rate: number; avg_latency_ms: number; dataset_size: number; fraud_rate: number };
type Options = Record<string, string[]>;
type Similar = Tx & { transaction_id: string; is_fraud: boolean; distance: number };

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const PRESETS: Record<string, Tx> = {
  'Everyday grocery': { amount: 42, merchant_category: 'grocery', hour: 14, day_of_week: 2, user_country: 'US', merchant_country: 'US', payment_method: 'debit_card', card_present: true },
  'Late-night crypto abroad': { amount: 6200, merchant_category: 'cryptocurrency', hour: 2, day_of_week: 5, user_country: 'US', merchant_country: 'RO', payment_method: 'crypto', card_present: false },
  'Card testing': { amount: 1.5, merchant_category: 'online_gaming', hour: 23, day_of_week: 6, user_country: 'UK', merchant_country: 'NG', payment_method: 'credit_card', card_present: false },
};
const REC_STYLE = {
  approve: 'bg-green-600 text-white', review: 'bg-amber-500 text-white', escalate: 'bg-red-600 text-white',
};
const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

function Nav() {
  const item = 'px-3 sm:px-4 py-2 bg-secondary text-secondary-foreground hover:bg-accent rounded-lg font-medium transition-colors text-center text-sm sm:text-base';
  return (
    <nav className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4 mb-8">
      <span className="px-3 sm:px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium text-center text-sm sm:text-base">Screening</span>
      <Link href="/" className={item}>Investigation</Link>
      <Link href="/tools" className={item}>Tools & Search</Link>
      <Link href="/help" className={item}>Help & Docs</Link>
    </nav>
  );
}

function AgentCard({ o }: { o: AgentOut }) {
  const rows: [string, string][] = [];
  if (o.agent === 'TransactionAgent') {
    rows.push(['Risk score', String((o.risk_score as number).toFixed(2))], ['Anomaly (IsolationForest)', o.is_anomaly ? 'yes' : 'no']);
    (o.risk_factors as string[]).forEach((f) => rows.push(['Factor', f]));
  } else if (o.agent === 'BehavioralAgent') {
    rows.push(['Fraud rate in 10 nearest cases', pct(o.fraud_probability as number)], ['Behavioral score', (o.behavioral_score as number).toFixed(2)]);
    (o.behavioral_risks as string[]).forEach((f) => rows.push(['Risk', f]));
  } else {
    rows.push(['Patterns matched', String(o.patterns_count)], ['Pattern score', (o.pattern_score as number).toFixed(2)]);
    (o.matched_patterns as { name: string }[]).forEach((p) => rows.push(['Pattern', p.name]));
  }
  return (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="font-semibold text-contrast mb-2">{o.agent.replace('Agent', ' Agent')}</div>
      <dl className="text-sm space-y-1">
        {rows.map(([k, v], i) => (
          <div key={i} className="flex justify-between gap-2"><dt className="text-muted-foreground">{k}</dt><dd className="text-right">{v}</dd></div>
        ))}
      </dl>
    </div>
  );
}

export default function ScreeningPage() {
  const [tx, setTx] = useState<Tx>(PRESETS['Late-night crypto abroad']);
  const [opts, setOpts] = useState<Options>({});
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [res, setRes] = useState<Result | null>(null);
  const [similar, setSimilar] = useState<Similar[]>([]);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch(createApiUrl('/screen/options')).then((r) => r.json()).then(setOpts).catch(() => setErr('API not reachable'));
    fetch(createApiUrl('/screen/metrics')).then((r) => r.json()).then(setMetrics).catch(() => {});
  }, []);

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault(); setBusy(true); setErr('');
    try {
      const body = JSON.stringify(tx);
      const headers = { 'Content-Type': 'application/json' };
      const [r, s] = await Promise.all([
        fetch(createApiUrl('/screen'), { method: 'POST', headers, body }),
        fetch(createApiUrl('/screen/similar?limit=5'), { method: 'POST', headers, body }),
      ]);
      if (!r.ok) throw new Error(`screening failed (${r.status})`);
      setRes(await r.json()); setSimilar(await s.json());
    } catch (x) { setErr(String(x)); } finally { setBusy(false); }
  };

  const investigateHref = res ? `/?${new URLSearchParams({
    amount: String(tx.amount), currency: 'USD', country_to: tx.merchant_country,
    risk_rating: res.is_fraud ? 'High' : 'Medium',
    description: `Flagged by GuardianAI screening (risk ${res.risk_score.toFixed(2)}): ${tx.payment_method} payment at ${tx.merchant_category} merchant in ${tx.merchant_country}, ${tx.hour}:00 ${DAYS[tx.day_of_week]}, card ${tx.card_present ? 'present' : 'not present'}, customer in ${tx.user_country}.`,
  })}` : '/';

  const select = (k: keyof Tx, label: string) => (
    <label className="block text-xs sm:text-sm font-medium text-contrast">{label}
      <select className="mt-1 w-full px-3 py-2 border border-border rounded-lg bg-input" value={String(tx[k])}
        onChange={(e) => setTx({ ...tx, [k]: e.target.value })}>
        {(opts[k] || [String(tx[k])]).map((o) => <option key={o}>{o}</option>)}
      </select>
    </label>
  );
  const num = (k: keyof Tx, label: string, min: number, max?: number) => (
    <label className="block text-xs sm:text-sm font-medium text-contrast">{label}
      <input type="number" step="any" min={min} max={max} className="mt-1 w-full px-3 py-2 border border-border rounded-lg bg-input"
        value={Number(tx[k])} onChange={(e) => setTx({ ...tx, [k]: Number(e.target.value) })} />
    </label>
  );

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <Nav />
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-contrast mb-2">Real-time transaction screening</h1>
          <p className="text-muted-foreground">GuardianAI&apos;s four agents score every transaction in milliseconds, with no LLM call. High-risk ones are escalated to a full InvestigatorAI investigation.</p>
        </div>

        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mb-8">
            {[['Accuracy', pct(metrics.accuracy)], ['Precision', pct(metrics.precision)], ['Recall', pct(metrics.recall)],
              ['False-positive rate', pct(metrics.false_positive_rate)], ['Avg latency', `${metrics.avg_latency_ms} ms`]].map(([k, v]) => (
              <div key={k} className="bg-card border border-border rounded-lg p-3">
                <div className="text-xs text-muted-foreground">{k}</div><div className="text-xl font-bold text-contrast">{v}</div>
              </div>
            ))}
            <p className="col-span-2 sm:col-span-5 text-xs text-muted-foreground">Measured on {metrics.samples} of {metrics.dataset_size} synthetic GuardianAI transactions ({pct(metrics.fraud_rate)} fraud), threshold {metrics.threshold}. In-sample, so treat as a sanity check.</p>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          <form onSubmit={submit} className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div className="flex flex-wrap gap-2">
              {Object.keys(PRESETS).map((p) => (
                <button type="button" key={p} onClick={() => setTx(PRESETS[p])} className="px-3 py-1 text-xs rounded-full bg-secondary hover:bg-accent">{p}</button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-3">
              {num('amount', 'Amount (USD)', 0.01)}
              {select('merchant_category', 'Merchant category')}
              {num('hour', 'Hour (0-23)', 0, 23)}
              <label className="block text-xs sm:text-sm font-medium text-contrast">Day of week
                <select className="mt-1 w-full px-3 py-2 border border-border rounded-lg bg-input" value={tx.day_of_week}
                  onChange={(e) => setTx({ ...tx, day_of_week: Number(e.target.value) })}>
                  {DAYS.map((d, i) => <option key={d} value={i}>{d}</option>)}
                </select>
              </label>
              {select('user_country', 'Customer country')}
              {select('merchant_country', 'Merchant country')}
              {select('payment_method', 'Payment method')}
              <label className="flex items-center gap-2 text-sm font-medium text-contrast mt-6">
                <input type="checkbox" checked={tx.card_present} onChange={(e) => setTx({ ...tx, card_present: e.target.checked })} /> Card present
              </label>
            </div>
            <button type="submit" disabled={busy} className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-semibold disabled:opacity-50">
              {busy ? 'Screening…' : 'Screen transaction'}
            </button>
            {err && <p className="text-red-600 text-sm">{err}</p>}
          </form>

          <div className="space-y-4">
            {!res && <div className="bg-card border border-border rounded-lg p-6 text-muted-foreground">Pick a preset or enter a transaction, then screen it.</div>}
            {res && (
              <>
                <div className="bg-card border border-border rounded-lg p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className={`px-3 py-1 rounded-full text-sm font-bold uppercase ${REC_STYLE[res.recommendation]}`}>{res.recommendation}</span>
                    <span className="text-sm text-muted-foreground">{res.processing_time_ms} ms</span>
                  </div>
                  <div className="text-4xl font-bold text-contrast">{res.risk_score.toFixed(2)}<span className="text-base font-normal text-muted-foreground"> risk score</span></div>
                  <div className="w-full h-2 bg-secondary rounded mt-2"><div className="h-2 rounded bg-red-500" style={{ width: `${Math.min(100, res.risk_score * 100)}%` }} /></div>
                  <pre className="mt-4 text-xs whitespace-pre-wrap text-muted-foreground font-sans">{res.explanation}</pre>
                  {res.recommendation !== 'approve' && (
                    <Link href={investigateHref} className="mt-4 block text-center py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold">
                      Open full investigation →
                    </Link>
                  )}
                </div>
                <div className="grid sm:grid-cols-3 gap-3">{res.agent_outputs.map((o) => <AgentCard key={o.agent} o={o} />)}</div>
              </>
            )}
          </div>
        </div>

        {similar.length > 0 && (
          <div className="mt-8 bg-card border border-border rounded-lg p-5 overflow-x-auto">
            <h2 className="font-semibold text-contrast mb-3">Most similar historical transactions</h2>
            <table className="w-full text-sm">
              <thead className="text-muted-foreground text-left"><tr><th>Amount</th><th>Category</th><th>Time</th><th>Route</th><th>Payment</th><th>Card</th><th>Label</th></tr></thead>
              <tbody>{similar.map((s) => (
                <tr key={s.transaction_id} className="border-t border-border">
                  <td className="py-1">${s.amount.toFixed(2)}</td><td>{s.merchant_category}</td><td>{s.hour}:00 {DAYS[s.day_of_week]}</td>
                  <td>{s.user_country} → {s.merchant_country}</td><td>{s.payment_method}</td><td>{s.card_present ? 'present' : 'absent'}</td>
                  <td className={s.is_fraud ? 'text-red-600 font-semibold' : 'text-green-600'}>{s.is_fraud ? 'fraud' : 'legit'}</td>
                </tr>))}</tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
