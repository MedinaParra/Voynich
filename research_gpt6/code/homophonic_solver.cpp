// Deterministic many-to-one substitution search; no plaintext/truth inputs.
// Same integer four-character LM and acceptance tables as the monoalphabetic baseline.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
using Key=array<int,26>;
struct RNG {
 uint64_t state;
 uint32_t next(){state^=state>>12;state^=state<<25;state^=state>>27;return uint32_t((state*2685821657736338717ULL)>>32);}
};
vector<uint64_t> readle(const string& path,int width){
 ifstream f(path,ios::binary);if(!f)throw runtime_error("missing binary file");
 vector<uint64_t> out;
 while(true){
  uint64_t v=0;
  for(int i=0;i<width;i++){
   int c=f.get();
   if(c==EOF){if(i)throw runtime_error("short binary word");return out;}
   v|=uint64_t(uint8_t(c))<<(8*i);
  }
  out.push_back(v);
 }
}
struct Gram{array<int,4> a;int count;};
struct Objective {
 const vector<int32_t>&lm;
 vector<Gram> grams;
 array<vector<int>,26> unary;
 array<array<vector<int>,26>,26> pairs;
 Key key{};
 vector<int32_t> values;
 int64_t total=0;
 Objective(const vector<int32_t>&table,const vector<int>&stream):lm(table){
  map<array<int,4>,int> grouped;
  for(size_t i=0;i+3<stream.size();i++)grouped[{stream[i],stream[i+1],stream[i+2],stream[i+3]}]++;
  for(auto&p:grouped)grams.push_back({p.first,p.second});
  for(size_t i=0;i<grams.size();i++){
   array<bool,26> seen{};
   for(int c:grams[i].a)seen[c]=true;
   for(int a=0;a<26;a++)if(seen[a])unary[a].push_back(int(i));
   for(int a=0;a<26;a++)for(int b=a+1;b<26;b++)if(seen[a]||seen[b])pairs[a][b].push_back(int(i));
  }
  values.resize(grams.size());
 }
 int32_t val(const Key&k,int i)const{
  auto a=grams[i].a;
  return lm[((k[a[0]]*26+k[a[1]])*26+k[a[2]])*26+k[a[3]]];
 }
 int64_t fullscore(const Key&k)const{
  int64_t sum=0;
  for(size_t i=0;i<grams.size();i++)sum+=int64_t(grams[i].count)*val(k,int(i));
  return sum;
 }
 void initialise(const Key&k){
  key=k;total=0;
  for(size_t i=0;i<grams.size();i++){values[i]=val(key,int(i));total+=int64_t(grams[i].count)*values[i];}
 }
 int64_t changed_delta(const vector<int>&affected)const{
  int64_t d=0;
  for(int i:affected)d+=int64_t(grams[i].count)*(int64_t(val(key,i))-values[i]);
  return d;
 }
 int64_t refresh(const vector<int>&affected){
  int64_t d=0;
  for(int i:affected){int32_t v=val(key,i);d+=int64_t(grams[i].count)*(int64_t(v)-values[i]);values[i]=v;}
  total+=d;return d;
 }
 int64_t delta_assign(int c,int p){
  int old=key[c];key[c]=p;int64_t d=changed_delta(unary[c]);key[c]=old;return d;
 }
 int64_t delta_swap(int a,int b){
  if(a>b)swap(a,b);
  swap(key[a],key[b]);int64_t d=changed_delta(pairs[a][b]);swap(key[a],key[b]);return d;
 }
 int64_t apply_assign(int c,int p){key[c]=p;return refresh(unary[c]);}
 int64_t apply_swap(int a,int b){if(a>b)swap(a,b);swap(key[a],key[b]);return refresh(pairs[a][b]);}
};
void require(bool ok,const string&why){if(!ok)throw runtime_error(why);}
int selftest(){
 vector<int32_t> lm(26*26*26*26);
 for(size_t i=0;i<lm.size();i++)lm[i]=-int32_t((uint32_t(i)*2654435761U+12345U)%30001U);
 string text="abracadabraabcdefghijklmnopqrstuvwxyzzyxwvutsrqponmlkjihgfedcbaabracadabra";
 vector<int> stream;for(char c:text)stream.push_back(c-'a');
 Objective o(lm,stream);Key key{};for(int i=0;i<26;i++)key[i]=(i*7)%11;o.initialise(key);
 int checks=0;
 require(o.total==o.fullscore(key),"initial fullscore mismatch");checks++;
 for(int c=0;c<26;c++)for(int p=0;p<26;p++)if(p!=key[c]){
  Key k=key;k[c]=p;
  require(o.delta_assign(c,p)==o.fullscore(k)-o.fullscore(key),"assignment delta mismatch");checks++;
  require(o.key==key&&o.total==o.fullscore(key),"assignment probe mutated state");checks++;
 }
 for(int a=0;a<26;a++)for(int b=a+1;b<26;b++){
  Key k=key;swap(k[a],k[b]);
  require(o.delta_swap(a,b)==o.fullscore(k)-o.fullscore(key),"swap delta mismatch");checks++;
  require(o.key==key&&o.total==o.fullscore(key),"swap probe mutated state");checks++;
 }
 RNG rng{123456789U};
 for(int i=0;i<128;i++){
  int a=rng.next()%26,b=rng.next()%26;int64_t before=o.fullscore(o.key);
  int64_t expected=(i&1)?o.delta_assign(a,b):o.delta_swap(a,b);
  int64_t actual=(i&1)?o.apply_assign(a,b):o.apply_swap(a,b);
  require(expected==actual&&o.total==o.fullscore(o.key)&&o.total-before==actual,"sequential state mismatch");checks++;
 }
 cout<<"{\"status\":\"PASS\",\"checks\":"<<checks<<",\"scope\":\"Synthetic integer objective deltas, not cipher recovery or Voynich validation\"}\n";
 return 0;
}
int main(int argc,char**argv){try{
 if(argc==2&&string(argv[1])=="--self-test")return selftest();
 require(argc==10,"lm accept temps rank ciphertext seed restarts steps polish");
 auto raw=readle(argv[1],4);vector<int32_t> lm;for(auto x:raw)lm.push_back(int32_t(uint32_t(x)));
 require(lm.size()==26*26*26*26,"LM size");
 auto accept=readle(argv[2],8),temperatures=readle(argv[3],4);
 require(accept.size()==8193&&temperatures.size()==100,"acceptance/temperature table size");
 for(auto t:temperatures)require(t>0,"zero temperature");
 for(auto p:accept)require(p<=4294967296ULL,"acceptance threshold range");
 Key plainrank{};ifstream ranks(argv[4]);require(bool(ranks),"missing rank");
 for(int&i:plainrank)require(bool(ranks>>i),"rank length");
 Key sorted=plainrank;sort(sorted.begin(),sorted.end());for(int i=0;i<26;i++)require(sorted[i]==i,"rank must be permutation");
 ifstream textfile(argv[5]);require(bool(textfile),"missing ciphertext");string text;getline(textfile,text);
 require(text.size()==2000,"expected 2000 ciphertext letters");
 vector<int> stream;array<int,26> freq{};
 for(char c:text){require(c>='a'&&c<='z',"cipher alphabet");stream.push_back(c-'a');freq[c-'a']++;}
 array<int,26> order{};iota(order.begin(),order.end(),0);
 sort(order.begin(),order.end(),[&](int a,int b){return freq[a]!=freq[b]?freq[a]>freq[b]:a<b;});
 uint64_t seed=stoull(argv[6]);int restarts=stoi(argv[7]),steps=stoi(argv[8]),polish=stoi(argv[9]);
 require(restarts>0&&steps>0&&polish>=0,"invalid search budget");
 Objective o(lm,stream);int64_t global=numeric_limits<int64_t>::min();Key globalkey{};
 uint64_t proposals=0,assignProposals=0,swapProposals=0,noops=0,accepted=0,polishChecks=0,polishUpdates=0;
 vector<int64_t> restartScores;
 for(int restart=0;restart<restarts;restart++){
  RNG rng{seed^(0x9e3779b97f4a7c15ULL*uint64_t(restart+1))};if(!rng.state)rng.state=1;
  Key initial{};for(int i=0;i<26;i++)initial[order[i]]=plainrank[i];
  if(restart)for(int j=0;j<12;j++){
   int a=rng.next()%26,b=rng.next()%25;if(b>=a)b++;
   if(j&1)initial[a]=rng.next()%26;else swap(initial[a],initial[b]);
  }
  o.initialise(initial);int64_t best=o.total;Key bestkey=o.key;
  for(int step=0;step<steps;step++){
   bool assignment=(rng.next()&1U)!=0;int a=rng.next()%26,b;
   if(assignment){b=rng.next()%25;if(b>=o.key[a])b++;assignProposals++;}
   else{b=rng.next()%25;if(b>=a)b++;swapProposals++;if(o.key[a]==o.key[b])noops++;}
   int64_t d=assignment?o.delta_assign(a,b):o.delta_swap(a,b);
   bool take=d>=0;
   if(d<0){uint64_t bucket=min<uint64_t>(8192,uint64_t(-d)*256/temperatures[size_t(step)*100/steps]);take=uint64_t(rng.next())<accept[bucket];}
   proposals++;
   if(take){
    int64_t applied=assignment?o.apply_assign(a,b):o.apply_swap(a,b);require(applied==d,"applied delta mismatch");accepted++;
    if(o.total>best||(o.total==best&&o.key<bestkey)){best=o.total;bestkey=o.key;}
   }
  }
  o.initialise(bestkey);
  for(int pass=0;pass<polish;pass++){
   int ba=-1,bb=-1,kind=0;int64_t bd=0;
   // Fixed tie priority: earliest assignment, then earliest swap; strict improvements only.
   for(int a=0;a<26;a++)for(int p=0;p<26;p++)if(p!=o.key[a]){
    int64_t d=o.delta_assign(a,p);polishChecks++;if(d>bd){bd=d;ba=a;bb=p;kind=1;}
   }
   for(int a=0;a<26;a++)for(int b=a+1;b<26;b++){
    int64_t d=o.delta_swap(a,b);polishChecks++;if(d>bd){bd=d;ba=a;bb=b;kind=2;}
   }
   if(!kind)break;
   int64_t applied=kind==1?o.apply_assign(ba,bb):o.apply_swap(ba,bb);require(applied==bd,"polish delta mismatch");polishUpdates++;
  }
  require(o.fullscore(o.key)==o.total,"restart final fullscore mismatch");
  restartScores.push_back(o.total);
  if(o.total>global||(o.total==global&&o.key<globalkey)){global=o.total;globalkey=o.key;}
 }
 string keytext,decoded;for(int c:globalkey)keytext+=char('a'+c);for(int c:stream)decoded+=char('a'+globalkey[c]);
 cout<<"{\"key\":\""<<keytext<<"\",\"letters_plaintext\":\""<<decoded<<"\",\"score\":"<<global
     <<",\"annealing_proposals\":"<<proposals<<",\"assignment_proposals\":"<<assignProposals
     <<",\"swap_proposals\":"<<swapProposals<<",\"noop_swap_proposals\":"<<noops
     <<",\"accepted\":"<<accepted<<",\"polish_pair_checks\":"<<polishChecks
     <<",\"polish_updates\":"<<polishUpdates<<",\"restart_scores\":[";
 for(size_t i=0;i<restartScores.size();i++){if(i)cout<<",";cout<<restartScores[i];}
 cout<<"]}\n";return 0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}
}
