const editor=document.getElementById('editor'), output=document.getElementById('output'), gutter=document.getElementById('gutter');
const starter=`# Welcome to ASAANIDE
# Your first ASAAN program

var.name/str = "ASAAN"
var.times/int = 3

print: "Welcome to " + name

for var.i/int in 1..times:
    print: "Run " + str(i)

calc.calculate | 6 * (2 + 3)
print: calculate
`;
editor.value=starter;
function lines(){gutter.textContent=Array.from({length:Math.max(1,editor.value.split('\\n').length)},(_,i)=>i+1).join('\\n')}
lines();editor.addEventListener('input',lines);
editor.addEventListener('scroll',()=>gutter.scrollTop=editor.scrollTop);
editor.addEventListener('keyup',()=>{const p=editor.selectionStart, before=editor.value.slice(0,p).split('\\n');document.getElementById('cursor').textContent=`Ln ${before.length}, Col ${before.at(-1).length+1}`});
function tokenizeExpr(expr,env){
  expr=expr.replace(/\\bT\\b/g,'true').replace(/\\bF\\b/g,'false').replace(/&&/g,'&&').replace(/\\|\\|/g,'||');
  if(!/^[\\w\\s"'()+\\-*/%.,!<>=&|]+$/.test(expr)) throw Error('Expression contains unsupported characters');
  const names=Object.keys(env).sort((a,b)=>b.length-a.length);
  for(const n of names) expr=expr.replace(new RegExp('\\\\b'+n+'\\\\b','g'),`env[${JSON.stringify(n)}]`);
  expr=expr.replace(/\\btrue\\b/g,'true').replace(/\\bfalse\\b/g,'false');
  if(/\\b(?:import|constructor|window|document|globalThis|function|new)\\b/.test(expr)) throw Error('Blocked expression keyword');
  return Function('env','return ('+expr+')')(env);
}
function runAsaan(src){
 const env={}, out=[], rows=src.split('\\n');
 function block(start,indent){
  let i=start;
  while(i<rows.length){
   let raw=rows[i], t=raw.trim(); if(!t||t.startsWith('#')){i++;continue}
   let level=raw.match(/^ */)[0].length;if(level<indent)return i;if(level>indent)throw Error(`Unexpected indentation at line ${i+1}`);
   let m=t.match(/^var\\.(\\w+)\\/(\\w+)\\s*=\\s*(.+)$/);
   if(m){let v=tokenizeExpr(m[3],env), typ=m[2];if(typ==='int')v=Number.parseInt(v);if(typ==='str')v=String(v);if(typ==='bol')v=Boolean(v);if(typ==='list'&&!Array.isArray(v))throw Error(`Line ${i+1}: expected list`);if(typ==='int'&&!Number.isFinite(v))throw Error(`Line ${i+1}: expected integer`);env[m[1]]=v;i++;continue}
   if(t.startsWith('print:')){out.push(String(tokenizeExpr(t.slice(6).trim(),env)));i++;continue}
   if(t.startsWith('calc.calculate |')){env.calculate=tokenizeExpr(t.split('|').slice(1).join('|').trim(),env);i++;continue}
   if(t.startsWith('if ')&&t.endsWith(':')){let end=findEnd(i+1,indent);if(tokenizeExpr(t.slice(3,-1),env)){block(i+1,indent+4);i=end;if(i<rows.length&&rows[i].trim()==='else:')i=findEnd(i+1,indent)}else{i=end;if(i<rows.length&&rows[i].trim()==='else:')i=block(i+1,indent+4)}continue}
   if(t.startsWith('for ')&&t.endsWith(':')){let f=t.match(/^for\\s+var\\.(\\w+)\\/\\w+\\s+in\\s+(-?\\d+)\\.\\.(-?\\d+):$/);if(!f)throw Error(`Line ${i+1}: expected for var.i/int in 1..5:`);let end=findEnd(i+1,indent);for(let n=+f[2];n<=+f[3];n++){env[f[1]]=n;block(i+1,indent+4)}i=end;continue}
   throw Error(`Line ${i+1}: unsupported statement: ${t}`);
  }return i;
 }
 function findEnd(start,base){let i=start;while(i<rows.length){let r=rows[i];if(r.trim()&&r.match(/^ */)[0].length<=base)break;i++}return i}
 block(0,0);return out.join('\\n');
}
document.getElementById('runBtn').onclick=()=>{try{output.textContent='> Running main.asa\\n\\n'+runAsaan(editor.value)+'\\n\\n[Process exited successfully]'}catch(e){output.textContent='> Runtime error\\n\\n'+e.message+'\\n\\nTip: check the line number and variable types.'}};
document.getElementById('compileBtn').onclick=()=>{output.textContent='ASAAN compiler — preview mode\\n\\nThis browser build runs ASAAN through its interpreter.\\nFor Python transpilation, use: asaan compile examples/hello.asa -o build/hello.py\\n\\nNo native executable was produced.'};
document.getElementById('clearBtn').onclick=()=>output.textContent='';
document.getElementById('newFile').onclick=()=>{editor.value='# New ASAAN file\\n\\n';lines();output.textContent='Created a new unsaved editor buffer.'};
document.querySelectorAll('.tool').forEach(b=>b.onclick=()=>{editor.setRangeText('\\n'+b.dataset.insert,editor.selectionStart,editor.selectionEnd,'end');lines();editor.focus()});
document.getElementById('themeBtn').onclick=()=>document.body.classList.toggle('light');
