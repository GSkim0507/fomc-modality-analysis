"""
09_robustness_v2.py — Critic-mandated checks after adversarial verification (v2).

G1  be_comp_type / be+appropriate family per-doc densities x macro (feedback-1 x feedback-2 crossover)
G2  triage of all BH-significant E4 class cells (Spearman + excl-2020 + sparsity)
G3  F1 CCF and F2 Granger re-run EXCLUDING 2020, dense series only (zero-share<50%, n_tokens>=60)
G4  E3 novel-modal x VIX verdict (excl-2020)
G5  headline cell (minutes can x VIX): era-dummy HAC, AR(1)-prewhitened corr, circular-shift p
G6  2010-2026 extension: rebuild per-doc modal series from modal_tokens (window=False), re-test surviving cells
Outputs: results/tables/G1..G6*.csv (+ console verdicts)
"""
from __future__ import annotations
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from common import *

def bh(p):
    p=np.asarray(p,float); n=len(p); o=np.argsort(p)
    r=p[o]*n/(np.arange(n)+1); q=np.minimum.accumulate(r[::-1])[::-1]
    out=np.empty(n); out[o]=np.minimum(q,1); return out

def cor(x,y):
    ok=(~np.isnan(x))&(~np.isnan(y)); x,y=x[ok],y[ok]
    if len(x)<10 or np.std(y)==0 or np.std(x)==0: return dict(n=len(x),r=np.nan,p=np.nan,rho=np.nan,p_rho=np.nan)
    r,pp=stats.pearsonr(x,y); rho,pr=stats.spearmanr(x,y)
    return dict(n=len(x),r=round(r,3),p=round(pp,4),rho=round(rho,3),p_rho=round(pr,4))

def load_tokens(window=True):
    df=pd.read_csv(TAB/"modal_tokens.csv",low_memory=False)
    df=df[~df.doc_id.isin(EXCLUDE_DOCS)&df.modal.isin(SIX)]
    if window: df=df[(df.date>=START)&(df.date<=END)]
    df["predicate"]=df["predicate"].fillna(df["head_verb"])
    df["be_comp_type"]=df["be_comp_type"].fillna("")
    for c in ["neg","cond","reported"]: df[c]=df[c].astype(str).str.lower().eq("true")
    return df

macro=pd.read_csv(TAB/"macro_by_doc.csv")
b1=pd.read_csv(TAB/"B1_modal_doc_series.csv")
ds=b1.merge(macro.drop(columns=["doc_type","date"]),on="doc_id")
ds14=ds[ds.date>=START]
df=load_tokens()

def series_for(g, mask_fn):
    base=ds14[ds14.doc_type==g].set_index("doc_id").sort_values("date")
    sub=df[(df.doc_type==g)]
    sub=sub[mask_fn(sub)]
    ser=sub.groupby("doc_id").size().reindex(base.index).fillna(0)*1000/base["n_tokens"]
    return base, ser

def screen(name, g, mask_fn, rows):
    base, ser = series_for(g, mask_fn)
    zero=float((ser==0).mean()); tot=int((ser*base["n_tokens"]/1000).round().sum())
    for tag, sel in [("full", np.ones(len(base),bool)), ("excl2020", ~base["date"].str.startswith("2020").values)]:
        for mvar in ["cfnai_ma3_lag2","vix_pre28"]:
            rr=cor(base[mvar].values[sel], ser.values[sel])
            rows.append(dict(feature=name,genre=g,sample=tag,macro=mvar,zero_share=round(zero,2),total_n=tot,**rr))

# ---------- G1: be_comp_type and be+appropriate family ----------
rows=[]
for g in ["minutes","press_conf","statement"]:
    for bt in ["adjectival","nominal","prepositional"]:
        screen(f"beComp:{bt}", g, lambda s,bt=bt: (s.head_verb=="be")&(s.be_comp_type==bt), rows)
    for mo in ["will","would","may"]:
        screen(f"{mo}+be+appropriate", g, lambda s,mo=mo: (s.modal==mo)&(s.predicate=="be+appropriate"), rows)
    screen("ANY+be+appropriate", g, lambda s: s.predicate=="be+appropriate", rows)
    screen("would+be+prepared", g, lambda s: (s.modal=="would")&(s.predicate=="be+prepared"), rows)
