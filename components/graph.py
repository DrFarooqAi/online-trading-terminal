import json
import streamlit.components.v1 as components
from data.graph_data import get_graph_data, get_convergence_score

_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{background:#08080f;font-family:'Courier New',monospace;overflow:hidden}
  #wrap{position:relative;width:100vw;height:100vh}
  svg{position:absolute;top:0;left:0}
  .nl{font-family:'Courier New',monospace;font-size:9px;text-anchor:middle;pointer-events:none}
  .es{font-family:'Courier New',monospace;font-size:8px;fill:#2a2a3e;text-anchor:middle;pointer-events:none}
</style>
</head>
<body>
<div id="wrap">

  <div style="position:absolute;top:10px;left:12px;color:#1c1c38;font-size:9px;letter-spacing:2px;z-index:10;">
    ■ MIROFISH &middot; RELATIONSHIP GRAPH &middot; PHASE 3
  </div>

  <div id="panel" style="
    position:absolute;top:10px;right:12px;
    background:#0b0b16;border:1px solid #1a1a3e;border-radius:4px;
    padding:10px 14px;min-width:168px;z-index:10;
  ">
    <div style="color:#00aaff;font-size:10px;letter-spacing:1px;margin-bottom:8px;">&#9632; CONVERGENCE</div>
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:#444;font-size:9px;">BULL PATHS</span>
      <span style="color:#00ff88;font-size:9px;font-weight:bold;">__BULL_COUNT__</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:#444;font-size:9px;">BEAR PATHS</span>
      <span style="color:#ff3c3c;font-size:9px;font-weight:bold;">__BEAR_COUNT__</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
      <span style="color:#444;font-size:9px;">BULL STR</span>
      <span style="color:#00ff88;font-size:9px;">__BULL_STR__</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:9px;">
      <span style="color:#444;font-size:9px;">BEAR STR</span>
      <span style="color:#ff3c3c;font-size:9px;">__BEAR_STR__</span>
    </div>
    <div style="border-top:1px solid #1a1a2e;padding-top:8px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="color:#444;font-size:9px;">SCORE</span>
        <span style="color:__SCORE_COLOR__;font-size:20px;font-weight:bold;">__SCORE_SIGN____SCORE__</span>
      </div>
      <div style="
        text-align:center;padding:4px;border-radius:3px;
        font-size:10px;font-weight:bold;letter-spacing:1px;
        background:__DIR_BG__;color:__DIR_COLOR__;border:1px solid __DIR_BD__;
      ">__DIR_ICON__ __DIRECTION__</div>
    </div>
  </div>

  <div id="legend" style="
    position:absolute;bottom:10px;left:12px;
    background:#0b0b16;border:1px solid #1a1a3e;border-radius:4px;
    padding:7px 12px;z-index:10;
  ">
    <div style="color:#222;font-size:8px;margin-bottom:5px;letter-spacing:1px;">NODE TYPES</div>
    <div style="display:flex;gap:10px;margin-bottom:5px;">
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:7px;height:7px;border-radius:50%;background:#00aaff;"></div><span style="color:#333;font-size:8px;">PRICE</span></div>
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:7px;height:7px;border-radius:50%;background:#ff8c00;"></div><span style="color:#333;font-size:8px;">SUPPLY</span></div>
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:7px;height:7px;border-radius:50%;background:#9b59b6;"></div><span style="color:#333;font-size:8px;">DEMAND</span></div>
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:7px;height:7px;border-radius:50%;background:#ffd700;"></div><span style="color:#333;font-size:8px;">MACRO</span></div>
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:7px;height:7px;border-radius:50%;background:#e74c3c;"></div><span style="color:#333;font-size:8px;">RISK</span></div>
    </div>
    <div style="display:flex;gap:14px;">
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:14px;height:2px;background:#00ff88;"></div><span style="color:#333;font-size:8px;">BULL</span></div>
      <div style="display:flex;align-items:center;gap:4px;"><div style="width:14px;height:2px;background:#ff3c3c;"></div><span style="color:#333;font-size:8px;">BEAR</span></div>
    </div>
  </div>

  <svg id="g"></svg>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const nodes = __NODES__;
const links = __LINKS__;
const W = window.innerWidth, H = window.innerHeight;

const TC = {center:"#00aaff",supply:"#ff8c00",demand:"#9b59b6",macro:"#ffd700",risk:"#e74c3c"};

const svg = d3.select("#g").attr("width",W).attr("height",H);
const defs = svg.append("defs");

[["glow-blue","#00aaff"],["glow-green","#00ff88"],["glow-red","#ff3c3c"]].forEach(([id,c])=>{
  const f=defs.append("filter").attr("id",id).attr("x","-60%").attr("y","-60%").attr("width","220%").attr("height","220%");
  f.append("feGaussianBlur").attr("in","SourceGraphic").attr("stdDeviation","4").attr("result","b");
  const m=f.append("feMerge");
  m.append("feMergeNode").attr("in","b");
  m.append("feMergeNode").attr("in","SourceGraphic");
});

["bull","bear"].forEach(d=>{
  const c=d==="bull"?"#00ff88":"#ff3c3c";
  defs.append("marker").attr("id","arr-"+d).attr("viewBox","0 -5 10 10")
    .attr("refX",22).attr("refY",0).attr("markerWidth",5).attr("markerHeight",5)
    .attr("orient","auto")
    .append("path").attr("d","M0,-5L10,0L0,5").attr("fill",c).attr("opacity",0.6);
});

const grid=svg.append("g");
for(let x=0;x<W;x+=50) grid.append("line").attr("x1",x).attr("y1",0).attr("x2",x).attr("y2",H).attr("stroke","#0c0c18").attr("stroke-width",0.5);
for(let y=0;y<H;y+=50) grid.append("line").attr("x1",0).attr("y1",y).attr("x2",W).attr("y2",y).attr("stroke","#0c0c18").attr("stroke-width",0.5);

const sim = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d=>d.id).distance(d=>d.target.type==="center"||d.source.type==="center"?155:105).strength(0.4))
  .force("charge", d3.forceManyBody().strength(-520))
  .force("center", d3.forceCenter(W/2, H/2))
  .force("collision", d3.forceCollide(52));

