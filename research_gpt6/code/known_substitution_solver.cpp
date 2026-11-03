// Integer-scored substitution search. No plaintext/truth or word dictionary input.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>
using namespace std;
struct RNG { uint64_t state; uint32_t next(){state^=state>>12;state^=state<<25;state^=state>>27;return uint32_t((state*2685821657736338717ULL)>>32);} };
vector<uint64_t> readle(const string& path,int width){ifstream f(path,ios::binary);if(!f)throw runtime_error("missing file");vector<uint64_t> out;while(true){uint64_t v=0;for(int i=0;i<width;i++){int c=f.get();if(c==EOF){if(i)throw runtime_error("short binary");return out;}v|=uint64_t(uint8_t(c))<<(8*i);}out.push_back(v);}}
struct Gram{array<int,4> a;int count;};
int main(int argc,char**argv){try{
 if(argc!=10)throw runtime_error("lm accept temps rank ciphertext seed restarts steps polish");
 auto raw=readle(argv[1],4);vector<int32_t> lm;for(auto x:raw)lm.push_back(int32_t(uint32_t(x)));if(lm.size()!=26*26*26*26)throw runtime_error("LM size");
 auto accept=readle(argv[2],8);auto temperatures=readle(argv[3],4);if(accept.size()!=8193||temperatures.size()!=100)throw runtime_error("table size");
 array<int,26> plainrank{};ifstream ranks(argv[4]);for(int&i:plainrank)ranks>>i;
 ifstream textfile(argv[5]);string text;getline(textfile,text);if(text.size()<4)throw runtime_error("short ciphertext");
 vector<int> stream;array<int,26> freq{};for(char c:text){if(c<'a'||c>'z')throw runtime_error("cipher alphabet");stream.push_back(c-'a');freq[c-'a']++;}
 map<array<int,4>,int> grouped;for(size_t i=0;i+3<stream.size();i++)grouped[{stream[i],stream[i+1],stream[i+2],stream[i+3]}]++;
 vector<Gram> grams;for(auto&p:grouped)grams.push_back({p.first,p.second});
 array<array<vector<int>,26>,26> affected;for(int a=0;a<26;a++)for(int b=a+1;b<26;b++)for(size_t i=0;i<grams.size();i++){bool used=false;for(int c:grams[i].a)if(c==a||c==b)used=true;if(used)affected[a][b].push_back(i);} 
 auto val=[&](const array<int,26>&k,int i){auto a=grams[i].a;return lm[((k[a[0]]*26+k[a[1]])*26+k[a[2]])*26+k[a[3]]];};
 array<int,26> cipherorder{};iota(cipherorder.begin(),cipherorder.end(),0);sort(cipherorder.begin(),cipherorder.end(),[&](int a,int b){return freq[a]!=freq[b]?freq[a]>freq[b]:a<b;});
 uint64_t seed=stoull(argv[6]);int restarts=stoi(argv[7]),steps=stoi(argv[8]),polish=stoi(argv[9]);
 int64_t global=INT64_MIN;array<int,26> globalkey{};uint64_t proposals=0,accepted=0,polishChecks=0;vector<int64_t> restartScores;
 for(int restart=0;restart<restarts;restart++){
  RNG rng{seed^(0x9e3779b97f4a7c15ULL*uint64_t(restart+1))};if(!rng.state)rng.state=1;
  array<int,26> key{};for(int i=0;i<26;i++)key[cipherorder[i]]=plainrank[i];
  if(restart)for(int j=0;j<12;j++){int a=rng.next()%26,b=rng.next()%25;if(b>=a)b++;swap(key[a],key[b]);}
  vector<int32_t> values(grams.size());int64_t current=0;for(size_t i=0;i<grams.size();i++){values[i]=val(key,i);current+=int64_t(grams[i].count)*values[i];}
  int64_t best=current;auto bestkey=key;vector<int32_t> proposed;proposed.reserve(grams.size());
  auto delta=[&](int a,int b){if(a>b)swap(a,b);swap(key[a],key[b]);int64_t d=0;proposed.clear();for(int i:affected[a][b]){int32_t v=val(key,i);proposed.push_back(v);d+=int64_t(grams[i].count)*(int64_t(v)-values[i]);}swap(key[a],key[b]);return d;};
  auto apply=[&](int a,int b){if(a>b)swap(a,b);swap(key[a],key[b]);for(int i:affected[a][b])values[i]=val(key,i);};
  for(int step=0;step<steps;step++){
   int a=rng.next()%26,b=rng.next()%25;if(b>=a)b++;int64_t d=delta(a,b);bool take=d>=0;
   if(d<0){uint64_t bucket=min<uint64_t>(8192,uint64_t(-d)*256/temperatures[size_t(step)*100/steps]);take=uint64_t(rng.next())<accept[bucket];}
   proposals++;if(take){apply(a,b);current+=d;accepted++;if(current>best||(current==best&&key<bestkey)){best=current;bestkey=key;}}
  }
  key=bestkey;current=best;for(size_t i=0;i<grams.size();i++)values[i]=val(key,i);
  for(int pass=0;pass<polish;pass++){
   int ba=-1,bb=-1;int64_t bd=0;
   for(int a=0;a<26;a++)for(int b=a+1;b<26;b++){int64_t d=delta(a,b);polishChecks++;if(d>bd){bd=d;ba=a;bb=b;}}
   if(ba<0)break;apply(ba,bb);current+=bd;
  }
  int64_t check=0;for(size_t i=0;i<grams.size();i++)check+=int64_t(grams[i].count)*val(key,i);if(check!=current)throw runtime_error("delta mismatch");
  restartScores.push_back(current);if(current>global||(current==global&&key<globalkey)){global=current;globalkey=key;}
 }
 string keytext,decoded;for(int c:globalkey)keytext+=char('a'+c);for(int c:stream)decoded+=char('a'+globalkey[c]);
 cout<<"{\"key\":\""<<keytext<<"\",\"letters_plaintext\":\""<<decoded<<"\",\"score\":"<<global<<",\"annealing_proposals\":"<<proposals<<",\"accepted\":"<<accepted<<",\"polish_pair_checks\":"<<polishChecks<<",\"restart_scores\":[";for(size_t i=0;i<restartScores.size();i++){if(i)cout<<",";cout<<restartScores[i];}cout<<"]}\n";
 return 0;
 }catch(const exception&e){cerr<<e.what()<<"\n";return 1;}}
