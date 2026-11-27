#!/usr/bin/env python3
"""Homodyne HMD-005 — build the ready-to-record token-colouring page.

Writes artifact/token-view.html: one self-contained page (no network) that
shows how each real tokenizer splits the same sentence in English and in
Persian. Every coloured box is one token; amber boxes are tokens that are only
part of a character (raw UTF-8 bytes). Counts come from the real tokenizers at
build time; the page itself runs nothing.

Sentences
  demo    our test sentence (frame 3-4 of the episode; self-written)
  gpt4o   OpenAI's own example from "Hello GPT-4o", 13 May 2024 (quoted)
  flores  FLORES-200 devtest line 1 (NLLB Team, Meta AI; CC BY-SA 4.0),
          read from the tarball if --flores is given, else the copy below

Keys on the page:  ← →  tokenizer · ↑ ↓  sentence · A  all tokenizers (bars only) · H  key help
Start state from the URL: token-view.html#s=gpt4o&t=PersianMind&all=1

Usage
  python3 -I token_view.py                 # needs tiktoken (+ transformers)
  python3 -I token_view.py --offline       # local tokenizer caches only
  python3 -I token_view.py --selftest      # fast, offline, no tokenizers
"""
import argparse
import datetime as dt
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # our own sibling modules (works under python3 -I)

FLORES_LINE1 = {  # devtest line 1 of pes_Arab / eng_Latn, exactly as published
    "fa": "وی افزود: «اکنون موش‌های 4 ماهه‌ای داریم که دیابت ندارند در حالی که قبلاً دیابت داشتند.»",
    "en": "\"We now have 4-month-old mice that are non-diabetic that used to be diabetic,\" he added.",
}
# Order on the page: oldest/most-split first, then the "Persian got room" pairs.
ORDER = ["gpt2 (r50k)", "cl100k_base", "o200k_base", "Llama-2", "PersianMind", "Qwen3", "Qwen3.5",
         "Llama-3.2", "Gemma-3", "Mistral-Nemo", "DeepSeek-V3", "gpt-oss"]


def sentences(flores_tar=None):
    import count_tokens
    import crosscheck
    fl = FLORES_LINE1
    if flores_tar:
        fa, en = crosscheck.read_flores(flores_tar)
        fl = {"fa": fa[0], "en": en[0]}
    return [
        {"id": "demo", "fa": count_tokens.DEMO, "en": count_tokens.DEMO_EN,
         "credit": "Homodyne test sentence (self-written) · episode frames 3–4"},
        {"id": "gpt4o", "fa": crosscheck.GPT4O_FA, "en": crosscheck.GPT4O_EN,
         "credit": "Sentence quoted from OpenAI, “Hello GPT-4o”, 13 May 2024 — OpenAI states Persian went from 61 to 32 tokens"},
        {"id": "flores", "fa": fl["fa"], "en": fl["en"],
         "credit": "FLORES-200 devtest, line 1 · NLLB Team (Meta AI) · CC BY-SA 4.0 "
                   "(https://creativecommons.org/licenses/by-sa/4.0/) · token split by Homodyne; this sentence "
                   "and its split are CC BY-SA 4.0, not covered by the repository licence."},
    ]


def collect(offline, flores_tar=None):
    import count_tokens
    import crosscheck
    specs = {s[0]: s for s in count_tokens.TOKENIZERS + crosscheck.EXTRA}
    sents = sentences(flores_tar)
    toks = []
    for label in ORDER:
        try:
            t = count_tokens.Tok(*specs[label], offline=offline)
        except Exception as e:  # graceful skip
            print(f"SKIPPED {label}: {type(e).__name__}", file=sys.stderr)
            continue
        toks.append({"label": label, "version": t.version, "note": t.note,
                     "split": {s["id"]: {"fa": t.pieces(s["fa"]), "en": t.pieces(s["en"])} for s in sents}})
        print(f"done    {label}", file=sys.stderr)
    return {"sentences": sents, "tokenizers": toks}