const linkEl = svg.append("g").selectAll("line").data(links).join("line")
  .attr("stroke", d=>d.direction==="bull"?"#00ff8840":"#ff3c3c40")
  .attr("stroke-width", d=>Math.max(1,d.strength/38))
  .attr("marker-end", d=>"url(#arr-"+d.direction+")");

const edgeLbl = svg.append("g").selectAll("text").data(links).join("text")
  .attr("class","es").text(d=>d.strength);

const nodeEl = svg.append("g").selectAll("g").data(nodes).join("g")
  .call(d3.drag()
    .on("start",(e,d)=>{if(!e.active)sim.alphaTarget(0.3).restart();d.fx=d.x;d.fy=d.y;})
    .on("drag", (e,d)=>{d.fx=e.x;d.fy=e.y;})
    .on("end",  (e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));

nodeEl.filter(d=>d.type==="center").append("circle").attr("class","pulse-ring")
  .attr("r",34).attr("fill","none").attr("stroke","#00aaff").attr("stroke-width",1.5).attr("opacity",0.12);

nodeEl.append("circle")
  .attr("r", d=>d.type==="center"?22:15)
  .attr("fill", d=>TC[d.type]+"18")
  .attr("stroke", d=>TC[d.type])
  .attr("stroke-width", d=>d.type==="center"?2:1.5)
  .attr("filter", d=>d.type==="center"?"url(#glow-blue)":null);

nodeEl.filter(d=>d.type==="center").append("text")
  .attr("class","nl").attr("fill","#00aaff").attr("font-size","10px").attr("font-weight","bold")
  .attr("dominant-baseline","central").text("WTI");

nodeEl.append("text").attr("class","nl")
  .attr("y", d=>d.type==="center"?36:27)
  .attr("fill", d=>TC[d.type])
  .attr("font-size", d=>d.type==="center"?"10px":"9px")
  .attr("font-weight", d=>d.type==="center"?"bold":"normal")
  .text(d=>d.label);

nodeEl.filter(d=>d.type!=="center").append("text").attr("class","nl")
  .attr("y",37).attr("fill","#333").attr("font-size","8px")
  .text(d=>d.weight+"%");

sim.on("tick",()=>{
  linkEl.attr("x1",d=>d.source.x).attr("y1",d=>d.source.y).attr("x2",d=>d.target.x).attr("y2",d=>d.target.y);
  edgeLbl.attr("x",d=>(d.source.x+d.target.x)/2).attr("y",d=>(d.source.y+d.target.y)/2-5);
  nodeEl.attr("transform",d=>"translate("+d.x+","+d.y+")");
});

(function pulse(){
  nodeEl.filter(d=>d.type==="center").select(".pulse-ring")
    .transition().duration(1300).ease(d3.easeSinInOut)
    .attr("r",42).attr("opacity",0.04).attr("stroke-width",0.5)
    .transition().duration(1300).ease(d3.easeSinInOut)
    .attr("r",30).attr("opacity",0.18).attr("stroke-width",2)
    .on("end",pulse);
})();

function spawnParticle(lk){
  const c=lk.direction==="bull"?"#00ff88":"#ff3c3c";
  const glow=lk.direction==="bull"?"glow-green":"glow-red";
  const sx=lk.source.x,sy=lk.source.y,tx=lk.target.x,ty=lk.target.y;
  svg.append("circle").attr("r",2.5).attr("fill",c).attr("filter","url(#"+glow+")").attr("opacity",0.9)
    .transition().duration(900+Math.random()*600).ease(d3.easeLinear)
    .tween("mv",function(){
      const el=d3.select(this);
      return t=>el.attr("cx",sx+(tx-sx)*t).attr("cy",sy+(ty-sy)*t);
    })
    .on("end",function(){d3.select(this).remove();});
}

let started=false;
function startParticles(){
  if(started)return; started=true;
  setInterval(()=>links.forEach(lk=>{if(Math.random()<0.55)spawnParticle(lk);}),550);
}
sim.on("end",startParticles);
setTimeout(startParticles,3500);
</script>
</body>
</html>"""


def render_graph_panel():
    data  = get_graph_data()
    conv  = get_convergence_score(data["links"])
    score = conv["score"]

    if conv["direction"] == "BULLISH":
        score_color, dir_bg, dir_color, dir_bd, dir_icon = "#00ff88","#0a2e1a","#00ff88","#00ff8833","&#9650;"
    elif conv["direction"] == "BEARISH":
        score_color, dir_bg, dir_color, dir_bd, dir_icon = "#ff3c3c","#2e0a0a","#ff3c3c","#ff3c3c33","&#9660;"
    else:
        score_color, dir_bg, dir_color, dir_bd, dir_icon = "#ffd700","#1a1800","#ffd700","#ffd70033","&#9670;"

    html = (
        _HTML
        .replace("__NODES__",      json.dumps(data["nodes"]))
        .replace("__LINKS__",      json.dumps(data["links"]))
        .replace("__BULL_COUNT__", str(conv["bull_count"]))
        .replace("__BEAR_COUNT__", str(conv["bear_count"]))
        .replace("__BULL_STR__",   str(conv["bull_str"]))
        .replace("__BEAR_STR__",   str(conv["bear_str"]))
        .replace("__SCORE_COLOR__",score_color)
        .replace("__SCORE_SIGN__", "+" if score >= 0 else "")
        .replace("__SCORE__",      str(score))
        .replace("__DIR_BG__",     dir_bg)
        .replace("__DIR_COLOR__",  dir_color)
        .replace("__DIR_BD__",     dir_bd)
        .replace("__DIR_ICON__",   dir_icon)
        .replace("__DIRECTION__",  conv["direction"])
    )
    components.html(html, height=500, scrolling=False)