g1=pd.DataFrame(rows)
m=g1.p.notna(); g1["q_bh"]=np.nan; g1.loc[m,"q_bh"]=bh(g1.loc[m,"p"].values).round(4)
g1.to_csv(TAB/"G1_becomp_macro.csv",index=False)

# ---------- G2: triage of E4 significant cells ----------
e4=pd.read_csv(TAB/"E4_class_macro.csv"); sig=e4[e4.q_bh<.05]
def pclass_of(s, pc):
    def f(hv,bt):
        if hv=="be":
            return {"adjectival":"copular_adj","nominal":"copular_nom","prepositional":"copular_prep","adverbial":"copular_other"}.get(bt or "","copular_bare")
        return verb_class(hv)
    return np.array([f(h,b) for h,b in zip(s.head_verb, s.be_comp_type)])==pc
rows=[]
for _,r0 in sig.iterrows():
    screen(f"{r0.modal}/{r0.pclass}", r0.genre, lambda s,mo=r0.modal,pc=r0.pclass: (s.modal==mo)&pclass_of(s,pc), rows)
g2=pd.DataFrame(rows).drop_duplicates(["feature","genre","sample","macro"])
def verdict_g2(grp):
    fullrow=grp[(grp["sample"]=="full")]
    ex=grp[(grp["sample"]=="excl2020")]
    if not len(fullrow) or not len(ex): return "?"
    f0,e0=fullrow.iloc[0],ex.iloc[0]
    if np.isnan(e0.r): return "insufficient"
    same=np.sign(f0.r)==np.sign(e0.r)
    okp=(e0.p<.1)or(e0.p_rho<.1)
    sparse=f0.zero_share>.5
    return ("CONFIRMED" if same and okp and not sparse else
            "WEAK" if same and not sparse else "ARTIFACT")
g2v=[]
for (feat,g_,mv),grp in g2.groupby(["feature","genre","macro"]):
    g2v.append(dict(feature=feat,genre=g_,macro=mv,verdict=verdict_g2(grp)))
g2verd=pd.DataFrame(g2v)
g2=g2.merge(g2verd,on=["feature","genre","macro"])
g2.to_csv(TAB/"G2_class_triage.csv",index=False)

# ---------- G3: excl-2020 CCF + Granger for dense series ----------
mm=pd.read_csv(TAB/"macro_monthly.csv",parse_dates=["date"]).set_index("date")
cfn=mm["CFNAIMA3"]; vixm=mm["VIX_M"]
dense=[("press_conf","will",None),("press_conf","would",None),("press_conf","can",None),
       ("minutes","would",None),("minutes","could",None),("minutes","can",None),
       ("statement","will",None),
       ("minutes","would",("predicate","be+appropriate")),
       ("minutes","would",("predicate","expand")),
       ("minutes","will",("predicate","assess"))]
