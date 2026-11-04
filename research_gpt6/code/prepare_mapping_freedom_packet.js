/* Stage 88 deterministic JS mirror. Pure functions: no filesystem/network/ref writes.
 * Same canonical JSON bytes as prepare_mapping_freedom_packet.py.
 * Answers and seed are private until the root's explicit GO_REVEAL.
 */
const ALPHABET = "abcdefghijklmnopqrstuvwxyz";
const N = 2000;
const SOURCE_COMMIT = "960254605ab910ed90af8d3a8cc7278bbb202185";
const SOURCE_BUNDLE_BLOB = "78cac8d327438695cd226a62529ad7ac078f59d1";
const PRIOR_TRUTH_BLOB = "d19cc5cdcc5bba1976ba05e61bccfcddbea5739a";
const LM_SHA256 = "9206bde5bb6252ddb4de70dd2ea28aef6cc0ca5f59effbc2deac3e34546eae77";
const TEST_PATHS = ["caesar/gall1.txt", "caesar/gall2.txt", "caesar/gall3.txt"];
const RNG_SPEC = "xorshift32 shifts13,17,5 unsigned32; rejection randbelow; Fisher-Yates descending";
const NORMALIZATION = "drop first line; exclude str.isupper lines; lower; regex [a-z]+; join words with ASCII space; no i/j or u/v merging; windows count letters, remove spaces";
const VERSION = "mapping-freedom-generator-v1";
function require88(ok, message) { if (!ok) throw new Error(message); }
function canonical(value) {
  function sorted(v) {
    if (Array.isArray(v)) return v.map(sorted);
    if (v !== null && typeof v === "object") {
      const out = {}; for (const k of Object.keys(v).sort()) out[k] = sorted(v[k]); return out;
    }
    return v;
  }
  return JSON.stringify(sorted(value)).replace(/[\u007f-\uffff]/g, c =>
    "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0")) + "\n";
}
function utf8Bytes(text) {
  const out = [];
  for (const c of text) {
    const n = c.codePointAt(0);
    if (n < 128) out.push(n);
    else if (n < 2048) out.push(192 | (n >> 6), 128 | (n & 63));
    else if (n < 65536) out.push(224 | (n >> 12), 128 | ((n >> 6) & 63), 128 | (n & 63));
    else out.push(240 | (n >> 18), 128 | ((n >> 12) & 63), 128 | ((n >> 6) & 63), 128 | (n & 63));
  }
  return out;
}
function utf8Text(raw) {
  const out = [];
  for (let i = 0; i < raw.length;) {
    const a = raw[i++]; let n;
    if (a < 128) n = a;
    else if (a < 224) n = ((a & 31) << 6) | (raw[i++] & 63);
    else if (a < 240) n = ((a & 15) << 12) | ((raw[i++] & 63) << 6) | (raw[i++] & 63);
    else n = ((a & 7) << 18) | ((raw[i++] & 63) << 12) | ((raw[i++] & 63) << 6) | (raw[i++] & 63);
    out.push(String.fromCodePoint(n));
  }
  return out.join("");
}
function base64Bytes(text) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  const out = []; let acc = 0, bits = 0;
  for (const c of text) {
    if (c === "=") break;
    if (/\s/.test(c)) continue;
    const v = chars.indexOf(c); require88(v >= 0, "Invalid source base64");
    acc = (acc << 6) | v; bits += 6;
    if (bits >= 8) { bits -= 8; out.push((acc >>> bits) & 255); acc &= (1 << bits)-1; }
  }
  return out;
}
function sha1Bytes(raw) {
  const bytes = raw.slice(), bitLength = bytes.length * 8;
  bytes.push(128);
  while (bytes.length % 64 !== 56) bytes.push(0);
  const hi = Math.floor(bitLength / 4294967296), lo = bitLength >>> 0;
  for (let shift = 24; shift >= 0; shift -= 8) bytes.push((hi >>> shift) & 255);
  for (let shift = 24; shift >= 0; shift -= 8) bytes.push((lo >>> shift) & 255);
  let h0 = 0x67452301, h1 = 0xefcdab89, h2 = 0x98badcfe, h3 = 0x10325476, h4 = 0xc3d2e1f0;
  const rot = (v,n) => ((v << n) | (v >>> (32-n))) >>> 0;
  for (let offset = 0; offset < bytes.length; offset += 64) {
    const w = new Array(80);
    for (let i=0;i<16;i++) {
      const p=offset+4*i; w[i]=((bytes[p]<<24)|(bytes[p+1]<<16)|(bytes[p+2]<<8)|bytes[p+3])>>>0;
    }
    for (let i=16;i<80;i++) w[i]=rot(w[i-3]^w[i-8]^w[i-14]^w[i-16],1);
    let a=h0,b=h1,c=h2,d=h3,e=h4;
    for (let i=0;i<80;i++) {
      let f,k;
      if (i<20) { f=(b&c)|((~b)&d); k=0x5a827999; }
      else if (i<40) { f=b^c^d; k=0x6ed9eba1; }
      else if (i<60) { f=(b&c)|(b&d)|(c&d); k=0x8f1bbcdc; }
      else { f=b^c^d; k=0xca62c1d6; }
      const temp=(rot(a,5)+f+e+k+w[i])>>>0;
      e=d;d=c;c=rot(b,30);b=a;a=temp;
    }
    h0=(h0+a)>>>0;h1=(h1+b)>>>0;h2=(h2+c)>>>0;h3=(h3+d)>>>0;h4=(h4+e)>>>0;
  }
  return [h0,h1,h2,h3,h4].map(x=>x.toString(16).padStart(8,"0")).join("");
}
function gitBlobBytes(raw) { return sha1Bytes(utf8Bytes("blob "+raw.length+"\0").concat(raw)); }
function gitBlobText(text) { return gitBlobBytes(utf8Bytes(text)); }
class XorShift32 {
  constructor(seed) {
    require88(Number.isInteger(seed) && seed > 0 && seed < 4294967296, "Seed must be a nonzero uint32");
    this.state=seed>>>0;
  }
  next() { let x=this.state; x^=x<<13; x^=x>>>17; x^=x<<5; this.state=x>>>0; return this.state; }
  below(n) {
    require88(Number.isInteger(n) && n>0 && n<=4294967296,"Bad randbelow bound");
    const limit=Math.floor(4294967296/n)*n;
    for (;;) { const x=this.next(); if (x<limit) return x%n; }
  }
  shuffle(values) {
    for (let i=values.length-1;i>0;i--) { const j=this.below(i+1); [values[i],values[j]]=[values[j],values[i]]; }
  }
}
function counts(text) { const out={}; for (const c of text) out[c]=(out[c]||0)+1; return out; }
function sources(bundleText) {
  require88(gitBlobText(bundleText)===SOURCE_BUNDLE_BLOB,"Latin bundle differs from pinned base");
  const bundle=JSON.parse(bundleText),texts={},provenance=[];
  for (const entry of bundle.files) {
    const raw=base64Bytes(entry.base64);
    require88(gitBlobBytes(raw)===entry.sha && raw.length===entry.size,"Source blob or byte size mismatch");
    let lines=utf8Text(raw).split(/\r\n|[\n\v\f\r\u0085\u2028\u2029]/);
    if (lines[lines.length-1]==="") lines.pop();
    lines=lines.filter((line,i)=>i>0 && !(line.toUpperCase()===line && line.toLowerCase()!==line));
    const tokens=lines.join("\n").toLowerCase().match(/[a-z]+/g)||[];
    const text=tokens.join(" ");
    texts[entry.path]=text;
    provenance.push({path:entry.path,git_blob_sha1:entry.sha,normalized_letters:text.replace(/ /g,"").length});
  }
  require88(TEST_PATHS.every(path=>Object.hasOwn(texts,path)),"Missing reserved book");
  return {latinCommit:bundle.commit,texts,provenance};
}
function excludedIntervals(priorText) {
  require88(gitBlobText(priorText)===PRIOR_TRUTH_BLOB,"Prior truth differs from committed stage86 reveal");
  const excluded=Object.fromEntries(TEST_PATHS.map(path=>[path,[]]));
  for (const c of JSON.parse(priorText).cases) if (Object.hasOwn(excluded,c.source_path)) {
    if (!excluded[c.source_path].some(x=>x[0]===c.letter_start && x[1]===c.letter_end_exclusive))
      excluded[c.source_path].push([c.letter_start,c.letter_end_exclusive]);
  }
  for (const rows of Object.values(excluded)) rows.sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  return excluded;
}
function sampleWindow(text,excluded,rng) {
  const letters=text.replace(/ /g,""),candidates=[];
  for (let start=0;start<=letters.length-N;start++)
    if (excluded.every(([lo,hi])=>start+N<=lo||start>=hi)) candidates.push(start);
  require88(candidates.length>0,"No stage86-disjoint sample window");
  const start=candidates[rng.below(candidates.length)];
  return {start,plain:letters.slice(start,start+N)};
}
function applyKey(text,key) { return [...text].map(c=>key[ALPHABET.indexOf(c)]).join(""); }
function mono(plain,rng) {
  const symbols=[...ALPHABET];rng.shuffle(symbols);
  const encryption=symbols.join("");
  const decryption=[...ALPHABET].map(c=>ALPHABET[encryption.indexOf(c)]).join("");
  return {cipher:applyKey(plain,encryption),encryption,decryption};
}
function homo(plain,rng) {
  const count=counts(plain),chars=Object.keys(count).sort();
  require88(chars.length<26,"No spare homophonic symbols");
  const available=[...ALPHABET];rng.shuffle(available);
  const aliases={};for(const c of chars) aliases[c]=[available.pop()];
  const ranked=chars.slice().sort((a,b)=>count[b]-count[a]||(a<b?-1:a>b?1:0));
  available.forEach((symbol,i)=>aliases[ranked[i%ranked.length]].push(symbol));
  const reverse={};for(const [c,group] of Object.entries(aliases)) for(const symbol of group) reverse[symbol]=c;
  const key=[...ALPHABET].map(c=>reverse[c]).join("");
  const cipher=[...plain].map(c=>aliases[c][rng.below(aliases[c].length)]).join("");
  return {cipher,aliases,key};
}
function ceiling(cipher,key) {
  const count=counts(cipher),groups={};
  [...ALPHABET].forEach((symbol,i)=>(groups[key[i]]??=[]).push(count[symbol]||0));
  return Object.values(groups).reduce((sum,values)=>sum+Math.max(...values),0);
}
function prepareMappingFreedom(bundleText,priorText,seed) {
  const {latinCommit,texts,provenance}=sources(bundleText);
  const excluded=excludedIntervals(priorText),rng=new XorShift32(seed),cases=[];
  TEST_PATHS.forEach((path,index)=>{
    const {start,plain}=sampleWindow(texts[path],excluded[path],rng),pair="P"+(index+1);
    const common={pair_id:pair,variant:"no_spaces",source_path:path,letter_start:start,letter_end_exclusive:start+N,letters_total:N};
    const m=mono(plain,rng);
    cases.push({...common,role:"monoalphabetic_positive",ciphertext:m.cipher,plaintext:plain,letters_plaintext:plain,encryption_key_plain_to_cipher:m.encryption,decryption_key_cipher_to_plain:m.decryption});
    const h=homo(plain,rng);
    cases.push({...common,role:"homophonic_positive",ciphertext:h.cipher,plaintext:plain,letters_plaintext:plain,aliases_plain_to_cipher:h.aliases,decryption_key_cipher_to_plain:h.key});
    const shuffled=[...h.cipher];rng.shuffle(shuffled);const nullCipher=shuffled.join(""),nullPlain=applyKey(nullCipher,h.key);
    cases.push({...common,role:"frequency_matched_null",ciphertext:nullCipher,plaintext:nullPlain,letters_plaintext:nullPlain,aliases_plain_to_cipher:h.aliases,decryption_key_cipher_to_plain:h.key,accuracy_interpretation:"Generating-map recovery only; shuffled plaintext is not coherent Latin"});
  });
  rng.shuffle(cases);
  cases.forEach((c,i)=>{c.id="U"+String(i+1).padStart(2,"0");c.observed_cipher_symbols=[...new Set(c.ciphertext)].sort().join("");c.bijective_ceiling_correct_letters=ceiling(c.ciphertext,c.decryption_key_cipher_to_plain);});
  const homoByPair=Object.fromEntries(cases.filter(c=>c.role==="homophonic_positive").map(c=>[c.pair_id,c.id]));
  for (const c of cases) if(c.role==="frequency_matched_null") c.parent_homophonic_id=homoByPair[c.pair_id];
  const seedRecord={schema:"mapping-freedom-seed-v1",seed_u32:seed,rng_spec:RNG_SPEC,generator_version:VERSION};
  const truth={schema:"mapping-freedom-truth-v1",experiment:88,source_commit:SOURCE_COMMIT,latin_source_commit:latinCommit,prior_truth_git_blob_sha1:PRIOR_TRUTH_BLOB,source_bundle_git_blob_sha1:SOURCE_BUNDLE_BLOB,generator_version:VERSION,normalization:NORMALIZATION,cases};
  const cipherPublic={schema:"mapping-freedom-cases-v1",cases:cases.map(c=>({id:c.id,ciphertext:c.ciphertext}))};
  const manifest={schema:"mapping-freedom-public-v1",experiment:88,generator_version:VERSION,alphabet:ALPHABET,spacing:"none",case_count:9,letters_per_case:N,source_commit:SOURCE_COMMIT,latin_source_commit:latinCommit,source_bundle_git_blob_sha1:SOURCE_BUNDLE_BLOB,prior_truth_git_blob_sha1:PRIOR_TRUTH_BLOB,normalization:NORMALIZATION,prior_exclusion_rule:"Exclude every stage86 revealed [letter_start,letter_end_exclusive) interval of the same source book",lm_sha256:LM_SHA256,lm_source_path:"research_gpt6/results/known_cipher_recovery/model/lm_int32.bin",lm_policy:"Reuse stage86 Apicius LM bytes; no retraining or reweighting",rng_spec:RNG_SPEC,seed_bits:32,sources:provenance,truth_git_blob_sha1:gitBlobText(canonical(truth)),seed_git_blob_sha1:gitBlobText(canonical(seedRecord)),ciphertexts_git_blob_sha1:gitBlobText(canonical(cipherPublic))};
  return {public:{"ciphertexts.json":cipherPublic,"manifest.json":manifest},private:{"truth.json":truth,"seed.json":seedRecord}};
}
if (typeof module !== "undefined") module.exports={prepareMappingFreedom,canonical,gitBlobText,gitBlobBytes,XorShift32,sources,excludedIntervals};
