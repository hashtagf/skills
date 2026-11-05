export default function Home(){return(<main className="bg-[#0b1020] text-white">
 <section className="text-center py-32"><p className="uppercase tracking-widest text-xs text-indigo-400">AI-POWERED</p>
  <h1 className="text-6xl font-bold">Supercharge your <span className="bg-gradient-to-r from-indigo-400 to-pink-400 bg-clip-text text-transparent">workflow</span></h1>
  <p className="text-slate-400">The all-in-one platform for modern teams.</p><button className="bg-indigo-500 rounded-lg px-6 py-3">Get started →</button></section>
 <section className="grid grid-cols-3 gap-6">{["Fast","Secure","Scalable"].map(t=><div key={t} className="rounded-xl bg-white/5 p-6"><div className="w-10 h-10 rounded-lg bg-indigo-500/20"/>{t}</div>)}</section>
 <section>Trusted by 10,000+ teams ★★★★★</section></main>)}