rows=[]; grows=[]
for g,mo,extra in dense:
    mask=lambda s,mo=mo,extra=extra: (s.modal==mo)&((s[extra[0]]==extra[1]) if extra else True)
    base,ser=series_for(g,mask)
    name=f"{mo}"+(f"+{extra[1]}" if extra else "_per1k")
    zero=float((ser==0).mean())
    sel=~base["date"].str.startswith("2020").values
    y=ser.values[sel]; dts=pd.to_datetime(base["date"].values[sel])
    if zero>0.5 or len(y)<25: continue
    for target,serM in [("CFNAI_MA3",cfn),("VIX_M",vixm)]:
        best=None
        for k in range(-9,10):
            vals=np.array([serM.get((pd.Period(d,freq="M")+k).to_timestamp(),np.nan) for d in dts])
            ok=~np.isnan(vals)
            if ok.sum()<20: continue
            r_,p_=stats.pearsonr(y[ok],vals[ok]); rho_,pr_=stats.spearmanr(y[ok],vals[ok])
            rows.append(dict(genre=g,feature=name,target=target,k=k,n=int(ok.sum()),r=round(r_,3),p=round(p_,4),rho=round(rho_,3),p_rho=round(pr_,4)))
    # Granger excl-2020 vs vix_pre28 & cfnai
    md=ds14[ds14.doc_type==g].sort_values("date")
    sel2=~md["date"].str.startswith("2020").values
    for target in ["vix_pre28","cfnai_ma3_lag2"]:
        x=md[target].values[sel2].astype(float); yy=ser.reindex(md["doc_id"]).values[sel2].astype(float)
        n=min(len(x),len(yy)); x,yy=x[:n],yy[:n]
        try:
            stat=lambda z: adfuller(z,autolag="AIC")[1]<.05
            xs=x if stat(x) else np.diff(x); ys=yy if stat(yy) else np.diff(yy)
            n2=min(len(xs),len(ys)); xs,ys=xs[-n2:],ys[-n2:]
            if n2<25: continue
            r1=grangercausalitytests(np.column_stack([xs,ys]),maxlag=4,verbose=False)
            r2=grangercausalitytests(np.column_stack([ys,xs]),maxlag=4,verbose=False)
            grows.append(dict(genre=g,feature=name,target=target,n=n2,
                              p_text_to_macro=round(min(r1[l][0]["ssr_ftest"][1] for l in r1),4),
                              p_macro_to_text=round(min(r2[l][0]["ssr_ftest"][1] for l in r2),4)))
        except Exception: pass
g3=pd.DataFrame(rows); g3.to_csv(TAB/"G3_ccf_excl2020.csv",index=False)
g3p=(g3.assign(absr=g3.r.abs()).sort_values("absr",ascending=False)
       .groupby(["genre","feature","target"]).head(1))
g3p.to_csv(TAB/"G3b_ccf_peaks_excl2020.csv",index=False)
g3g=pd.DataFrame(grows)
if len(g3g):
    g3g["q_text_to_macro"]=bh(g3g.p_text_to_macro.values).round(4)
g3g.to_csv(TAB/"G3c_granger_excl2020.csv",index=False)

# ---------- G4: novel-modal x macro excl-2020 ----------
reuse=pd.read_csv(TAB/"C1_statement_sentence_reuse.csv")[["doc_id","sent_id","formulaic"]]
st=df[df.doc_type=="statement"].merge(reuse,on=["doc_id","sent_id"],how="left")
st["formulaic"]=st["formulaic"].fillna(False).astype(bool)
baseS=ds14[ds14.doc_type=="statement"].set_index("doc_id").sort_values("date")
rows=[]
for name,sub in [("novel_modal",st[~st.formulaic]),("formulaic_modal",st[st.formulaic])]:
    ser=sub.groupby("doc_id").size().reindex(baseS.index).fillna(0)*1000/baseS["n_tokens"]
    for tag,sel in [("full",np.ones(len(baseS),bool)),("excl2020",~baseS["date"].str.startswith("2020").values)]:
        for mvar in ["cfnai_ma3_lag2","vix_pre28"]:
            rr=cor(baseS[mvar].values[sel],ser.values[sel])
            rows.append(dict(feature=name,sample=tag,macro=mvar,**rr))
g4=pd.DataFrame(rows); g4.to_csv(TAB/"G4_novel_formulaic_verdict.csv",index=False)

# ---------- G5: headline minutes can x VIX — era dummy, prewhitening, circular shift ----------
baseM=ds14[ds14.doc_type=="minutes"].set_index("doc_id").sort_values("date")
y=baseM["can_per1k"].values.astype(float)
x=baseM[["cfnai_ma3_lag2","vix_pre28"]].astype(float)
era=(baseM["date"]>="2021-01-01").astype(float).values
res=[]
for tag,sel in [("full",np.ones(len(baseM),bool)),("excl2020",~baseM["date"].str.startswith("2020").values)]:
    X=sm.add_constant(pd.DataFrame({"cfnai":x["cfnai_ma3_lag2"].values[sel],"vix":x["vix_pre28"].values[sel],"post2021":era[sel]}))
    m1=sm.OLS(y[sel],X).fit(cov_type="HAC",cov_kwds={"maxlags":4})
    res.append(dict(check=f"HAC+era({tag})",b_vix=round(m1.params["vix"],4),p_vix=round(m1.pvalues["vix"],4),
                    b_post2021=round(m1.params["post2021"],4),p_post2021=round(m1.pvalues["post2021"],4),n=int(sel.sum())))