CSS = """
:root{--bg:#111214;--fg:#f2efe8;--mute:#8d8a83;--amber:#e8a33d;--line:#2a2c30}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--fg);
font-family:"Vazirmatn","IRANSans",system-ui,-apple-system,"Segoe UI",sans-serif}
main{width:min(1600px,100vw);margin:0 auto;padding:28px 56px}
header{display:flex;justify-content:space-between;align-items:baseline;gap:24px;border-bottom:1px solid var(--line);padding-bottom:16px}
h1{font-size:40px;margin:0;font-weight:700;letter-spacing:.01em}
.sub{color:var(--mute);font-size:20px}
.row{margin-top:22px}
.lab{display:flex;justify-content:space-between;align-items:baseline;color:var(--mute);font-size:22px;margin-bottom:12px}
.lab b{color:var(--fg);font-size:48px;font-variant-numeric:tabular-nums}
.toks{display:flex;flex-wrap:wrap;gap:6px;font-size:33px;line-height:1.2}
.toks i{font-style:normal;padding:4px 9px;border-radius:8px;white-space:pre;border:1px solid rgba(255,255,255,.08)}
.toks i:nth-child(5n+1){background:#2f3b4a}.toks i:nth-child(5n+2){background:#3a3550}
.toks i:nth-child(5n+3){background:#2e4639}.toks i:nth-child(5n+4){background:#4a3a33}.toks i:nth-child(5n){background:#36424a}
.toks i.b{background:var(--amber)!important;color:#111214;font-family:ui-monospace,Menlo,monospace;font-size:21px;align-self:center}
.toks i.z{background:#5b2a4a!important;font-family:ui-monospace,Menlo,monospace;font-size:20px;align-self:center}
.fa{direction:rtl}.en{direction:ltr}
.ratio{margin:22px 0 0;font-size:28px;color:var(--mute)}.ratio b{color:var(--amber);font-size:60px}
.all{display:none;margin-top:18px}body.allmode .all{display:block}body.allmode .row,body.allmode .ratio{display:none}
body.allmode .bar{font-size:27px;margin:9px 0}body.allmode .bar i{height:30px}
.bar{display:grid;grid-template-columns:220px 1fr 110px;gap:16px;align-items:center;font-size:21px;margin:3px 0}
.bar span:first-child{direction:ltr;text-align:left}
.bar i{display:block;height:20px;background:#3a3d44;border-radius:4px}.bar.cur i{background:var(--amber)}
.bar b{font-variant-numeric:tabular-nums;direction:ltr}
footer{margin-top:22px;border-top:1px solid var(--line);padding-top:10px;color:var(--mute);font-size:14px;direction:ltr;line-height:1.45}
.help{position:fixed;bottom:12px;right:16px;color:var(--mute);font-size:14px;direction:ltr}.help.off{display:none}
"""

JS = """
const D=JSON.parse(document.getElementById('data').textContent);
let s=0,t=0;const $=id=>document.getElementById(id);
function chips(el,pieces){el.innerHTML='';for(const p of pieces){const i=document.createElement('i');
 if(/^<[0-9a-f]+>$/.test(p)){i.className='b';i.textContent=p.slice(1,-1)}
 else if(p.includes('\\u200c')){i.className='z';i.textContent=p.replace(/\\u200c/g,'ZWNJ')}
 else i.textContent=p.trim()===''?'\\u2423':p;el.appendChild(i)}}
function draw(){const S=D.sentences[s],T=D.tokenizers[t],sp=T.split[S.id];
 $('tok').textContent=document.body.classList.contains('allmode')?'فارسی ÷ انگلیسی · Persian ÷ English':T.label;$('ver').textContent=T.version;
 chips($('en'),sp.en);chips($('fa'),sp.fa);$('nen').textContent=sp.en.length;$('nfa').textContent=sp.fa.length;
 $('r').textContent=(sp.fa.length/sp.en.length).toFixed(2)+'\\u00d7';$('credit').textContent=S.credit;
 const mx=Math.max(...D.tokenizers.map(x=>x.split[S.id].fa.length/x.split[S.id].en.length));
 $('all').innerHTML=D.tokenizers.map((x,k)=>{const r=x.split[S.id].fa.length/x.split[S.id].en.length;
  return `<div class="bar${k===t?' cur':''}"><span>${x.label}</span><i style="width:${(100*r/mx).toFixed(1)}%"></i><b>${r.toFixed(2)}\\u00d7</b></div>`}).join('')}
addEventListener('keydown',e=>{const n=D.tokenizers.length,m=D.sentences.length;
 if(e.key==='ArrowRight'||e.key===' ')t=(t+1)%n;else if(e.key==='ArrowLeft')t=(t+n-1)%n;
 else if(e.key==='ArrowDown')s=(s+1)%m;else if(e.key==='ArrowUp')s=(s+m-1)%m;
 else if(e.key==='a'||e.key==='A')document.body.classList.toggle('allmode');
 else if(e.key==='h'||e.key==='H')$('help').classList.toggle('off');else return;e.preventDefault();draw()});
const H=new URLSearchParams(location.hash.slice(1));
const fi=(k,arr)=>{const v=H.get(k);if(v===null)return -1;const i=arr.findIndex(x=>(x.label||x.id)===v);return i>=0?i:(+v||0)};
if(fi('t',D.tokenizers)>=0)t=fi('t',D.tokenizers);if(fi('s',D.sentences)>=0)s=fi('s',D.sentences);
if(H.get('all'))document.body.classList.add('allmode');
draw();
"""


def render(data, built):
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="fa"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HMD-005 token view</title><style>{CSS}</style></head><body><main>
<header><h1 id="tok"></h1><span class="sub" id="ver" dir="ltr"></span></header>
<section class="row"><div class="lab"><span>English</span><b id="nen"></b></div><div class="toks en" id="en" lang="en"></div></section>
<section class="row"><div class="lab"><span>فارسی</span><b id="nfa"></b></div><div class="toks fa" id="fa" lang="fa"></div></section>
<p class="ratio">فارسی ÷ انگلیسی · Persian ÷ English &nbsp;<b id="r" dir="ltr"></b></p>
<section class="all" id="all"></section>
<footer><span id="credit"></span><br>
Each box = one token. Amber = part of a character (raw UTF-8 bytes, hex). ZWNJ = the invisible half-space.
Splits computed by Homodyne on {html.escape(built)} with the real tokenizer files (versions above; see sources.md). Special tokens not counted.</footer>
</main><div class="help off" id="help">← → tokenizer · ↑ ↓ sentence · A all · H hide</div>
<script type="application/json" id="data">{payload}</script><script>{JS}</script></body></html>
"""


def selftest():
    data = {"sentences": [{"id": "x", "fa": "سلام", "en": "hi", "credit": "c </script> & <b>"}],
            "tokenizers": [{"label": "fake", "version": "v0", "note": "",
                            "split": {"x": {"fa": ["سل", "ام", "<d8>", "‌ی"], "en": ["hi"]}}}]}
    page = render(data, "2026-01-01")
    assert page.startswith("<!doctype html>") and page.count("<script") == 2
    blob = page.split('id="data">', 1)[1].split("</script>", 1)[0]
    assert "</script>" not in blob and json.loads(blob.replace("<\\/", "</")) == data
    assert "http" not in page.replace("https://", "")  # no network fetches in the page
    assert FLORES_LINE1["fa"].startswith("وی افزود") and len(ORDER) == len(set(ORDER))
    import count_tokens
    import crosscheck
    known = {s[0] for s in count_tokens.TOKENIZERS + crosscheck.EXTRA}
    assert set(ORDER) <= known, set(ORDER) - known
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(HERE / "token-view.html"))
    ap.add_argument("--flores", help="flores200_dataset.tar.gz (optional; else the built-in copy of line 1)")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    data = collect(a.offline, a.flores)
    if not data["tokenizers"]:
        sys.exit("no tokenizer could be loaded")
    Path(a.out).write_text(render(data, a.date), encoding="utf-8")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