# AR(1) prewhiten
def prewhite(z):
    z=np.asarray(z,float); rho=np.corrcoef(z[:-1],z[1:])[0,1]
    return z[1:]-rho*z[:-1]
sel=~baseM["date"].str.startswith("2020").values
yy=y[sel]; vv=x["vix_pre28"].values[sel]
r_pw,p_pw=stats.pearsonr(prewhite(yy),prewhite(vv))
res.append(dict(check="prewhitened_corr(excl2020)",b_vix=round(r_pw,3),p_vix=round(p_pw,4),b_post2021=np.nan,p_post2021=np.nan,n=len(yy)-1))
# circular shift test
robs=stats.pearsonr(yy,vv)[0]; null=[]
for s_ in range(5,len(yy)-5):
    null.append(abs(stats.pearsonr(yy,np.roll(vv,s_))[0]))
p_shift=(np.sum(np.array(null)>=abs(robs))+1)/(len(null)+1)
res.append(dict(check="circular_shift_p(excl2020)",b_vix=round(robs,3),p_vix=round(p_shift,4),b_post2021=np.nan,p_post2021=np.nan,n=len(yy)))
g5=pd.DataFrame(res); g5.to_csv(TAB/"G5_headline_minutes_can.csv",index=False)

# ---------- G6: genuine 2010-2026 extension ----------
dfx=load_tokens(window=False); dfx=dfx[dfx.date>="2010-01-01"]
docs_all=pd.read_csv(TAB/"corpus_docs.csv"); docs_all=docs_all[~docs_all.doc_id.isin(EXCLUDE_DOCS)]
docs_all=docs_all[docs_all.date>="2010-01-01"]
mac=macro.set_index("doc_id")
rows=[]
CELLS=[("minutes","can",None,"vix_pre28"),("press_conf","will",None,"vix_pre28"),
       ("press_conf","could",None,"vix_pre28"),("minutes","would",("predicate","be+appropriate"),"vix_pre28"),
       ("minutes","would",("predicate","expand"),"vix_pre28"),("statement","will",None,"vix_pre28"),
       ("minutes","can",None,"cfnai_ma3_lag2")]
for g,mo,extra,mvar in CELLS:
    base=docs_all[docs_all.doc_type==g].set_index("doc_id").sort_values("date")
    sub=dfx[(dfx.doc_type==g)&(dfx.modal==mo)]
    if extra: sub=sub[sub[extra[0]]==extra[1]]
    ser=sub.groupby("doc_id").size().reindex(base.index).fillna(0)*1000/base["n_tokens"]
    mv=mac[mvar].reindex(base.index)
    name=f"{mo}"+(f"+{extra[1]}" if extra else "")
    for tag,sel in [("2010-2026",np.ones(len(base),bool)),
                    ("2010-2026_excl2020",~base["date"].str.startswith("2020").values)]:
        rr=cor(mv.values[sel].astype(float),ser.values[sel])
        rows.append(dict(genre=g,feature=name,macro=mvar,sample=tag,zero_share=round(float((ser==0).mean()),2),**rr))
g6=pd.DataFrame(rows); g6.to_csv(TAB/"G6_2010_extension.csv",index=False)

pd.set_option("display.width",240)
print("=== G1 be-comp x macro (q<.05 or notable) ===")
print(g1[(g1.q_bh<.05)|((g1["sample"]=="excl2020")&(g1.p_rho<.05))].to_string(index=False))
print("\n=== G2 class triage verdicts ===")
print(g2verd.to_string(index=False))
print("\n=== G3b CCF peaks excl-2020 (p<.05, |k| noted) ===")
print(g3p[g3p.p<.05].to_string(index=False))
print("\n=== G3c Granger excl-2020 ===")
print(g3g.sort_values("p_text_to_macro").to_string(index=False))
print("\n=== G4 novel/formulaic verdict ===")
print(g4.to_string(index=False))
print("\n=== G5 headline checks ===")
print(g5.to_string(index=False))
print("\n=== G6 2010-2026 extension ===")
print(g6.to_string(index=False))
